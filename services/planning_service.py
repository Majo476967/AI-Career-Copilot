"""Priority-only compatibility and explicitly enabled, transactional task planning."""
from contextlib import nullcontext
from core.schemas import PlanningSnapshot, Event, EventType, TaskStatus
from core.errors import BusinessError
from core import config
from core.planner import TaskPlanner, task_budget, duration_minutes
from storage.repository import normalize_task
from services.memory_service import MemoryService
from core.priority_engine import calculate_priorities, empty_result
from services.common import storage_errors


class PlanningService:
    def __init__(self, repository, *, enable_tasks=False, planner=None, memory_service=None):
        self.repo = repository
        self.enable_tasks = enable_tasks
        self.planner = planner if planner is not None else (TaskPlanner() if enable_tasks else None)
        self.memory = memory_service if memory_service is not None else (MemoryService(repository) if enable_tasks else None)

    @storage_errors
    def get_priority(self):
        """Read-only UI projection; no snapshot, model call or task creation on rerun."""
        if self.repo.get_profile() is None:
            return empty_result("no_confirmed_profile")
        return calculate_priorities(self.repo.get_active_jds(), self.repo.get_capabilities())

    @storage_errors
    def recompute(self, trigger="manual"):
        if self.enable_tasks:
            return self._replan(trigger)
        return self._priority_only(trigger)

    def _priority_only(self, trigger):
        if not isinstance(trigger, str) or not trigger.strip():
            return {**empty_result("invalid_input", "Snapshot trigger 必须为非空文本。"), "snapshot_id": None}
        # Reuse the transaction owned by an injected Profile/JD workflow.
        scope = nullcontext() if self.repo.connection.in_transaction else self.repo.transaction()
        with scope:
            profile = self.repo.get_profile()
            jds = self.repo.get_active_jds()
            capabilities = self.repo.get_capabilities()
            capability_state = [{**item, "evidence": self.repo.get_evidence(item["id"])} for item in capabilities]
            if profile is None:
                result = empty_result("no_confirmed_profile")
            else:
                result = calculate_priorities(jds, capabilities)
            result["warnings"] = []
            if profile is not None and not any(item["evidence"] for item in capability_state):
                result["warnings"].append("当前没有 Capability Evidence 记录，请补充证据；已有确认等级不会被本计算改写。")
            if result["status"] == "invalid_input":
                # Invalid input is not saved as a valid decision snapshot.
                result["snapshot_id"] = None
                return result
            snapshot_id = self.repo.create_snapshot(PlanningSnapshot(
                trigger=trigger, active_jds_json=jds, capability_state_json=capability_state,
                priority_result_json=result, selected_task_json=None, reason=result["reason"]))
            return {**result, "snapshot_id": snapshot_id}

    def _read_state(self):
        capabilities = self.repo.get_capabilities()
        return {"profile": self.repo.get_profile(), "jds": self.repo.get_active_jds(),
                "capabilities": [{**c, "evidence": self.repo.get_evidence(c["id"])} for c in capabilities],
                "pending": self.repo.pending_tasks(), "event_head": self.repo.event_head()}

    def _valid_pending(self, task, top, budget):
        if not top or task["capability"] != top["capability"]:
            return False, "任务能力已不是当前 Top Priority。"
        creation = self.repo.task_creation_event(task["id"])
        basis = (creation or {}).get("payload_json", {}).get("planning_basis", {})
        if basis.get("current_level") != top["current_level"] or basis.get("next_gap_type") != top["next_gap_type"]:
            return False, "当前等级或下一等级已变化，或旧任务缺少创建依据。"
        try:
            if duration_minutes(task["estimated_time"]) > budget:
                return False, "任务超过新的时间预算。"
        except BusinessError:
            return False, "旧任务没有有效时长。"
        if self.repo.capability_events(task["capability"], after_id=creation["id"], limit=1, feedback_only=True):
            return False, "任务创建后出现新的相关反馈，需要重新设计。"
        return True, "能力方向、等级、时间预算仍匹配，且没有新的相关反馈，保留 pending 任务。"

    def _failure(self, trigger, error):
        code = error.code if isinstance(error, BusinessError) else "planning_error"
        result = {"status": "planning_failed", "needs_retry": True, "error_code": code,
                  "reason": "重规划未完成；已提交的反馈和原始记录保留，请重试。"}
        try:
            if self.repo.connection.in_transaction:
                raise BusinessError("transaction_open", "请先提交业务事务。")
            with self.repo.transaction():
                result["event_id"] = self.repo.append_event(Event(EventType.REPLAN, "planning", "current",
                    {"trigger": trigger if isinstance(trigger, str) else "unknown", **result}))
        except Exception:
            result["failure_recorded"] = False
        else:
            result["failure_recorded"] = True
        return result

    def _replan(self, trigger):
        try:
            if not isinstance(trigger, str) or not trigger.strip():
                raise BusinessError("invalid_trigger", "缺少规划触发原因。")
            if self.repo.connection.in_transaction:
                raise BusinessError("transaction_open", "完整重规划须在业务事务提交后运行。")
            with self.repo.transaction():
                state = self._read_state()
                priority = (calculate_priorities(state["jds"], state["capabilities"])
                            if state["profile"] else empty_result("no_confirmed_profile"))
                if priority["status"] == "invalid_input":
                    raise BusinessError("invalid_input", priority["reason"])
                top = priority["top_priority"]
                budget = task_budget((state["profile"] or {}).get("available_hours_per_day"))
                checks = [(t, *self._valid_pending(t, top, budget)) for t in state["pending"]]
            retained = next((t for t, valid, _ in checks if valid), None)
            reason = next((why for t, valid, why in checks if valid), priority["reason"])
            generated = None
            if top and budget >= config.MIN_TASK_MINUTES and retained is None:
                context = self.memory.build_context(priority, state["profile"])
                generated = self.planner.plan(context)
                forbidden = state["pending"] + self.repo.recent_terminal_tasks(top["capability"], config.RELEVANT_HISTORY_LIMIT)
                if normalize_task(generated.task_text) in {t["task_key"] for t in forbidden}:
                    raise BusinessError("duplicate_recent_task", "生成任务与 pending 或近期已反馈任务完全重复。")
                reason = "按当前 Top Priority 和相关反馈生成任务；" + generated.reason
                action = "created"
            elif retained:
                action = "retained"
            else:
                action = "no_time_budget" if top else "no_task"
                reason = "当前时间预算不足 5 分钟，不强行生成任务。" if top else priority["reason"]
            # No LLM call occurs inside this write transaction.
            with self.repo.transaction():
                if self._read_state() != state:
                    raise BusinessError("stale_state", "生成期间状态发生变化，请按最新状态重试。")
                superseded = []
                for task, valid, why in checks:
                    if retained is None or task["id"] != retained["id"]:
                        self.repo.update_task_status(task["id"], TaskStatus.SUPERSEDED)
                        superseded.append({"task_id": task["id"], "reason": why if not valid else "保留另一项仍有效的当前任务。"})
                selected = retained
                if generated is not None:
                    from services.task_service import TaskService
                    selected = TaskService(self.repo).create_task(generated, planning_basis={
                        "current_level": top["current_level"], "next_gap_type": top["next_gap_type"],
                        "task_budget_minutes": budget})
                planning = {"status": action, "trigger": trigger, "reason": reason,
                            "selected_task_id": selected["id"] if selected else None,
                            "superseded": superseded, "needs_retry": False}
                event_id = self.repo.append_event(Event(EventType.REPLAN, "planning", "current", planning))
                snapshot_id = self.repo.create_snapshot(PlanningSnapshot(trigger, state["jds"], state["capabilities"],
                    {**priority, "planning": planning}, selected, reason))
            return {**priority, "planning_status": action, "selected_task": selected,
                    "snapshot_id": snapshot_id, "event_id": event_id, "needs_retry": False}
        except Exception as error:
            return self._failure(trigger, error)
