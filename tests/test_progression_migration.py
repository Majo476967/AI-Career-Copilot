import sqlite3
import tempfile
import unittest
from pathlib import Path
from storage.database import connect_database, initialize_database
from storage.repository import Repository
from core.schemas import Event, EventType, MemorySummary, Task

OLD_SCHEMA = "-- Single-user V1.0 foundation. JSON is serialized at the repository boundary.\nCREATE TABLE IF NOT EXISTS user_profile (\n    id INTEGER PRIMARY KEY CHECK (id = 1),\n    education TEXT NOT NULL,\n    major TEXT NOT NULL,\n    target_direction TEXT NOT NULL,\n    available_hours_per_day REAL CHECK (available_hours_per_day BETWEEN 0 AND 24),\n    resume_text TEXT NOT NULL,\n    profile_json TEXT NOT NULL CHECK (json_valid(profile_json)),\n    updated_at TEXT NOT NULL\n);\nCREATE TABLE IF NOT EXISTS user_capabilities (\n    id INTEGER PRIMARY KEY,\n    capability_name TEXT NOT NULL UNIQUE CHECK (length(trim(capability_name)) > 0),\n    level INTEGER NOT NULL CHECK (typeof(level) = 'integer' AND level BETWEEN 0 AND 4),\n    updated_at TEXT NOT NULL\n);\nCREATE TABLE IF NOT EXISTS capability_evidence (\n    id INTEGER PRIMARY KEY,\n    capability_id INTEGER NOT NULL REFERENCES user_capabilities(id),\n    evidence_type TEXT NOT NULL CHECK (length(trim(evidence_type)) > 0),\n    content TEXT NOT NULL CHECK (length(trim(content)) > 0),\n    source TEXT NOT NULL CHECK (length(trim(source)) > 0),\n    source_id TEXT,\n    created_at TEXT NOT NULL\n);\nCREATE TABLE IF NOT EXISTS target_jds (\n    id INTEGER PRIMARY KEY,\n    company TEXT NOT NULL,\n    job_title TEXT NOT NULL,\n    jd_text TEXT NOT NULL CHECK (length(trim(jd_text)) > 0),\n    jd_analysis_json TEXT NOT NULL CHECK (json_valid(jd_analysis_json)),\n    status TEXT NOT NULL CHECK (status IN ('active', 'archived')),\n    created_at TEXT NOT NULL,\n    archived_at TEXT,\n    CHECK ((status = 'active' AND archived_at IS NULL) OR\n           (status = 'archived' AND archived_at IS NOT NULL))\n);\nCREATE TABLE IF NOT EXISTS tasks (\n    id INTEGER PRIMARY KEY,\n    capability TEXT NOT NULL CHECK (length(trim(capability)) > 0),\n    task_text TEXT NOT NULL CHECK (length(trim(task_text)) > 0),\n    task_key TEXT NOT NULL,\n    reason TEXT NOT NULL,\n    estimated_time TEXT NOT NULL,\n    acceptance_criteria_json TEXT NOT NULL CHECK (json_valid(acceptance_criteria_json)),\n    status TEXT NOT NULL CHECK (status IN\n        ('pending', 'completed', 'partial', 'not_completed', 'superseded')),\n    created_at TEXT, -- NULL for imported history with unknown creation time.\n    completed_at TEXT,\n    CHECK (status = 'completed' OR completed_at IS NULL)\n);\nCREATE TABLE IF NOT EXISTS planning_snapshots (\n    id INTEGER PRIMARY KEY,\n    trigger TEXT NOT NULL,\n    active_jds_json TEXT NOT NULL CHECK (json_valid(active_jds_json)),\n    capability_state_json TEXT NOT NULL CHECK (json_valid(capability_state_json)),\n    priority_result_json TEXT NOT NULL CHECK (json_valid(priority_result_json)),\n    selected_task_json TEXT NOT NULL CHECK (json_valid(selected_task_json)),\n    reason TEXT NOT NULL,\n    created_at TEXT NOT NULL\n);\nCREATE TABLE IF NOT EXISTS events (\n    id INTEGER PRIMARY KEY AUTOINCREMENT,\n    event_type TEXT NOT NULL CHECK (event_type IN\n        ('TASK_CREATED', 'TASK_COMPLETED', 'TASK_PARTIAL', 'TASK_NOT_COMPLETED',\n         'JD_ADDED', 'JD_ARCHIVED', 'JD_REPLACED', 'PROFILE_CONFIRMED', 'REPLAN')),\n    entity_type TEXT NOT NULL CHECK (length(trim(entity_type)) > 0),\n    entity_id TEXT NOT NULL CHECK (length(trim(entity_id)) > 0),\n    payload_json TEXT NOT NULL CHECK (json_valid(payload_json)),\n    created_at TEXT NOT NULL -- Event recording time, not inferred historical time.\n);\nCREATE TABLE IF NOT EXISTS memory_summaries (\n    id INTEGER PRIMARY KEY,\n    scope TEXT NOT NULL UNIQUE CHECK (length(trim(scope)) > 0),\n    summary TEXT NOT NULL,\n    covered_until_event_id INTEGER REFERENCES events(id),\n    updated_at TEXT NOT NULL\n);\nCREATE INDEX IF NOT EXISTS evidence_capability ON capability_evidence(capability_id, id);\nCREATE INDEX IF NOT EXISTS active_jds ON target_jds(status, id);\nCREATE INDEX IF NOT EXISTS task_capability ON tasks(capability, id);\n-- Only simultaneous pending duplicates are forbidden; historical tasks stay intact.\nCREATE UNIQUE INDEX IF NOT EXISTS pending_task_key ON tasks(task_key)\n    WHERE status = 'pending';\nCREATE INDEX IF NOT EXISTS event_entity ON events(entity_type, entity_id, id);\nCREATE INDEX IF NOT EXISTS event_type ON events(event_type, id);\n-- A migration key lives in metadata, not in the product's entity schema.\nCREATE UNIQUE INDEX IF NOT EXISTS event_migration_key\n    ON events(json_extract(payload_json, '$.migration.import_key'))\n    WHERE json_extract(payload_json, '$.migration.import_key') IS NOT NULL;\nCREATE TRIGGER IF NOT EXISTS events_no_update BEFORE UPDATE ON events\nBEGIN SELECT RAISE(ABORT, 'events are append-only'); END;\nCREATE TRIGGER IF NOT EXISTS events_no_delete BEFORE DELETE ON events\nBEGIN SELECT RAISE(ABORT, 'events are append-only'); END;\n\n-- Independent staging; never treated as confirmed Current State.\nCREATE TABLE IF NOT EXISTS profile_drafts (\n    id INTEGER PRIMARY KEY AUTOINCREMENT,\n    resume_text TEXT NOT NULL,\n    resume_version TEXT NOT NULL,\n    draft_json TEXT NOT NULL CHECK (json_valid(draft_json)),\n    status TEXT NOT NULL CHECK (status IN ('draft', 'confirmed', 'discarded')),\n    created_at TEXT NOT NULL,\n    updated_at TEXT NOT NULL,\n    confirmed_at TEXT\n);\n"


