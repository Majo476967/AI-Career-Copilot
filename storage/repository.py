"""Small explicit repository. Reads return dicts with decoded *_json fields.

Each write commits immediately unless enclosed in `with repository.transaction():`.
No method silently writes events: future services compose state + events explicitly.
Closing a connection is the caller's responsibility.
"""
import json
import unicodedata
from datetime import datetime, timezone

from core.schemas import (Capability, CapabilityLevel, Event, EventType, Evidence,
                          JDStatus, MemorySummary, PlanningSnapshot, TargetJD,
                          Task, TaskStatus, UserProfile)
from storage.database import initialize_database, transaction


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def normalize_task(text):
    return " ".join(unicodedata.normalize("NFKC", text).split()).casefold()


def encode(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False)


def row_dict(row):
    if row is None:
        return None
    result = dict(row)
    for key in result:
        if key.endswith("_json"):
            result[key] = json.loads(result[key])
    return result


def nonempty(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be non-empty text")
    return value.strip()


class Repository:
    def __init__(self, connection):
        self.connection = connection

    def initialize(self):
        initialize_database(self.connection)

    def transaction(self):
        return transaction(self.connection)

    def get_profile(self):
        return row_dict(self.connection.execute("SELECT * FROM user_profile WHERE id=1").fetchone())

    def upsert_profile(self, profile: UserProfile):
        if not isinstance(profile.profile_json, dict):
            raise ValueError("profile_json must be an object")
        self.connection.execute("""
            INSERT INTO user_profile VALUES (1, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET education=excluded.education,
              major=excluded.major, target_direction=excluded.target_direction,
              available_hours_per_day=excluded.available_hours_per_day,
              resume_text=excluded.resume_text, profile_json=excluded.profile_json,
              updated_at=excluded.updated_at
        """, (profile.education, profile.major, profile.target_direction,
              profile.available_hours_per_day, profile.resume_text,
              encode(profile.profile_json), utc_now()))
        return self.get_profile()

    def get_capability(self, name):
        return row_dict(self.connection.execute(
            "SELECT * FROM user_capabilities WHERE capability_name=?", (name,)).fetchone())

    def get_capabilities(self):
        return [row_dict(r) for r in self.connection.execute("SELECT * FROM user_capabilities ORDER BY id")]

    def upsert_capability(self, capability: Capability):
        name = nonempty(capability.capability_name, "capability_name")
        if isinstance(capability.level, bool) or not isinstance(capability.level, int):
            raise ValueError("level must be an integer from 0 to 4")
        level = CapabilityLevel(capability.level)
        self.connection.execute("""
            INSERT INTO user_capabilities(capability_name, level, updated_at) VALUES (?, ?, ?)
            ON CONFLICT(capability_name) DO UPDATE SET level=excluded.level, updated_at=excluded.updated_at
        """, (name, int(level), utc_now()))
        return self.get_capability(name)

    def add_evidence(self, evidence: Evidence):
        cursor = self.connection.execute("""
            INSERT INTO capability_evidence(capability_id, evidence_type, content, source, source_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (evidence.capability_id, nonempty(evidence.evidence_type, "evidence_type"),
              nonempty(evidence.content, "content"), nonempty(evidence.source, "source"),
              evidence.source_id, evidence.created_at or utc_now()))
        return cursor.lastrowid

    def get_evidence(self, capability_id):
        return [row_dict(r) for r in self.connection.execute(
            "SELECT * FROM capability_evidence WHERE capability_id=? ORDER BY id", (capability_id,))]

    def add_jd(self, jd: TargetJD):
        if not isinstance(jd.jd_analysis_json, dict):
            raise ValueError("jd_analysis_json must be an object")
        cursor = self.connection.execute("""
            INSERT INTO target_jds(company, job_title, jd_text, jd_analysis_json, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (jd.company, jd.job_title, nonempty(jd.jd_text, "jd_text"),
              encode(jd.jd_analysis_json), JDStatus.ACTIVE.value, utc_now()))
        return cursor.lastrowid

    def get_jd(self, jd_id):
        return row_dict(self.connection.execute("SELECT * FROM target_jds WHERE id=?", (jd_id,)).fetchone())

    def get_active_jds(self):
        return [row_dict(r) for r in self.connection.execute(
            "SELECT * FROM target_jds WHERE status='active' ORDER BY id")]

    def archive_jd(self, jd_id):
        if self.get_jd(jd_id) is None:
            raise KeyError(jd_id)
        self.connection.execute("""UPDATE target_jds SET status='archived', archived_at=?
            WHERE id=? AND status='active'""", (utc_now(), jd_id))

    def create_task(self, task: Task, *, legacy_unknown_time=False):
        text = nonempty(task.task_text, "task_text")
        if not isinstance(task.acceptance_criteria_json, list) or not all(
                isinstance(item, str) for item in task.acceptance_criteria_json):
            raise ValueError("acceptance criteria must be a list of strings")
        status = TaskStatus(task.status)
        now = None if legacy_unknown_time else utc_now()
        cursor = self.connection.execute("""
            INSERT INTO tasks(capability, task_text, task_key, reason, estimated_time,
              acceptance_criteria_json, status, created_at, completed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (nonempty(task.capability, "capability"), text, normalize_task(text), task.reason,
              task.estimated_time, encode(task.acceptance_criteria_json), status.value, now,
              now if status == TaskStatus.COMPLETED else None))
        return cursor.lastrowid

    def get_task(self, task_id):
        return row_dict(self.connection.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone())

    def find_task_by_text(self, text):
        """Return the earliest matching task, keeping legacy migration identity stable.

        This is a history lookup, not the pending duplicate check (enforced by SQLite).
        """
        return row_dict(self.connection.execute(
            "SELECT * FROM tasks WHERE task_key=? ORDER BY id ASC LIMIT 1",
            (normalize_task(text),)).fetchone())

    def update_task_status(self, task_id, status):
        """State-only primitive; feedback validation/event composition belongs to future services."""
        status = TaskStatus(status)
        if self.get_task(task_id) is None:
            raise KeyError(task_id)
        self.connection.execute("""UPDATE tasks SET status=?, completed_at=
            CASE WHEN ?='completed' THEN CASE WHEN status='completed' THEN completed_at ELSE ? END
            ELSE NULL END WHERE id=?""", (status.value, status.value, utc_now(), task_id))

    def get_task_history(self, *, capability=None, limit=100):
        """Task records in insertion order, not inferred historical timestamps. Events hold feedback history."""
        sql, params = "SELECT * FROM tasks", []
        if capability is not None:
            sql += " WHERE capability=?"
            params.append(capability)
        sql += " ORDER BY id DESC LIMIT ?"
        params.append(self._limit(limit))
        return [row_dict(r) for r in self.connection.execute(sql, params)]

    def create_snapshot(self, snapshot: PlanningSnapshot):
        cursor = self.connection.execute("""INSERT INTO planning_snapshots(trigger, active_jds_json,
            capability_state_json, priority_result_json, selected_task_json, reason, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)""", (snapshot.trigger, encode(snapshot.active_jds_json),
            encode(snapshot.capability_state_json), encode(snapshot.priority_result_json),
            encode(snapshot.selected_task_json), snapshot.reason, utc_now()))
        return cursor.lastrowid

    def get_snapshot(self, snapshot_id):
        return row_dict(self.connection.execute(
            "SELECT * FROM planning_snapshots WHERE id=?", (snapshot_id,)).fetchone())

    def list_snapshots(self, limit=10):
        return [row_dict(r) for r in self.connection.execute(
            "SELECT * FROM planning_snapshots ORDER BY id DESC LIMIT ?", (self._limit(limit),))]

    def upsert_summary(self, summary: MemorySummary):
        self.connection.execute("""INSERT INTO memory_summaries(scope, summary, covered_until_event_id, updated_at)
            VALUES (?, ?, ?, ?) ON CONFLICT(scope) DO UPDATE SET summary=excluded.summary,
            covered_until_event_id=excluded.covered_until_event_id, updated_at=excluded.updated_at""",
            (nonempty(summary.scope, "scope"), summary.summary, summary.covered_until_event_id, utc_now()))
        return self.get_summary(summary.scope)

    def get_summary(self, scope):
        return row_dict(self.connection.execute(
            "SELECT * FROM memory_summaries WHERE scope=?", (scope,)).fetchone())

    def append_event(self, event: Event):
        if not isinstance(event.payload_json, dict):
            raise ValueError("payload_json must be an object")
        cursor = self.connection.execute("""INSERT INTO events(event_type, entity_type, entity_id,
            payload_json, created_at) VALUES (?, ?, ?, ?, ?)""", (EventType(event.event_type).value,
            nonempty(event.entity_type, "entity_type"), nonempty(str(event.entity_id), "entity_id"),
            encode(event.payload_json), utc_now()))
        return cursor.lastrowid

    def list_events(self, *, entity_type=None, entity_id=None, event_type=None, after_id=0, limit=100):
        conditions, params = ["id > ?"], [after_id]
        for column, value in (("entity_type", entity_type), ("entity_id", entity_id), ("event_type", event_type)):
            if value is not None:
                conditions.append(column + "=?")
                params.append(EventType(value).value if column == "event_type" else str(value))
        sql = "SELECT * FROM events WHERE " + " AND ".join(conditions) + " ORDER BY id LIMIT ?"
        return [row_dict(r) for r in self.connection.execute(sql, params + [self._limit(limit)])]

    def has_migration_key(self, key):
        return self.connection.execute("""SELECT 1 FROM events
            WHERE json_extract(payload_json, '$.migration.import_key')=?""", (key,)).fetchone() is not None

    @staticmethod
    def _limit(limit):
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
            raise ValueError("limit must be a positive integer")
        return limit
