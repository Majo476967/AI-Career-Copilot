"""Offline storage tests. Every test owns a temporary database and source fixture."""
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.schemas import (Capability, CapabilityLevel, Event, EventType, Evidence,
                          MemorySummary, PlanningSnapshot, TargetJD, Task, TaskStatus, UserProfile)
from scripts.migrate_json_memory import migrate_json_memory
from storage.database import connect_database
from storage.repository import Repository


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "test.sqlite3"
        self.connection = connect_database(self.path)
        self.addCleanup(lambda: self.connection.close())
        self.repo = Repository(self.connection)
        self.repo.initialize()

    def fixture(self, data):
        path = Path(self.temp.name) / "legacy.json"
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return path

    def test_initialization_is_repeatable(self):
        self.repo.initialize()
        tables = {r[0] for r in self.connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertTrue({"user_profile", "user_capabilities", "capability_evidence", "target_jds",
                         "tasks", "events", "planning_snapshots", "memory_summaries"} <= tables)
        self.assertEqual(self.connection.execute("PRAGMA foreign_keys").fetchone()[0], 1)

    def test_profile_persists_and_updates(self):
        self.repo.upsert_profile(UserProfile(education="本科", available_hours_per_day=3,
                                            profile_json={"projects": ["demo"]}))
        profile = self.repo.get_profile()
        self.assertEqual(profile["profile_json"]["projects"], ["demo"])
        self.repo.upsert_profile(UserProfile(education="硕士"))
        self.assertEqual(self.repo.get_profile()["education"], "硕士")
        self.assertEqual(self.connection.execute("SELECT count(*) FROM user_profile").fetchone()[0], 1)

    def test_capability_and_traceable_evidence(self):
        capability = self.repo.upsert_capability(Capability("SQL"))
        self.assertEqual(capability["level"], CapabilityLevel.UNKNOWN_EVIDENCE)
        self.repo.add_evidence(Evidence(capability["id"], "task_feedback", "完成 JOIN 练习", "task", "12"))
        evidence = self.repo.get_evidence(capability["id"])[0]
        self.assertEqual(evidence["source_id"], "12")
        self.assertTrue(evidence["created_at"])
        self.assertEqual(self.repo.get_capability("SQL")["level"], 0)  # No automatic upgrade.
        self.repo.upsert_capability(Capability("SQL", CapabilityLevel.PRACTICE))
        self.assertEqual(self.repo.get_capability("SQL")["id"], capability["id"])
        self.assertEqual(len(self.repo.get_evidence(capability["id"])), 1)

    def test_invalid_level_and_orphan_evidence_are_rejected(self):
        for level in (-1, 5, 1.5, True):
            with self.assertRaises(ValueError):
                self.repo.upsert_capability(Capability("SQL", level))
        with self.assertRaises(sqlite3.IntegrityError):
            self.repo.add_evidence(Evidence(999, "resume", "demo", "resume"))

    def test_active_jds_and_archive(self):
        ids = [self.repo.add_jd(TargetJD("公司", str(i), "要求 SQL")) for i in range(4)]
        self.assertEqual(len(self.repo.get_active_jds()), 4)
        self.repo.archive_jd(ids[0])
        archived = self.repo.get_jd(ids[0])
        self.assertEqual(archived["status"], "archived")
        self.assertTrue(archived["archived_at"])
        self.repo.archive_jd(ids[0])
        self.assertEqual(self.repo.get_jd(ids[0])["archived_at"], archived["archived_at"])
        self.assertEqual(len(self.repo.get_active_jds()), 3)

    def test_task_persistence_status_and_history(self):
        task_id = self.repo.create_task(Task("SQL", "完成 JOIN", "岗位要求", "1 hour", ["保存查询结果"]))
        self.assertEqual(self.repo.get_task(task_id)["acceptance_criteria_json"], ["保存查询结果"])
        for status in TaskStatus:
            self.repo.update_task_status(task_id, status)
            task = self.repo.get_task(task_id)
            self.assertEqual(task["status"], status.value)
            self.assertEqual(task["completed_at"] is not None, status == TaskStatus.COMPLETED)
        self.assertEqual(len(self.repo.get_task_history(capability="SQL")), 1)
        self.assertEqual(self.repo.get_task_history(capability="RAG"), [])

    def test_duplicate_pending_task_is_rejected(self):
        self.repo.create_task(Task("SQL", "Study SQL"))
        for duplicate in ("Study SQL", "  study   sql  ", "ＳＴＵＤＹ SQL"):
            with self.assertRaises(sqlite3.IntegrityError):
                self.repo.create_task(Task("SQL", duplicate))

    def assert_recreation_after(self, status):
        old_id = self.repo.create_task(Task("SQL", "Study SQL"))
        event_id = self.repo.append_event(Event(EventType.TASK_CREATED, "task", str(old_id)))
        self.repo.update_task_status(old_id, status)
        old = self.repo.get_task(old_id)
        new_id = self.repo.create_task(Task("SQL", "  study   sql  "))
        self.assertNotEqual(old_id, new_id)
        self.assertEqual(self.repo.get_task(old_id), old)
        self.assertEqual(self.repo.get_task(new_id)["status"], "pending")
        self.assertEqual(len(self.repo.get_task_history()), 2)
        self.assertEqual(self.repo.list_events()[0]["id"], event_id)
        with self.assertRaises(sqlite3.IntegrityError):
            self.repo.create_task(Task("SQL", "ＳＴＵＤＹ SQL"))

    def test_completed_task_allows_future_same_text(self):
        self.assert_recreation_after(TaskStatus.COMPLETED)

    def test_superseded_task_allows_future_same_text(self):
        self.assert_recreation_after(TaskStatus.SUPERSEDED)

    def test_partial_and_not_completed_allow_future_same_text(self):
        for status in (TaskStatus.PARTIAL, TaskStatus.NOT_COMPLETED):
            text = "Retry " + status.value
            old_id = self.repo.create_task(Task("SQL", text))
            self.repo.update_task_status(old_id, status)
            new_id = self.repo.create_task(Task("SQL", text))
            self.assertNotEqual(old_id, new_id)
            self.assertEqual(self.repo.get_task(old_id)["status"], status.value)

    def test_restoring_history_to_pending_obeys_duplicate_constraint(self):
        old_id = self.repo.create_task(Task("SQL", "Restore task"))
        self.repo.update_task_status(old_id, TaskStatus.COMPLETED)
        new_id = self.repo.create_task(Task("SQL", "Restore task"))
        with self.assertRaises(sqlite3.IntegrityError):
            self.repo.update_task_status(old_id, TaskStatus.PENDING)
        self.assertEqual(self.repo.get_task(old_id)["status"], "completed")
        self.assertEqual(self.repo.get_task(new_id)["status"], "pending")

    def test_migration_stays_idempotent_after_task_recreation(self):
        source = self.fixture({"completed_tasks": ["Repeat demo"]})
        migrate_json_memory(source, self.repo)
        old = self.repo.find_task_by_text("Repeat demo")
        new_id = self.repo.create_task(Task("SQL", "Repeat demo"))
        before = self.repo.list_events()
        result = migrate_json_memory(source, self.repo)
        self.assertEqual(result["tasks_created"], 0)
        self.assertEqual(result["events_appended"], 0)
        self.assertEqual(self.repo.find_task_by_text("Repeat demo")["id"], old["id"])
        self.assertEqual(self.repo.list_events(), before)
        self.assertEqual(self.repo.get_task(new_id)["status"], "pending")

    def test_event_append_filter_and_state_update(self):
        task_id = self.repo.create_task(Task("SQL", "任务"))
        first = self.repo.append_event(Event(EventType.TASK_CREATED, "task", str(task_id), {"task": "任务"}))
        with self.repo.transaction():
            self.repo.update_task_status(task_id, TaskStatus.COMPLETED)
            self.repo.append_event(Event(EventType.TASK_COMPLETED, "task", str(task_id), {"feedback": ""}))
        events = self.repo.list_events(entity_type="task", entity_id=task_id)
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["id"], first)
        self.assertEqual(len(self.repo.list_events(event_type=EventType.TASK_COMPLETED, after_id=first)), 1)
        self.assertEqual(self.repo.list_events(entity_type="jd"), [])

    def test_events_cannot_be_updated_or_deleted(self):
        self.repo.append_event(Event(EventType.PROFILE_CONFIRMED, "profile", "1"))
        for sql in ("UPDATE events SET entity_id='2'", "DELETE FROM events"):
            with self.assertRaises(sqlite3.IntegrityError):
                self.connection.execute(sql)
        self.assertEqual(len(self.repo.list_events()), 1)

    def test_transaction_rolls_back_state_and_event(self):
        task_id = self.repo.create_task(Task("SQL", "回滚测试"))
        with self.assertRaises(RuntimeError):
            with self.repo.transaction():
                self.repo.update_task_status(task_id, "completed")
                self.repo.append_event(Event(EventType.TASK_COMPLETED, "task", str(task_id)))
                raise RuntimeError("simulated failure")
        self.assertEqual(self.repo.get_task(task_id)["status"], "pending")
        self.assertEqual(self.repo.list_events(), [])

    def test_failed_event_rolls_back_state(self):
        with self.assertRaises(ValueError):
            with self.repo.transaction():
                self.repo.upsert_profile(UserProfile(education="new"))
                self.repo.append_event(Event("INVALID", "profile", "1"))
        self.assertIsNone(self.repo.get_profile())

    def test_composed_archive_add_event_transaction(self):
        old = self.repo.add_jd(TargetJD("A", "old", "old text"))
        with self.assertRaises(RuntimeError):
            with self.repo.transaction():
                self.repo.archive_jd(old)
                new = self.repo.add_jd(TargetJD("B", "new", "new text"))
                self.repo.append_event(Event(EventType.JD_REPLACED, "jd", str(new), {"old_id": old}))
                raise RuntimeError("fail")
        self.assertEqual([r["id"] for r in self.repo.get_active_jds()], [old])
        self.assertEqual(self.repo.list_events(), [])

    def test_reopen_retains_state(self):
        self.repo.upsert_profile(UserProfile(major="软件工程"))
        capability = self.repo.upsert_capability(Capability("SQL", CapabilityLevel.KNOWLEDGE))
        self.repo.add_evidence(Evidence(capability["id"], "self_report", "理解查询概念", "profile", "1"))
        self.repo.add_jd(TargetJD("公司", "岗位", "SQL"))
        task_id = self.repo.create_task(Task("SQL", "练习"))
        self.repo.append_event(Event(EventType.TASK_CREATED, "task", str(task_id)))
        self.connection.close()
        self.connection = connect_database(self.path)
        self.repo = Repository(self.connection)
        self.repo.initialize()
        self.assertEqual(self.repo.get_profile()["major"], "软件工程")
        self.assertEqual(len(self.repo.get_evidence(capability["id"])), 1)
        self.assertEqual(len(self.repo.get_active_jds()), 1)
        self.assertIsNotNone(self.repo.get_task(task_id))
        self.assertEqual(len(self.repo.list_events()), 1)

    def test_snapshot_and_summary(self):
        snapshot_id = self.repo.create_snapshot(PlanningSnapshot("test", [], [], [], None, "storage test"))
        event_id = self.repo.append_event(Event(EventType.REPLAN, "snapshot", str(snapshot_id)))
        self.assertIsNone(self.repo.get_snapshot(snapshot_id)["selected_task_json"])
        self.assertEqual(self.repo.list_snapshots()[0]["id"], snapshot_id)
        self.repo.upsert_summary(MemorySummary("SQL", "first", event_id))
        self.repo.upsert_summary(MemorySummary("SQL", "second", event_id))
        self.assertEqual(self.repo.get_summary("SQL")["summary"], "second")
        self.assertEqual(self.repo.get_summary("SQL")["covered_until_event_id"], event_id)
        self.assertIsNone(self.repo.get_summary("RAG"))

    def test_migration_repeatable_and_source_unchanged(self):
        source = self.fixture({"gaps": ["SQL"], "skills": ["SQL"],
            "completed_tasks": ["完成任务"], "pending_tasks": ["待做任务"],
            "task_history": [{"task": "完成任务", "status": "partial", "feedback": "缺一部分"},
                             {"task": "完成任务", "status": "completed", "feedback": "做好了"}]})
        before = source.read_bytes()
        first = migrate_json_memory(source, self.repo)
        tasks = self.repo.get_task_history()
        events = self.repo.list_events()
        second = migrate_json_memory(source, self.repo)
        self.assertEqual(first["tasks_created"], 2)
        self.assertEqual(len(self.repo.list_events(event_type="TASK_COMPLETED")), 1)
        self.assertEqual(second["tasks_created"], 0)
        self.assertEqual(second["events_appended"], 0)
        self.assertEqual(tasks, self.repo.get_task_history())
        self.assertEqual(events, self.repo.list_events())
        self.assertEqual(source.read_bytes(), before)
        self.assertTrue(all(t["created_at"] is None and t["completed_at"] is None for t in tasks))
        self.assertEqual(self.repo.get_capabilities(), [])
        self.assertEqual(self.repo.list_snapshots(), [])
        self.assertTrue(all(e["payload_json"]["migration"]["time_status"] == "unknown" for e in events))

    def test_migration_preserves_identical_history_occurrences(self):
        observation = {"task": "卡点", "status": "partial", "feedback": "未完成后半段"}
        source = self.fixture({"task_history": [observation, observation]})
        migrate_json_memory(source, self.repo)
        self.assertEqual(len(self.repo.list_events(event_type="TASK_PARTIAL")), 2)
        self.assertEqual(migrate_json_memory(source, self.repo)["events_appended"], 0)

    def test_migration_conflict_and_unknown_feedback(self):
        source = self.fixture({"completed_tasks": ["冲突任务"], "pending_tasks": ["冲突任务"],
                               "task_history": [{"task": "历史任务", "status": "partial"}]})
        migrate_json_memory(source, self.repo)
        self.assertEqual(self.repo.find_task_by_text("冲突任务")["status"], "pending")
        self.assertTrue(any(e["payload_json"]["migration"]["status_conflict"] for e in self.repo.list_events()))
        event = self.repo.list_events(event_type="TASK_PARTIAL")[0]
        self.assertIsNone(event["payload_json"]["feedback"])
        self.assertEqual(event["payload_json"]["migration"]["feedback_status"], "unknown")

    def test_migration_does_not_rewind_current_task(self):
        source = self.fixture({"pending_tasks": ["练习 SQL"]})
        migrate_json_memory(source, self.repo)
        task = self.repo.find_task_by_text("练习 SQL")
        self.repo.update_task_status(task["id"], "completed")
        migrate_json_memory(source, self.repo)
        self.assertEqual(self.repo.get_task(task["id"])["status"], "completed")

    def test_migration_failure_is_atomic(self):
        source = self.fixture({"pending_tasks": ["迁移任务"]})
        with patch.object(self.repo, "append_event", side_effect=RuntimeError("fail")):
            with self.assertRaises(RuntimeError):
                migrate_json_memory(source, self.repo)
        self.assertEqual(self.repo.get_task_history(), [])
        self.assertEqual(self.repo.list_events(), [])

    def test_migration_reports_unrecognized_records(self):
        source = self.fixture({"task_history": [{"task": "bad", "status": {"bad": 1}}]})
        result = migrate_json_memory(source, self.repo)
        self.assertEqual(len(result["skipped"]), 1)
        self.assertEqual(self.repo.get_task_history(), [])

    def test_invalid_migration_and_missing_entities(self):
        source = self.fixture({"task_history": "wrong"})
        with self.assertRaises(ValueError):
            migrate_json_memory(source, self.repo)
        self.assertEqual(self.repo.get_task_history(), [])
        with self.assertRaises(KeyError):
            self.repo.archive_jd(123)
        with self.assertRaises(KeyError):
            self.repo.update_task_status(123, "partial")


if __name__ == "__main__":
    unittest.main()
