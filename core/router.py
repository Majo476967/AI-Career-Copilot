"""Explicit event dispatcher. No tool selection, LLM, event replay, or task feedback."""
from core.schemas import EventType

PLANNING_EVENTS = frozenset({"PROFILE_CONFIRMED", "JD_ADDED", "JD_ARCHIVED", "JD_REPLACED"})


class EventRouter:
    def __init__(self, planning_service):
        self.planning_service = planning_service

    def dispatch(self, event_type):
        value = event_type.value if isinstance(event_type, EventType) else event_type
        if not isinstance(value, str) or value not in PLANNING_EVENTS:
            return {"status": "ignored", "reason": "该事件不在 Phase 3 的 Priority 重算范围内。"}
        return self.planning_service.recompute(trigger=value)
