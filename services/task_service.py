"""Atomic task/feedback persistence. Replanning happens only after feedback commits."""
from contextlib import nullcontext
import sqlite3
from core.errors import BusinessError
from core.schemas import Capability, Evidence, Event, EventType, TaskStatus
from core.planner import validate_task
from core.gap_engine import NEXT_GAP_TYPE, validate_level
from core.capability_progression import progress_capability
from services.common import storage_errors
from storage.repository import encode, normalize_task, utc_now

FEEDBACK_EVENTS = {"completed": EventType.TASK_COMPLETED,
                   "partial": EventType.TASK_PARTIAL, "not_completed": EventType.TASK_NOT_COMPLETED}


class TaskService:
    def __init__(self, repository, *, planning_service=None):
        self.repo = repository
        self._planning = planning_service
        if planning_service is not None and not planning_service.enable_tasks:
            raise ValueError("Task feedback requires a task-enabled PlanningService")

    @property
    def planning(self):
        if self._planning is None:
            from services.planning_service import PlanningService
            self._planning = PlanningService(self.repo, enable_tasks=True)
        return self._planning

    @storage_errors
    def create_task(self, task, *, planning_basis=None):
        # Keep the public creation boundary validated even when called without the Planner.
        if task.status != TaskStatus.PENDING:
            raise BusinessError("invalid_task", "新任务必须为 pending。")
        cleaned = validate_task({"capability": task.capability, "task": task.task_text,
            "reason": task.reason, "estimated_time": task.estimated_time,
            "acceptance_criteria": task.acceptance_criteria_json}, task.capability,
            (planning_basis or {}).get("task_budget_minutes", 240))
        if planning_basis and "current_level" in planning_basis:
            level = validate_level(planning_basis["current_level"])
            if level not in NEXT_GAP_TYPE or planning_basis.get("next_gap_type") != NEXT_GAP_TYPE[level]:
                raise BusinessError("invalid_stage", "任务阶段与当前等级不匹配。")
            cleaned.gap_type, cleaned.target_level = NEXT_GAP_TYPE[level], level + 1
        else:
            cleaned.gap_type, cleaned.target_level = task.gap_type, task.target_level
        scope = nullcontext() if self.repo.connection.in_transaction else self.repo.transaction()
        try:
            with scope:
                if any(t["task_key"] == normalize_task(cleaned.task_text) for t in self.repo.pending_tasks()):
                    raise BusinessError("duplicate_pending_task", "已有相同 pending 任务。")
                task_id = self.repo.create_task(cleaned)
                self.repo.append_event(Event(EventType.TASK_CREATED, "task", str(task_id), {
                    "task_id": task_id, "capability": cleaned.capability, "task_text": cleaned.task_text,
                    "planning_basis": planning_basis or {}, "gap_type": cleaned.gap_type,
                    "target_level": cleaned.target_level}))
                return self.repo.get_task(task_id)
        except sqlite3.IntegrityError:
            raise BusinessError("task_conflict", "任务写入冲突，未创建重复任务。") from None

    @storage_errors
    def submit_task_feedback(self, task_id, status, feedback=None):
        if type(task_id) is not int or task_id < 1:
            raise BusinessError("invalid_task_id", "task_id 必须为正整数。")
        if not isinstance(status, str) or status not in FEEDBACK_EVENTS:
            raise BusinessError("invalid_feedback_status", "请选择 completed / partial / not_completed。")
        if feedback is not None and not isinstance(feedback, str):
            raise BusinessError("invalid_feedback", "Feedback 必须为文本。")
        if status != "completed" and not (feedback or "").strip():
            raise BusinessError("feedback_required", "partial / not_completed 必须填写原因。")
        if self.repo.connection.in_transaction:
            raise BusinessError("transaction_open", "请在独立事务边界提交反馈。")
        with self.repo.transaction():
            task = self.repo.get_task(task_id)
            if task is None:
                raise BusinessError("task_missing", "任务不存在。")
            if task["status"] != "pending":
                raise BusinessError("task_closed", "任务已反馈或 superseded，不能重复提交。")
            payload = {"task_id": task_id, "capability": task["capability"],
                "task_text": task["task_text"], "previous_status": task["status"], "new_status": status,
                "feedback": feedback or "", "reported_at": utc_now(), "source": "user_report"}
            self.repo.update_task_status(task_id, status)
            event_id = self.repo.append_event(Event(FEEDBACK_EVENTS[status], "task", str(task_id), payload))
            capability = self.repo.get_capability(task["capability"])
            if capability is None:
                capability = self.repo.upsert_capability(Capability(task["capability"], 0))
            evidence_id = self.repo.add_evidence(Evidence(capability["id"], "task_result",
                encode({"reported_status": status, "task": task["task_text"], "feedback": feedback or "",
                        "verification": "self-reported completion evidence，未经外部独立验收；单条证据不升级 Level"}),
                "task", str(task_id)))
            progression = progress_capability(self.repo, task["capability"]) if status == "completed" else None
        # Core feedback is now durable, regardless of summary or planning outcome.
        try:
            summary = self.planning.memory.maybe_summarize(task["capability"])
        except Exception:
            summary = {"status": "summary_failed", "needs_retry": True}
        from core.router import EventRouter
        try:
            replanning = EventRouter(self.planning).dispatch(FEEDBACK_EVENTS[status])
        except Exception:
            replanning = self.planning._failure(FEEDBACK_EVENTS[status].value,
                BusinessError("planning_error", "后续规划失败。"))
        return {"status": "feedback_saved", "task_id": task_id, "task_status": status,
                "event_id": event_id, "evidence_id": evidence_id, "progression": progression, "summary": summary, "replanning": replanning}
