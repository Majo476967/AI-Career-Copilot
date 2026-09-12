"""Phase 1 data contracts; no analysis, routing or planning behavior."""
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Any


class CapabilityLevel(IntEnum):
    # Unknown evidence is NOT proof of low ability.
    UNKNOWN_EVIDENCE = 0
    KNOWLEDGE = 1
    PRACTICE = 2
    EXPERIENCE = 3
    DEPTH = 4


class JDStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class TaskStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    PARTIAL = "partial"
    NOT_COMPLETED = "not_completed"
    SUPERSEDED = "superseded"


class EventType(str, Enum):
    TASK_CREATED = "TASK_CREATED"
    TASK_COMPLETED = "TASK_COMPLETED"
    TASK_PARTIAL = "TASK_PARTIAL"
    TASK_NOT_COMPLETED = "TASK_NOT_COMPLETED"
    JD_ADDED = "JD_ADDED"
    JD_ARCHIVED = "JD_ARCHIVED"
    JD_REPLACED = "JD_REPLACED"
    PROFILE_CONFIRMED = "PROFILE_CONFIRMED"
    CAPABILITY_LEVEL_CHANGED = "CAPABILITY_LEVEL_CHANGED"
    REPLAN = "REPLAN"


@dataclass
class UserProfile:
    education: str = ""
    major: str = ""
    target_direction: str = ""
    available_hours_per_day: float | None = None
    resume_text: str = ""
    profile_json: dict[str, Any] = field(default_factory=dict)


@dataclass
class Capability:
    capability_name: str
    level: CapabilityLevel = CapabilityLevel.UNKNOWN_EVIDENCE


@dataclass
class Evidence:
    capability_id: int
    evidence_type: str
    content: str
    source: str
    source_id: str | None = None
    created_at: str | None = None


@dataclass
class TargetJD:
    company: str
    job_title: str
    jd_text: str
    jd_analysis_json: dict[str, Any] = field(default_factory=dict)


@dataclass
class Task:
    capability: str
    task_text: str
    reason: str = ""
    estimated_time: str = "unknown"
    acceptance_criteria_json: list[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    gap_type: str | None = None
    target_level: int | None = None


@dataclass
class PlanningSnapshot:
    trigger: str
    active_jds_json: list[Any]
    capability_state_json: list[Any]
    priority_result_json: dict[str, Any] | list[Any]
    selected_task_json: dict[str, Any] | None
    reason: str


@dataclass
class MemorySummary:
    scope: str
    summary: str
    covered_until_event_id: int | None = None


@dataclass
class Event:
    event_type: EventType
    entity_type: str
    entity_id: str
    payload_json: dict[str, Any] = field(default_factory=dict)
