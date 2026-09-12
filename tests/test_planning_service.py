import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.errors import BusinessError
from core.router import EventRouter
from core.schemas import Capability, Evidence, Event, EventType, TargetJD, UserProfile
from services.jd_service import JDService
from services.planning_service import PlanningService
from services.profile_service import ProfileService
from storage.database import connect_database
from storage.repository import Repository
from tests.phase2_fixtures import docx_bytes, jd_input, jd_output, profile
from tests.phase3_fixtures import requirement


class PlanningServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "phase3.sqlite3"
        self.connection = connect_database(self.path)
        self.addCleanup(lambda: self.connection.close())
        self.repo = Repository(self.connection)
        self.repo.initialize()
        self.planning = PlanningService(self.repo)
        self.router = EventRouter(self.planning)
        blocker = patch("llm.request_analysis", side_effect=AssertionError("Real LLM forbidden"))
        self.model = blocker.start()
        self.addCleanup(blocker.stop)

    def seed(self, *, level=1, evidence=True):
        self.repo.upsert_profile(UserProfile(education="Synthetic academy"))
        cap = self.repo.upsert_capability(Capability("SQL", level))
        if evidence:
            self.repo.add_evidence(Evidence(cap["id"], "skill", "Synthetic knowledge evidence", "test", "fixture"))
        return self.repo.add_jd(TargetJD("Fictional", "Synthetic role", "Synthetic requirement",
                                        {"capabilities": [requirement()]}))

    def jd_service(self):
        return JDService(self.repo, event_router=self.router)

    def mock_analysis(self, data):
        self.model.side_effect = None
        self.model.return_value = json.dumps(data, ensure_ascii=False)

    def test_ranked_output(self):
        self.seed()
        result = self.planning.recompute()
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["ranked_priorities"][0]["capability"], "SQL")
        self.model.assert_not_called()

    def test_snapshot_contents_and_no_selected_task(self):
        jd_id = self.seed()
        result = self.planning.recompute("JD_ADDED")
        snapshot = self.repo.get_snapshot(result["snapshot_id"])
        self.assertEqual(snapshot["trigger"], "JD_ADDED")
        self.assertEqual(snapshot["active_jds_json"][0]["id"], jd_id)
        self.assertEqual(snapshot["capability_state_json"][0]["evidence"][0]["source_id"], "fixture")
        self.assertEqual(snapshot["priority_result_json"], {k: v for k, v in result.items() if k != "snapshot_id"})
        self.assertIsNone(snapshot["selected_task_json"])
        self.assertTrue(snapshot["reason"])
        self.assertTrue(snapshot["created_at"])
        self.assertEqual(self.repo.get_task_history(), [])

    def test_snapshot_survives_reopen(self):
        self.seed()
        result = self.planning.recompute()
        snapshot = self.repo.get_snapshot(result["snapshot_id"])
        self.connection.close()
        self.connection = connect_database(self.path)
        self.repo = Repository(self.connection)
        self.assertEqual(self.repo.get_snapshot(result["snapshot_id"]), snapshot)

    def test_missing_confirmed_profile(self):
        result = self.planning.recompute()
        self.assertEqual(result["status"], "no_confirmed_profile")
        self.assertIsNone(result["top_priority"])
        self.assertIsNotNone(result["snapshot_id"])

    def test_draft_is_not_confirmed_state(self):
        self.repo.create_profile_draft("Synthetic", "synthetic-version", profile())
        self.assertEqual(self.planning.recompute()["status"], "no_confirmed_profile")
        self.assertIsNone(self.repo.get_profile())

    def test_confirmed_profile_without_active_jds(self):
        self.repo.upsert_profile(UserProfile())
        self.assertEqual(self.planning.recompute()["status"], "no_active_jd")

    def test_no_evidence_returns_warning_without_changing_level(self):
        self.seed(evidence=False)
        result = self.planning.recompute()
        self.assertTrue(result["warnings"])
        self.assertEqual(self.repo.get_capability("SQL")["level"], 1)

    def test_no_capabilities_uses_evidence_gap(self):
        self.repo.upsert_profile(UserProfile())
        self.repo.add_jd(TargetJD("Fictional", "Role", "Synthetic", {"capabilities": [requirement()]}))
        result = self.planning.recompute()
        self.assertTrue(result["top_priority"]["evidence_gap"])
        self.assertTrue(result["warnings"])
        self.assertEqual(self.repo.get_capabilities(), [])

    def test_invalid_stored_requirement_has_no_snapshot(self):
        self.repo.upsert_profile(UserProfile())
        self.repo.add_jd(TargetJD("Fictional", "Role", "Synthetic", {}))
        result = self.planning.recompute()
        self.assertEqual(result["status"], "invalid_input")
        self.assertIsNone(result["snapshot_id"])
        self.assertEqual(self.repo.list_snapshots(), [])

    def test_invalid_trigger(self):
        self.assertEqual(self.planning.recompute(None)["status"], "invalid_input")
        self.assertEqual(self.repo.list_snapshots(), [])

    def test_state_jds_and_event_history_unchanged(self):
        self.seed()
        self.repo.append_event(Event(EventType.PROFILE_CONFIRMED, "profile", "1"))
        def state():
            return (self.repo.get_profile(), self.repo.get_capabilities(),
                    [dict(r) for r in self.connection.execute("SELECT * FROM capability_evidence")],
                    self.repo.list_jds(), self.repo.list_events(), self.repo.get_task_history())
        before = state()
        self.planning.recompute()
        self.assertEqual(state(), before)
        self.assertEqual(len(self.repo.list_snapshots()), 1)

    def test_router_profile_confirmed(self):
        self.seed()
        self.assertEqual(self.router.dispatch(EventType.PROFILE_CONFIRMED)["status"], "ok")
        self.assertEqual(self.repo.list_snapshots()[0]["trigger"], "PROFILE_CONFIRMED")

    def test_router_jd_added(self):
        self.seed()
        self.router.dispatch("JD_ADDED")
        self.assertEqual(self.repo.list_snapshots()[0]["trigger"], "JD_ADDED")

    def test_router_jd_archived(self):
        jd_id = self.seed()
        self.repo.archive_jd(jd_id)
        result = self.router.dispatch("JD_ARCHIVED")
        self.assertEqual(result["status"], "no_active_jd")
        self.assertEqual(self.repo.list_snapshots()[0]["trigger"], "JD_ARCHIVED")

    def test_router_jd_replaced(self):
        self.seed()
        self.router.dispatch("JD_REPLACED")
        self.assertEqual(self.repo.list_snapshots()[0]["trigger"], "JD_REPLACED")

    def test_non_planning_events_are_ignored(self):
        for event in ("TASK_CREATED", "TASK_COMPLETED", "TASK_PARTIAL", "TASK_NOT_COMPLETED", "REPLAN", "UNKNOWN", None, {}):
            with self.subTest(event=event):
                self.assertEqual(self.router.dispatch(event)["status"], "ignored")
        self.assertEqual(self.repo.list_snapshots(), [])
        self.model.assert_not_called()

    def test_profile_confirmation_hook_and_repeat_noop(self):
        self.mock_analysis(profile())
        service = ProfileService(self.repo, event_router=self.router)
        draft = service.create_profile_draft(docx_bytes(), filename="synthetic.docx")
        self.assertEqual(self.repo.list_snapshots(), [])
        service.confirm_profile(draft["id"])
        service.confirm_profile(draft["id"])
        self.assertEqual(len(self.repo.list_snapshots()), 1)
        snapshot = self.repo.list_snapshots()[0]
        self.assertEqual(snapshot["trigger"], "PROFILE_CONFIRMED")
        self.assertEqual(snapshot["capability_state_json"][0]["level"], 2)
        self.assertEqual(len(self.repo.list_events()), 1)

    def test_jd_add_archive_replace_hooks(self):
        self.repo.upsert_profile(UserProfile())
        service = self.jd_service()
        self.mock_analysis(jd_output(1))
        old = service.add_jd(jd_input(1))
        self.mock_analysis(jd_output(2))
        new = service.replace_jd(old["id"], jd_input(2))
        replaced = self.repo.list_snapshots()[0]
        self.assertEqual([r["id"] for r in replaced["active_jds_json"]], [new["id"]])
        service.archive_jd(new["id"])
        service.archive_jd(new["id"])
        self.assertEqual([r["trigger"] for r in reversed(self.repo.list_snapshots())],
                         ["JD_ADDED", "JD_REPLACED", "JD_ARCHIVED"])
        self.assertEqual([r["event_type"] for r in self.repo.list_events()],
                         ["JD_ADDED", "JD_REPLACED", "JD_ARCHIVED"])
        self.assertEqual(self.repo.get_task_history(), [])

    def test_snapshot_failure_rolls_back_jd_and_event(self):
        self.repo.upsert_profile(UserProfile())
        self.mock_analysis(jd_output())
        with patch.object(self.repo, "create_snapshot", side_effect=sqlite3.OperationalError("synthetic failure")):
            with self.assertRaises(BusinessError) as caught:
                self.jd_service().add_jd(jd_input())
        self.assertEqual(caught.exception.code, "storage_error")
        self.assertEqual(self.repo.list_jds(), [])
        self.assertEqual(self.repo.list_events(), [])
        self.assertEqual(self.repo.list_snapshots(), [])

    def test_snapshot_failure_rolls_back_confirmation(self):
        self.mock_analysis(profile())
        service = ProfileService(self.repo, event_router=self.router)
        draft = service.create_profile_draft(docx_bytes(), filename="synthetic.docx")
        with patch.object(self.repo, "create_snapshot", side_effect=sqlite3.OperationalError("synthetic failure")):
            with self.assertRaises(BusinessError):
                service.confirm_profile(draft["id"])
        self.assertIsNone(self.repo.get_profile())
        self.assertEqual(self.repo.get_capabilities(), [])
        self.assertEqual(self.repo.list_events(), [])
        self.assertEqual(self.repo.get_profile_draft(draft["id"])["status"], "draft")

    def test_formal_jd_service_aggregation(self):
        jd_id = self.seed()
        result = self.jd_service().get_active_jd_requirements()
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["requirements"][0]["jd_ids"], [jd_id])
        self.model.assert_not_called()
