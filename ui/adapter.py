"""Small UI projection/action adapter. No duplicate gap, priority or memory algorithms."""
from contextlib import contextmanager
from copy import deepcopy
import hashlib
import json
from core.errors import BusinessError
from core.router import EventRouter
from services.profile_service import ProfileService
from services.jd_service import JDService
from services.planning_service import PlanningService
from services.task_service import TaskService
from storage.database import connect_database, DEFAULT_DATABASE_PATH
from storage.repository import Repository

LEVEL_LABELS = {0: "当前证据不足", 1: "知识理解", 2: "实践", 3: "真实经历", 4: "深度能力"}
STAGE_LABELS = {"evidence_knowledge_verification": "补充或核实基础知识证据", "practice": "动手练习",
                "experience": "贴近真实业务场景", "depth": "优化与深入评估"}
STATUS_LABELS = {"pending": "待完成", "completed": "已完成", "partial": "部分完成",
                 "not_completed": "未完成", "superseded": "已调整"}
TRIGGER_LABELS = {"PROFILE_CONFIRMED": "画像确认", "JD_ADDED": "新增岗位", "JD_ARCHIVED": "岗位归档",
                  "JD_REPLACED": "替换岗位", "TASK_COMPLETED": "任务完成", "TASK_PARTIAL": "部分完成反馈",
                  "TASK_NOT_COMPLETED": "未完成反馈", "manual": "手动规划", "retry": "重试规划"}


def level_label(level):
    return f"{level} · {LEVEL_LABELS.get(level, '待确认')}"


def validate_feedback(status, feedback):
    if status not in {"completed", "partial", "not_completed"}:
        raise BusinessError("invalid_feedback_status", "请选择任务完成情况。")
    if not isinstance(feedback, str):
        raise BusinessError("invalid_feedback", "反馈必须是文本。")
    if status != "completed" and not feedback.strip():
        raise BusinessError("feedback_required", "部分完成或未完成时，请填写已完成部分或原因。")


def evidence_text(content):
    try:
        data = json.loads(content)
    except (ValueError, TypeError):
        return content
    if isinstance(data, dict) and "reported_status" in data:
        return (f"用户报告：{STATUS_LABELS.get(data['reported_status'], data['reported_status'])}。"
                f"任务：{data.get('task', '')}。反馈：{data.get('feedback') or '未填写'}。"
                "这是用户自报记录，不是客观考试认证。")
    return content


def operation_key(action, value):
    content = value if isinstance(value, bytes) else str(value).encode("utf-8")
    return action + ":" + hashlib.sha256(content).hexdigest()


def run_once(state, key, operation):
    """Cache successful action results, including saved-feedback/replan-failure results."""
    results = state.setdefault("action_results", {})
    if key in results:
        return results[key]
    result = operation()
    results[key] = result
    if len(results) > 100:
        del results[next(iter(results))]
    return result


def profile_changes(draft, fields, rows):
    data = deepcopy(draft["draft_json"])
    for field in ("education", "internships", "projects", "skills"):
        data[field] = [line.strip() for line in fields[field].splitlines() if line.strip()]
    for field in ("major", "target_direction", "available_hours_per_day"):
        data[field] = fields[field]
    capabilities = []
    for original, row in zip(draft["draft_json"]["capabilities"], rows):
        if row["保留"]:
            capabilities.append({**original, "name": row["能力"], "level": int(str(row["等级"]).split(" · ")[0])})
    data["capabilities"] = capabilities
    return data


class ProductAdapter:
    def __init__(self, repository, *, planning=None):
        self.repo = repository
        self.planning = planning or PlanningService(repository, enable_tasks=True)
        router = EventRouter(self.planning)
        self.profiles = ProfileService(repository, event_router=router)
        self.jobs = JDService(repository, event_router=router)
        self.tasks = TaskService(repository, planning_service=self.planning)

    def dashboard(self):
        profile = self.repo.get_profile()
        priority = self.planning.get_priority()
        latest = self.repo.latest_event("REPLAN")
        needs_retry = bool(latest and latest["payload_json"].get("needs_retry"))
        snapshots = self.repo.list_snapshots(limit=1)
        selected = snapshots[0]["selected_task_json"] if snapshots else None
        task = self.repo.get_task(selected["id"]) if selected and "id" in selected else None
        if task and (task["status"] != "pending" or needs_retry):
            task = None
        top = priority["top_priority"]
        if task and (not top or task["capability"] != top["capability"]):
            task = None
        if not profile:
            empty = "先上传简历建立你的求职能力档案。"
        elif priority["status"] == "no_active_jd":
            empty = "添加至少一个目标岗位后，系统才能分析准备优先级。"
        elif priority["status"] == "no_positive_gap":
            empty = "当前没有识别到明确的正向能力 Gap。"
        elif not top:
            empty = priority["reason"]
        else:
            empty = ""
        explanation = ""
        if top:
            fact = top["reason"]
            required = "、".join(str(n) for n in sorted(set(top["required_levels"])))
            explanation = (f"{top['capability']} 覆盖 {fact['active_jd_count']}/{fact['total_active_jd_count']} 个目标岗位，"
                f"平均重要程度为 {top['importance']:.0%}。当前为{level_label(top['current_level'])}，"
                f"岗位要求等级为 {required}。它在正向差距候选中按固定评分与同分规则排名第一。")
        return {"profile_confirmed": profile is not None, "active_jd_count": len(self.jobs.list_active_jds()),
                "priority": priority, "task": task, "empty_message": empty, "explanation": explanation,
                "needs_retry": needs_retry, "revision": self.repo.event_head(), "replanning_reason": (latest or {}).get("payload_json", {}).get("reason", "")}

    def profile(self):
        return {"current": self.repo.get_profile(), "drafts": self.repo.open_profile_drafts(),
                "capabilities": self.capabilities()}

    def capabilities(self):
        return [{**c, "level_label": level_label(c["level"]), "evidence": self.repo.get_evidence(c["id"]),
                 "summary": self.repo.get_summary(c["capability_name"])} for c in self.repo.get_capabilities()]

    def job_summary(self):
        result = self.jobs.get_active_jd_requirements()
        return [{"能力": r["capability_name"], "岗位覆盖": f"{r['active_jd_count']}/{r['total_active_jd_count']}",
                 "要求等级": "、".join(str(n) for n in r["required_levels"]),
                 "重要程度": "、".join({"must_have": "必需", "important": "重要", "bonus": "加分"}[v] for v in r["importance_labels"])}
                for r in result["requirements"]]

    def feedback(self, task_id, status, feedback):
        validate_feedback(status, feedback)
        return self.tasks.submit_task_feedback(task_id, status, feedback)

    def history(self, limit=50):
        tasks = self.repo.get_task_history(limit=limit)
        for task in tasks:
            events = self.repo.list_events(entity_type="task", entity_id=task["id"], limit=20)
            feedback = next((e for e in reversed(events) if e["event_type"] in
                             {"TASK_COMPLETED", "TASK_PARTIAL", "TASK_NOT_COMPLETED"}), None)
            task["feedback"] = feedback["payload_json"].get("feedback", "") if feedback else ""
        return {"tasks": tasks, "capabilities": self.capabilities(), "snapshots": self.repo.list_snapshots(limit=20)}


@contextmanager
def open_product(path=DEFAULT_DATABASE_PATH):
    connection = connect_database(path)
    try:
        repo = Repository(connection)
        repo.initialize()
        yield ProductAdapter(repo)
    finally:
        connection.close()
