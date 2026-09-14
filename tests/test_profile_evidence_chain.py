"""BC-PROFILE-001: temporary SQLite and Fake LLM only."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from core.errors import AnalysisError
from core.schemas import TargetJD
from services.profile_service import ProfileService
from services.planning_service import PlanningService
from storage.database import connect_database
from storage.repository import Repository
from tools.user_analyzer import analyze_resume
from tools.analysis_validation import validate_profile
from tests.phase2_fixtures import docx_bytes
from tests.phase3_fixtures import requirement


class ProfileEvidenceChainTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.conn = connect_database(Path(self.temp.name) / "test.sqlite3")
        self.addCleanup(self.conn.close)
        self.repo = Repository(self.conn)
        self.repo.initialize()
        self.service = ProfileService(self.repo)
        self.mock = patch("llm.request_analysis", side_effect=AssertionError("Real API forbidden"))
        self.request = self.mock.start()
        self.addCleanup(self.mock.stop)

    def output(self, source, name="SQL基础", level=1):
        return {"education": [], "internships": [], "projects": [], "skills": [source],
                "capabilities": [{"name": name, "level": level, "evidence": [
                    {"evidence_type": "skill", "content": source, "source": "resume"}]}]}

    def draft(self, source, name="SQL基础", level=1):
        self.request.side_effect = None
        self.request.return_value = json.dumps(self.output(source, name, level))
        return self.service.create_profile_draft(docx_bytes(source), filename="fiction.docx")

    def test_basic_sql_has_canonical_evidence(self):
        draft = self.draft("了解 SQL 基础，学习基本查询概念。")
        c = draft["draft_json"]["capabilities"][0]
        self.assertEqual((c["name"], c["level"]), ("SQL", 1))
        self.assertIn("了解 SQL 基础", c["evidence"][0]["content"])
        self.assertEqual(c["raw_names"], ["SQL基础"])

    def test_demo_practice_preserves_model_level_and_quote(self):
        source = "使用 SELECT / WHERE / JOIN 完成查询 Demo，保存代码和输出。"
        draft = self.draft(source, "数据库查询", 2)
        c = draft["draft_json"]["capabilities"][0]
        self.assertEqual((c["name"], c["level"]), ("SQL", 2))
        self.assertEqual(c["evidence"][0]["content"], source)

    def test_user_aliases(self):
        for alias in ["SQL基础", "SQL技能", "数据库查询"]:
            data = validate_profile(self.output("了解 SQL 基础", alias), "了解 SQL 基础")
            self.assertEqual(data["capabilities"][0]["name"], "SQL")

    def test_confirmation_persists_all_and_planning_reads_state(self):
        draft = self.draft("了解 SQL 基础，使用 SQL 完成查询练习并保存输出。", "SQL技能", 2)
        self.service.confirm_profile(draft["id"])
        row = self.repo.get_capability("SQL")
        self.assertEqual(row["level"], 2)
        evidence = self.repo.get_evidence(row["id"])
        self.assertEqual(evidence[0]["source"], "resume")
        self.assertEqual(evidence[0]["source_id"], draft["resume_version"])
        self.assertEqual(len(self.repo.list_events(event_type="PROFILE_CONFIRMED")), 1)
        self.repo.add_jd(TargetJD("虚构", "岗位", "SQL项目", {"capabilities": [requirement("SQL实践能力", 3)]}))
        result = PlanningService(self.repo).recompute()
        self.assertEqual(result["top_priority"]["current_level"], 2)
        self.assertFalse(result["top_priority"]["evidence_gap"])
        self.assertEqual(self.repo.list_snapshots()[0]["capability_state_json"][0]["level"], 2)

    def test_empty_analyzer_capabilities_saved_but_cannot_confirm(self):
        source = "项目：使用 SQL 完成库存查询 Demo，保存代码与输出。"
        data = self.output(source); data["capabilities"] = []
        self.request.side_effect = None
        self.request.return_value = json.dumps(data)
        draft = self.service.create_profile_draft(docx_bytes(source), filename="fiction.docx")
        self.assertEqual(draft["draft_json"]["validation_status"], "incomplete")
        with self.assertRaisesRegex(AnalysisError, "能力草稿为空"):
            self.service.confirm_profile(draft["id"])
        self.assertEqual(len(self.repo.open_profile_drafts()), 1)
        self.assertIsNone(self.repo.get_profile())
        self.assertEqual(self.repo.get_capabilities(), [])

    def test_legacy_empty_draft_cannot_confirm(self):
        source = "了解 SQL 基础，使用 SQL 完成查询练习。"
        data = self.output(source); data["capabilities"] = []
        draft_id = self.repo.create_profile_draft(source, "fiction-v1", data)
        with self.assertRaises(AnalysisError):
            self.service.confirm_profile(draft_id)
        self.assertIsNone(self.repo.get_profile())
        self.assertEqual(self.repo.get_capabilities(), [])
        self.assertEqual(self.repo.list_events(), [])
        self.assertEqual(self.repo.get_profile_draft(draft_id)["status"], "draft")

    def test_clearing_capabilities_rejected_without_changing_draft(self):
        draft = self.draft("了解 SQL 基础与查询概念。")
        with self.assertRaises(AnalysisError):
            self.service.update_profile_draft(draft["id"], {"capabilities": []})
        self.assertEqual(self.repo.get_profile_draft(draft["id"])["draft_json"], draft["draft_json"])

    def test_no_skills_does_not_invent_capabilities(self):
        source = "姓名为虚构人物，仅有教育信息。"
        data = {"education": [source], "internships": [], "projects": [], "skills": [], "capabilities": []}
        self.assertEqual(validate_profile(data, source)["capabilities"], [])

    def test_canonicalization_does_not_override_valid_level(self):
        for value in [1,2]:
            source = "使用 SQL 完成查询练习并保存输出。"
            c = validate_profile(self.output(source, "SQL技能", value), source)["capabilities"][0]
            self.assertEqual(c["level"], value)

    def test_evidence_failure_rolls_back_confirmation(self):
        draft = self.draft("了解 SQL 基础，学习基本查询概念。")
        with patch.object(self.repo, "add_evidence_if_new", side_effect=RuntimeError("test failure")):
            with self.assertRaises(RuntimeError):
                self.service.confirm_profile(draft["id"])
        self.assertIsNone(self.repo.get_profile())
        self.assertEqual(self.repo.get_capabilities(), [])
        self.assertEqual(self.repo.list_events(), [])
