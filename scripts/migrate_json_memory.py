"""Import legacy task observations without changing the JSON or inferring ability.

Run: python -m scripts.migrate_json_memory --database runtime/career_copilot.sqlite3
Event created_at is import/recording time. Original occurrence time stays unknown
unless explicitly present in the source payload. Existing V1 task state is never
rewound on repeated imports. Source identity is stable even if the file is copied.
"""
import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.schemas import Event, EventType, Task, TaskStatus
from storage.database import DEFAULT_DATABASE_PATH, connect_database
from storage.repository import Repository, normalize_task

DEFAULT_SOURCE = Path(__file__).resolve().parents[1] / "memory" / "user_state.json"
STATUS_EVENTS = {
    "completed": EventType.TASK_COMPLETED,
    "partial": EventType.TASK_PARTIAL,
    "not_completed": EventType.TASK_NOT_COMPLETED,
}


def digest(value):
    text = json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def migrate_json_memory(source, repository):
    data = json.loads(Path(source).read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("Legacy memory must be an object")
    groups = {}
    skipped = []

    def group(text):
        key = normalize_task(text)
        return groups.setdefault(key, {"text": text, "history": [], "lists": []})

    history = data.get("task_history", [])
    if not isinstance(history, list):
        raise ValueError("task_history must be a list")
    occurrences = Counter()
    for index, record in enumerate(history):
        if (not isinstance(record, dict) or not isinstance(record.get("task"), str)
                or not record["task"].strip() or not isinstance(record.get("status"), str)
                or record["status"] not in STATUS_EVENTS):
            skipped.append(f"task_history[{index}]: unrecognized task/status")
            continue
        identity = digest(record)
        occurrences[identity] += 1
        # Preserve repeated observations, while remaining stable under file copying/reordering.
        key = f"legacy-json-v1:history:{identity}:{occurrences[identity]}"
        group(record["task"])["history"].append((key, index, record))

    for name in ("completed_tasks", "pending_tasks"):
        values = data.get(name, [])
        if not isinstance(values, list):
            raise ValueError(f"{name} must be a list")
        for index, text in enumerate(values):
            if not isinstance(text, str) or not text.strip():
                skipped.append(f"{name}[{index}]: unrecognized task")
                continue
            entry = group(text)
            observation = {"list": name, "task": text}
            if observation not in entry["lists"]:
                entry["lists"].append(observation)

    counts = {"tasks_created": 0, "events_appended": 0, "skipped": skipped}
    with repository.transaction():
        for normalized, entry in groups.items():
            task = repository.find_task_by_text(entry["text"])
            statuses = {item["list"] for item in entry["lists"]}
            conflict = len(statuses) > 1
            if entry["history"]:
                status = entry["history"][-1][2]["status"]
                conflict = conflict or ("completed_tasks" in statuses and status != "completed")
                conflict = conflict or ("pending_tasks" in statuses and status == "completed")
            elif "completed_tasks" in statuses and not conflict:
                status = "completed"
            else:
                # A conflicting completed/pending pair cannot establish completion.
                status = "pending"
            task_key = f"legacy-json-v1:task:{digest(normalized)}"
            if task is None:
                task_id = repository.create_task(Task(
                    capability="unknown", task_text=entry["text"],
                    reason="Legacy migration: capability, acceptance criteria and original times unknown",
                    status=TaskStatus(status)), legacy_unknown_time=True)
                counts["tasks_created"] += 1
                repository.append_event(Event(EventType.TASK_CREATED, "task", str(task_id), {
                    "task_text": entry["text"],
                    "migration": {"import_key": task_key, "source": "legacy_json_memory",
                        "occurred_at": None, "time_status": "unknown",
                        "state_basis": "last source history entry; otherwise legacy lists",
                        "status_conflict": conflict, "source_lists": entry["lists"],
                        "note": "TASK_CREATED records import, not a known historical creation event"}}))
                counts["events_appended"] += 1
            else:
                task_id = task["id"]

            for key, index, record in entry["history"]:
                if repository.has_migration_key(key):
                    continue
                repository.append_event(Event(STATUS_EVENTS[record["status"]], "task", str(task_id), {
                    "feedback": record.get("feedback"), "original_record": record,
                    "migration": {"import_key": key, "source": "legacy_json_memory",
                        "source_index": index, "occurred_at": None, "time_status": "unknown",
                        "original_timestamp": record.get("created_at"),
                        "feedback_status": "provided" if record.get("feedback") else "unknown",
                        "status_conflict": conflict}}))
                counts["events_appended"] += 1
            # History is authoritative for imported status. Lists are preserved in creation
            # metadata; do not count a matching completed list entry as another completion.
            for observation in entry["lists"]:
                if entry["history"] or observation["list"] == "pending_tasks":
                    continue
                key = f"legacy-json-v1:list:{digest(observation)}"
                if repository.has_migration_key(key):
                    continue
                event_type = (EventType.TASK_COMPLETED if observation["list"] == "completed_tasks"
                              else EventType.TASK_CREATED)
                repository.append_event(Event(event_type, "task", str(task_id), {
                    "original_record": observation,
                    "migration": {"import_key": key, "source": "legacy_json_memory",
                        "observation_only": True, "occurred_at": None, "time_status": "unknown",
                        "feedback_status": "unknown", "status_conflict": conflict}}))
                counts["events_appended"] += 1
    return counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE_PATH)
    args = parser.parse_args()
    connection = connect_database(args.database)
    try:
        repository = Repository(connection)
        repository.initialize()
        print(json.dumps(migrate_json_memory(args.source, repository), ensure_ascii=False))
    finally:
        connection.close()


if __name__ == "__main__":
    main()
