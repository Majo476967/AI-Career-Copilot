"""BC-PROFILE-003: explicit recovery; only temporary databases and Fake LLM."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from core.errors import AnalysisError, BusinessError
from services.profile_service import ProfileService
from storage.database import connect_database
from storage.repository import Repository
from tests.phase2_fixtures import docx_bytes
from tests.test_profile_completeness_reason import draft as fake_profile

SOURCE = "了解 SQL 基础、Python 基础及数据分析概念。"


class ProfileRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.conn = connect_database(Path(self.temp.name) / "recovery.sqlite3"); self.addCleanup(self.conn.close)
        self.repo = Repository(self.conn); self.repo.initialize()
        self.service = ProfileService(self.repo)
        p = patch("llm.request_analysis", return_value=json.dumps(fake_profile(SOURCE, ["SQL", "Data Analysis"])))
        self.request = p.start(); self.addCleanup(p.stop)

    def create(self):
        return self.service.create_profile_draft(docx_bytes(SOURCE), filename="fiction.docx")

    def add(self, item, value=1):
        return self.service.resolve_missing_capability(item["id"], "Programming", "add", level=value, evidence_snippet=SOURCE)

    def test_partial_output_persisted_with_missing_details(self):
        item = self.create(); data = item["draft_json"]
        self.assertEqual(data["validation_status"], "incomplete")
        self.assertEqual(len(data["capabilities"]), 2)
        self.assertEqual(data["missing_capabilities"], [{"canonical_name": "Programming", "matched_resume_terms": ["Python"], "evidence_snippets": [SOURCE]}])
        self.assertIsNone(self.repo.get_profile())
        self.assertEqual(self.repo.get_capabilities(), [])
        self.request.assert_called_once()

    def test_incomplete_confirm_blocked_even_with_forged_valid_flag(self):
        item = self.create(); data = item["draft_json"]
        data.update(validation_status="valid", missing_capabilities=[])
        self.repo.update_profile_draft(item["id"], data)
        with self.assertRaises(AnalysisError): self.service.confirm_profile(item["id"])
        self.assertEqual(self.repo.list_events(), [])
        self.assertIsNone(self.repo.get_profile())

    def test_add_revalidates_and_preserves_user_evidence_on_confirm(self):
        item = self.add(self.create()); data = item["draft_json"]
        self.assertEqual(data["validation_status"], "valid")
        self.assertEqual(data["missing_capabilities"], [])
        self.assertIsNone(self.repo.get_profile())
        self.service.confirm_profile(item["id"])
        cap = self.repo.get_capability("Programming")
        self.assertEqual(cap["level"], 1)
        evidence = self.repo.get_evidence(cap["id"])[0]
        self.assertEqual(evidence["source"], "resume")
        self.assertEqual(evidence["evidence_type"], "user_confirmed_resume_evidence")
        self.assertEqual(evidence["content"], SOURCE)
        self.assertTrue(evidence["created_at"])
        self.request.assert_called_once()

    def test_level_must_be_explicit(self):
        item = self.create()
        for value in [None, True, "1", -1, 5]:
            with self.subTest(value=value), self.assertRaises(BusinessError): self.add(item, value)
        self.assertEqual(self.service.get_profile_draft(item["id"]), item)

    def test_user_selected_zero_not_upgraded(self):
        item = self.add(self.create(), 0)
        cap = next(c for c in item["draft_json"]["capabilities"] if c["name"] == "Programming")
        self.assertEqual(cap["level"], 0)

    def test_ignore_unlocks_confirm_without_adding_capability(self):
        item = self.create()
        result = self.service.resolve_missing_capability(item["id"], "Programming", "ignore")
        self.assertEqual(result["draft_json"]["ignored_missing_capabilities"], ["Programming"])
        self.assertEqual(result["draft_json"]["validation_status"], "valid")
        self.service.confirm_profile(item["id"])
        self.assertIsNone(self.repo.get_capability("Programming"))
        self.request.assert_called_once()

    def test_ignore_does_not_leak_to_new_draft(self):
        item = self.create()
        self.service.resolve_missing_capability(item["id"], "Programming", "ignore")
        new = self.create()["draft_json"]
        self.assertEqual(new["validation_status"], "incomplete")
        self.assertEqual(new["ignored_missing_capabilities"], [])

    def test_llm_cannot_supply_ignore_override(self):
        output = fake_profile(SOURCE, ["SQL", "Data Analysis"])
        output["ignored_missing_capabilities"] = ["Programming"]
        output["validation_status"] = "valid"
        self.request.return_value = json.dumps(output)
        self.assertEqual(self.create()["draft_json"]["validation_status"], "incomplete")

    def test_fabricated_candidate_evidence_rejected(self):
        item = self.create()
        with self.assertRaises(BusinessError):
            self.service.resolve_missing_capability(item["id"], "Programming", "add", level=1, evidence_snippet="invented")
        self.assertEqual(self.service.get_profile_draft(item["id"]), item)

    def test_ignore_not_allowed_through_generic_update(self):
        item = self.create()
        with self.assertRaises(BusinessError):
            self.service.update_profile_draft(item["id"], {"ignored_missing_capabilities": ["Programming"]})

    def test_duplicate_action_and_closed_draft_rejected(self):
        item = self.create(); self.add(item)
        with self.assertRaises(BusinessError): self.add(item)
        self.service.confirm_profile(item["id"])
        with self.assertRaises(BusinessError): self.service.resolve_missing_capability(item["id"], "Programming", "ignore")

    def test_structural_or_fabricated_analysis_not_saved(self):
        output = fake_profile(SOURCE, ["SQL"])
        output["capabilities"][0]["evidence"][0]["content"] = "invented"
        self.request.return_value = json.dumps(output)
        with self.assertRaises(AnalysisError): self.create()
        self.assertEqual(self.repo.open_profile_drafts(), [])

    def test_valid_draft_original_flow(self):
        self.request.return_value = json.dumps(fake_profile(SOURCE, ["SQL", "Programming", "Data Analysis"]))
        item = self.create()
        self.assertEqual(item["draft_json"]["validation_status"], "valid")
        self.service.confirm_profile(item["id"])
        self.assertEqual(self.repo.get_capability("Programming")["level"], 1)

    def test_multiple_missing_requires_each_decision(self):
        self.request.return_value = json.dumps(fake_profile(SOURCE, ["SQL"]))
        item = self.create(); updated = self.add(item)
        self.assertEqual(updated["draft_json"]["validation_status"], "incomplete")
        with self.assertRaises(AnalysisError): self.service.confirm_profile(item["id"])
        result = self.service.resolve_missing_capability(item["id"], "Data Analysis", "ignore")
        self.assertEqual(result["draft_json"]["validation_status"], "valid")


class ProfileRecoveryUITests(unittest.TestCase):
    setUp = ProfileRecoveryTests.setUp
    create = ProfileRecoveryTests.create

    def app(self):
        from streamlit.testing.v1 import AppTest
        setting = patch.dict("os.environ", {"CAREER_COPILOT_DB": str(Path(self.temp.name) / "recovery.sqlite3")})
        setting.start(); self.addCleanup(setting.stop)
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30).run()
        return app.sidebar.radio[0].set_value("我的档案").run()

    def test_ui_add_requires_level_and_unlocks_confirmation(self):
        item = self.create(); app = self.app()
        self.assertFalse(app.exception)
        button = next(b for b in app.button if b.label == "确认并更新正式档案")
        self.assertTrue(button.disabled)
        choice = next(s for s in app.selectbox if s.label == "选择能力等级")
        self.assertIsNone(choice.value)
        next(b for b in app.button if b.label == "添加到草稿").click().run()
        self.assertTrue(app.error)
        next(s for s in app.selectbox if s.label == "选择能力等级").set_value(1)
        next(b for b in app.button if b.label == "添加到草稿").click().run()
        self.assertFalse(app.exception)
        self.assertFalse(app.error)
        self.assertFalse(next(b for b in app.button if b.label == "确认并更新正式档案").disabled)
        self.assertEqual(self.repo.get_profile_draft(item["id"])["draft_json"]["validation_status"], "valid")
        self.assertIsNone(self.repo.get_profile())
        self.request.assert_called_once()

    def test_ui_ignore_unlocks_without_capability(self):
        item = self.create(); app = self.app()
        next(b for b in app.button if b.label == "不纳入").click().run()
        self.assertFalse(app.exception)
        self.assertFalse(app.error)
        self.assertFalse(next(b for b in app.button if b.label == "确认并更新正式档案").disabled)
        data = self.repo.get_profile_draft(item["id"])["draft_json"]
        self.assertEqual(data["ignored_missing_capabilities"], ["Programming"])
        self.assertNotIn("Programming", [c["name"] for c in data["capabilities"]])
        self.request.assert_called_once()
