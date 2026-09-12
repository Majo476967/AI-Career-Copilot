import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from core.errors import BusinessError, AnalysisError
from core.schemas import Capability, Evidence, Event, EventType, Task, UserProfile
from services.jd_service import JDService
from storage.database import connect_database
from storage.repository import Repository
from tests.phase2_fixtures import jd_input, jd_output, docx_bytes


class JDServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.connection = connect_database(Path(self.temp.name) / "test.sqlite3")
        self.addCleanup(self.connection.close)
        self.repo = Repository(self.connection)
        self.repo.initialize()
        self.service = JDService(self.repo)
        response = patch("llm.request_analysis")
        self.model = response.start()
        self.addCleanup(response.stop)

    def add(self, index=1):
        self.model.return_value = json.dumps(jd_output(index), ensure_ascii=False)
        return self.service.add_jd(jd_input(index))

    def test_four_plus_active_jds(self):
        for i in range(5):
            self.add(i)
        self.assertEqual(len(self.service.list_active_jds()), 5)
        self.assertEqual(len(self.repo.list_events(event_type="JD_ADDED")), 5)

    def test_archive_preserves_record_and_is_idempotent(self):
        jd = self.add()
        first = self.service.archive_jd(jd["id"])
        self.assertEqual(self.service.list_active_jds(), [])
        self.assertEqual(self.service.list_archived_jds()[0]["jd_text"], jd["jd_text"])
        self.assertEqual(self.service.archive_jd(jd["id"]), first)
        self.assertEqual(len(self.repo.list_events(event_type="JD_ARCHIVED")), 1)

    def test_replace_old_archived_new_active_and_event(self):
        old = self.add()
        self.model.return_value = json.dumps(jd_output(2), ensure_ascii=False)
        new = self.service.replace_jd(old["id"], jd_input(2))
        self.assertEqual(self.service.get_jd(old["id"])["status"], "archived")
        self.assertEqual(new["status"], "active")
        self.assertNotEqual(new["id"], old["id"])
        event = self.repo.list_events(event_type="JD_REPLACED")[0]
        self.assertEqual(event["payload_json"]["old_jd_id"], old["id"])
        self.assertEqual(event["payload_json"]["new_jd_id"], new["id"])
        self.assertTrue(event["payload_json"]["planning_required"])
        self.assertEqual(self.repo.list_snapshots(), [])

    def test_replace_preserves_user_tasks_evidence_and_history(self):
        self.repo.upsert_profile(UserProfile(education="original"))
        cap = self.repo.upsert_capability(Capability("SQL", 1))
        self.repo.add_evidence(Evidence(cap["id"], "skill", "SQL evidence", "resume", "v1"))
        task_id = self.repo.create_task(Task("SQL", "Existing task"))
        self.repo.append_event(Event(EventType.TASK_CREATED, "task", str(task_id)))
        old = self.add()
        before = (self.repo.get_profile(), self.repo.get_capabilities(), self.repo.get_evidence(cap["id"]),
                  self.repo.get_task_history(), self.repo.list_events())
        self.model.return_value = json.dumps(jd_output(2), ensure_ascii=False)
        self.service.replace_jd(old["id"], jd_input(2))
        after = (self.repo.get_profile(), self.repo.get_capabilities(), self.repo.get_evidence(cap["id"]),
                 self.repo.get_task_history(), self.repo.list_events()[:-1])
        self.assertEqual(before, after)

    def test_aggregation_facts_only_and_archived_excluded(self):
        first = self.add(1)
        second = self.add(2)
        summary = self.service.get_active_jd_capability_summary()
        self.assertEqual(summary["SQL"], {"jd_ids": [first["id"], second["id"]], "count": 2,
            "importance": ["must_have", "must_have"], "required_levels": [2, 2]})
        self.assertEqual(set(summary["SQL"]), {"jd_ids", "count", "importance", "required_levels"})
        self.service.archive_jd(first["id"])
        self.assertEqual(self.service.get_active_jd_capability_summary()["SQL"]["jd_ids"], [second["id"]])

    def test_duplicate_capabilities_not_double_counted(self):
        data = jd_output()
        data["capabilities"].append({"name": "数据库查询", "category": "technical", "importance": "important",
                                     "required_level": 3, "evidence": "数据库查询练习"})
        self.model.return_value = json.dumps(data, ensure_ascii=False)
        self.service.add_jd(jd_input())
        self.assertEqual(self.service.get_active_jd_capability_summary()["SQL"]["count"], 1)

    def test_duplicate_jd_is_readable_and_no_write(self):
        old = self.add()
        calls = self.model.call_count
        with self.assertRaises(BusinessError) as caught:
            self.service.add_jd("  " + jd_input() + "  ")
        self.assertEqual(caught.exception.code, "duplicate_jd")
        self.assertEqual(self.model.call_count, calls)
        self.service.archive_jd(old["id"])
        with self.assertRaises(BusinessError):
            self.service.add_jd(jd_input())
        self.assertEqual(len(self.repo.list_jds()), 1)

    def test_company_and_title_can_be_corrected(self):
        self.model.return_value = json.dumps(jd_output(), ensure_ascii=False)
        jd = self.service.add_jd(jd_input(), company="人工修正公司", job_title="人工修正岗位")
        self.assertEqual(jd["company"], "人工修正公司")
        self.assertEqual(jd["jd_analysis_json"]["job_title"], "人工修正岗位")

    def test_jd_file_input(self):
        self.model.return_value = json.dumps(jd_output(), ensure_ascii=False)
        jd = self.service.add_jd(file=docx_bytes(jd_input()), filename="job.docx")
        self.assertEqual(jd["jd_text"], jd_input())

    def test_replace_missing_or_archived(self):
        with self.assertRaises(BusinessError) as caught:
            self.service.replace_jd(999, jd_input(2))
        self.assertEqual(caught.exception.code, "jd_missing")
        old = self.add()
        self.service.archive_jd(old["id"])
        with self.assertRaises(BusinessError):
            self.service.replace_jd(old["id"], jd_input(2))

    def test_replace_failure_rolls_back_all_jd_changes(self):
        old = self.add()
        events = self.repo.list_events()
        self.model.return_value = json.dumps(jd_output(2), ensure_ascii=False)
        with patch.object(self.repo, "append_event", side_effect=sqlite3.OperationalError("fail")):
            with self.assertRaises(BusinessError):
                self.service.replace_jd(old["id"], jd_input(2))
        self.assertEqual(self.service.list_active_jds(), [old])
        self.assertEqual(self.service.list_archived_jds(), [])
        self.assertEqual(self.repo.list_events(), events)

    def test_analysis_failure_leaves_old_jd_active(self):
        old = self.add()
        self.model.return_value = "invalid JSON"
        with self.assertRaises(AnalysisError):
            self.service.replace_jd(old["id"], jd_input(2))
        self.assertEqual(self.service.list_active_jds(), [old])

    def test_empty_or_ambiguous_input(self):
        for options in ({}, {"text": ""}, {"text": jd_input(), "file": b"file"}):
            with self.assertRaises(BusinessError):
                self.service.add_jd(**options)
        self.model.assert_not_called()
        self.assertEqual(self.repo.list_jds(), [])

    def test_empty_aggregation(self):
        self.assertEqual(self.service.get_active_jd_capability_summary(), {})
