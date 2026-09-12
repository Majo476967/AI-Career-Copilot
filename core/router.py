"""Deterministic dispatcher; feedback workflows require explicit task mode."""
from core.schemas import EventType

PLANNING_EVENTS = frozenset({"PROFILE_CONFIRMED", "JD_ADDED", "JD_ARCHIVED", "JD_REPLACED"})

FEEDBACK_EVENTS = frozenset({"TASK_COMPLETED", "TASK_PARTIAL", "TASK_NOT_COMPLETED"})


class EventRouter:
    def __init__(self, planning_service):
        self.planning_service = planning_service

    @property
    def defer_until_commit(self):
        return self.planning_service.enable_tasks

    def dispatch(self, event_type):
        value = event_type.value if isinstance(event_type, EventType) else event_type
        supported = PLANNING_EVENTS | (FEEDBACK_EVENTS if self.defer_until_commit else frozenset())
        if not isinstance(value, str) or value not in supported:
            return {"status": "ignored", "reason": "该事件不在当前模式的规划范围内。"}
        return self.planning_service.recompute(trigger=value)