class ProgressionMigrationTests(unittest.TestCase):
    def test_old_database_upgrade_preserves_events_and_watermark(self):
        with tempfile.TemporaryDirectory() as directory:
            connection = connect_database(Path(directory) / "old.sqlite3")
            try:
                connection.executescript(OLD_SCHEMA)
                connection.execute("INSERT INTO tasks(capability,task_text,task_key,reason,estimated_time,acceptance_criteria_json,status) VALUES ('SQL','legacy','legacy','','unknown','[]','completed')")
                repo = Repository(connection)
                event_id = repo.append_event(Event(EventType.TASK_COMPLETED, "task", "1", {"legacy": True}))
                repo.upsert_summary(MemorySummary("SQL", "legacy summary", event_id))
                before = repo.list_events()
                initialize_database(connection)
                initialize_database(connection)
                self.assertEqual(repo.list_events(), before)
                self.assertEqual(repo.get_summary("SQL")["covered_until_event_id"], event_id)
                self.assertIsNone(repo.get_task(1)["gap_type"])
                self.assertIsNone(repo.get_task(1)["target_level"])
                self.assertEqual(connection.execute("PRAGMA foreign_keys").fetchone()[0], 1)
                self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])
                new_id = repo.append_event(Event(EventType.CAPABILITY_LEVEL_CHANGED, "capability", "1"))
                self.assertGreater(new_id, event_id)
                with self.assertRaises(sqlite3.IntegrityError):
                    connection.execute("DELETE FROM events")
                with self.assertRaises(sqlite3.IntegrityError):
                    connection.execute("UPDATE events SET entity_id='2'")
                task_id = repo.create_task(Task("SQL", "new stage", gap_type="practice", target_level=2))
                self.assertEqual(repo.get_task(task_id)["target_level"], 2)
            finally:
                connection.close()
