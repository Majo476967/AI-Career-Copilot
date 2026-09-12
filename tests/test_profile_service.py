import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from core.errors import BusinessError, AnalysisError
from core.schemas import UserProfile
from services.profile_service import ProfileService
from storage.database import connect_database
from storage.repository import Repository
from tests.phase2_fixtures import docx_bytes, profile, RESUME


class ProfileServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "test.sqlite3"
        self.connection = connect_database(self.path)
        self.addCleanup(lambda: self.connection.close())
        self.repo = Repository(self.connection)
        self.repo.initialize()
        self.service = ProfileService(self.repo)
        response = patch("llm.request_analysis", return_value=json.dumps(profile(), ensure_ascii=False))
        self.model = response.start()
        self.addCleanup(response.stop)

    def draft(self):
        return self.service.create_profile_draft(docx_bytes(), filename="resume.docx")

    def test_draft_does_not_overwrite_current(self):
        self.repo.upsert_profile(UserProfile(education="Original"))
        before = self.repo.get_profile()
        draft = self.draft()
        self.assertEqual(self.repo.get_profile(), before)
        self.assertEqual(draft["status"], "draft")
        self.assertEqual(self.repo.get_capabilities(), [])
        self.assertEqual(self.repo.list_events(), [])

    def test_confirm_profile_evidence_and_event(self):
        draft = self.draft()
        result = self.service.confirm_profile(draft["id"])
        self.assertEqual(result["profile_id"], 1)
        self.assertEqual(self.repo.get_profile()["resume_text"], RESUME)
        self.assertEqual(self.repo.get_profile()["profile_json"]["projects"], profile()["projects"])
        capability = self.repo.get_capability("SQL")
        self.assertEqual(capability["level"], 2)
        evidence = self.repo.get_evidence(capability["id"])
        self.assertEqual(len(evidence), 1)
        self.assertEqual(evidence[0]["source"], "resume")
        self.assertEqual(evidence[0]["source_id"], draft["resume_version"])
        self.assertTrue(evidence[0]["created_at"])
        self.assertEqual(len(self.repo.list_events(event_type="PROFILE_CONFIRMED")), 1)
        self.assertEqual(self.repo.list_snapshots(), [])
        self.assertEqual(self.repo.get_task_history(), [])

    def test_repeat_confirmation_is_noop(self):
        draft = self.draft()
        first = self.service.confirm_profile(draft["id"])
        current = self.repo.get_profile()
        self.assertEqual(first, self.service.confirm_profile(draft["id"]))
        self.assertEqual(current, self.repo.get_profile())
        self.assertEqual(len(self.repo.list_events()), 1)
        self.assertEqual(len(self.repo.get_evidence(self.repo.get_capability("SQL")["id"])), 1)

    def test_same_resume_new_draft_does_not_duplicate_evidence(self):
        self.service.confirm_profile(self.draft()["id"])
        self.service.confirm_profile(self.draft()["id"])
        self.assertEqual(len(self.repo.get_evidence(self.repo.get_capability("SQL")["id"])), 1)
        self.assertEqual(len(self.repo.list_events()), 2)

    def test_draft_edits_require_confirmation(self):
        draft = self.draft()
        updated = self.service.update_profile_draft(draft["id"], {
            "major": "人工确认专业", "available_hours_per_day": 3, "education": ["人工修正的学历"]})
        self.assertEqual(updated["draft_json"]["major"], "人工确认专业")
        self.assertIsNone(self.repo.get_profile())
        self.service.confirm_profile(draft["id"])
        self.assertEqual(self.repo.get_profile()["major"], "人工确认专业")
        self.assertEqual(self.repo.get_profile()["available_hours_per_day"], 3)

    def test_discard_draft(self):
        draft = self.draft()
        self.assertEqual(self.service.discard_profile_draft(draft["id"])["status"], "discarded")
        self.assertEqual(self.service.discard_profile_draft(draft["id"])["status"], "discarded")
        with self.assertRaises(BusinessError):
            self.service.confirm_profile(draft["id"])
        self.assertIsNone(self.repo.get_profile())

    def test_confirmed_draft_not_editable(self):
        draft = self.draft()
        self.service.confirm_profile(draft["id"])
        with self.assertRaises(BusinessError):
            self.service.update_profile_draft(draft["id"], {"major": "new"})
        with self.assertRaises(BusinessError):
            self.service.discard_profile_draft(draft["id"])

    def test_invalid_draft_edit_does_not_mutate(self):
        draft = self.draft()
        for changes in ({"available_hours_per_day": 25}, {"status": "confirmed"}):
            with self.assertRaises(BusinessError):
                self.service.update_profile_draft(draft["id"], changes)
        self.assertEqual(self.service.get_profile_draft(draft["id"]), draft)

    def test_confirm_rollback_on_event_failure(self):
        self.repo.upsert_profile(UserProfile(education="Original"))
        before = self.repo.get_profile()
        draft = self.draft()
        with patch.object(self.repo, "append_event", side_effect=sqlite3.OperationalError("failure")):
            with self.assertRaises(BusinessError):
                self.service.confirm_profile(draft["id"])
        self.assertEqual(self.repo.get_profile(), before)
        self.assertEqual(self.repo.get_capabilities(), [])
        self.assertEqual(self.repo.list_events(), [])
        self.assertEqual(self.service.get_profile_draft(draft["id"])["status"], "draft")
        self.assertEqual(self.connection.execute("SELECT count(*) FROM capability_evidence").fetchone()[0], 0)

    def test_missing_draft(self):
        with self.assertRaises(BusinessError) as caught:
            self.service.confirm_profile(1234)
        self.assertEqual(caught.exception.code, "draft_missing")

    def test_analysis_failure_creates_no_draft(self):
        self.model.return_value = "invalid"
        with self.assertRaises(AnalysisError):
            self.draft()
        self.assertEqual(self.connection.execute("SELECT count(*) FROM profile_drafts").fetchone()[0], 0)

    def test_draft_survives_restart(self):
        draft = self.draft()
        self.connection.close()
        self.connection = connect_database(self.path)
        self.repo = Repository(self.connection)
        self.service = ProfileService(self.repo)
        self.assertEqual(self.service.get_profile_draft(draft["id"])["status"], "draft")
        self.service.confirm_profile(draft["id"])
        self.assertIsNotNone(self.repo.get_profile())

    def test_reconfirm_old_draft_does_not_revert_new_profile(self):
        old = self.draft()
        self.service.confirm_profile(old["id"])
        new = self.draft()
        self.service.update_profile_draft(new["id"], {"major": "New major"})
        self.service.confirm_profile(new["id"])
        self.service.confirm_profile(old["id"])
        self.assertEqual(self.repo.get_profile()["major"], "New major")
