import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from openai import APIError
from core.capabilities import normalize_capability, VOCABULARY
from core.errors import AnalysisError, ParseError
from tools.user_analyzer import analyze_resume
from tools.jd_analyzer import analyze_jd_text
from tests.phase2_fixtures import RESUME, profile, jd_input, jd_output


class AnalyzerTests(unittest.TestCase):
    def setUp(self):
        model = patch("llm.get_chat_model")
        self.model = model.start().return_value
        self.addCleanup(model.stop)

    def response(self, value):
        self.model.invoke.return_value = SimpleNamespace(content=json.dumps(value, ensure_ascii=False))

    def test_valid_resume_json(self):
        self.response(profile())
        result = analyze_resume(RESUME)
        self.assertEqual(result["capabilities"][0]["name"], "SQL")
        self.assertEqual(result["capabilities"][0]["level"], 2)

    def test_invalid_json(self):
        self.model.invoke.return_value = SimpleNamespace(content="not json")
        with self.assertRaises(AnalysisError) as caught:
            analyze_resume(RESUME)
        self.assertEqual(caught.exception.code, "invalid_json")

    def test_missing_profile_fields(self):
        self.response({"education": []})
        with self.assertRaises(AnalysisError):
            analyze_resume(RESUME)

    def test_profile_level_range_and_type(self):
        for value in (-1, 5, True, "2", 1.5):
            with self.subTest(value=value):
                data = profile()
                data["capabilities"][0]["level"] = value
                self.response(data)
                with self.assertRaises(AnalysisError):
                    analyze_resume(RESUME)

    def test_no_evidence_cannot_raise_level(self):
        data = profile()
        data["capabilities"][0]["evidence"] = []
        self.response(data)
        with self.assertRaises(AnalysisError):
            analyze_resume(RESUME)
        data["capabilities"][0]["level"] = 0
        self.response(data)
        self.assertEqual(analyze_resume(RESUME)["capabilities"][0]["level"], 0)

    def test_keyword_alone_cannot_raise_level(self):
        data = profile()
        data["capabilities"][0]["evidence"][0]["content"] = "SQL"
        self.response(data)
        with self.assertRaises(AnalysisError):
            analyze_resume(RESUME)

    def test_fabricated_experience_rejected(self):
        data = profile()
        data["internships"] = ["在真实知名公司担任负责人"]
        self.response(data)
        with self.assertRaises(AnalysisError):
            analyze_resume(RESUME)

    def test_fabricated_evidence_rejected(self):
        data = profile()
        data["capabilities"][0]["evidence"][0]["content"] = "优化千万级 SQL 查询"
        self.response(data)
        with self.assertRaises(AnalysisError):
            analyze_resume(RESUME)

    def test_evidence_type_and_source_rejected(self):
        for key, value in (("source", "invented"), ("evidence_type", "unknown_kind")):
            data = profile()
            data["capabilities"][0]["evidence"][0][key] = value
            self.response(data)
            with self.subTest(key=key), self.assertRaises(AnalysisError):
                analyze_resume(RESUME)

    def test_empty_resume_no_llm_call(self):
        with self.assertRaises(ParseError):
            analyze_resume("")
        self.model.invoke.assert_not_called()

    def test_api_error_is_readable(self):
        self.model.invoke.side_effect = APIError("private response", Mock(), body=None)
        with self.assertRaises(AnalysisError) as caught:
            analyze_resume(RESUME)
        self.assertEqual(caught.exception.code, "llm_error")
        self.assertNotIn("private response", str(caught.exception))

    def test_empty_response(self):
        self.model.invoke.return_value = SimpleNamespace(content="")
        with self.assertRaises(AnalysisError):
            analyze_resume(RESUME)

    def test_valid_jd(self):
        self.response(jd_output())
        result = analyze_jd_text(jd_input())
        self.assertEqual(result["capabilities"][0]["name"], "SQL")
        self.assertEqual(result["capabilities"][1]["name"], "Data Analysis")
        self.assertNotIn("priority", result)

    def test_invalid_importance(self):
        data = jd_output()
        data["capabilities"][0]["importance"] = "high"
        self.response(data)
        with self.assertRaises(AnalysisError):
            analyze_jd_text(jd_input())

    def test_invalid_required_level(self):
        data = jd_output()
        data["capabilities"][0]["required_level"] = 5
        self.response(data)
        with self.assertRaises(AnalysisError):
            analyze_jd_text(jd_input())

    def test_same_jd_capability_merged(self):
        data = jd_output()
        data["capabilities"].append({"name": "数据库查询", "category": "technical",
            "importance": "bonus", "required_level": 3, "evidence": "数据库查询练习"})
        self.response(data)
        result = analyze_jd_text(jd_input())
        self.assertEqual(len(result["capabilities"]), 2)
        sql = result["capabilities"][0]
        self.assertEqual(sql["required_level"], 3)
        self.assertEqual(sql["importance"], "must_have")
        self.assertIn("数据库查询练习", sql["evidence"])

    def test_merged_jd_evidence_can_be_validated_again(self):
        from tools.analysis_validation import validate_jd
        data = jd_output()
        data["capabilities"].append({"name": "数据库查询", "category": "technical",
            "importance": "bonus", "required_level": 3, "evidence": "数据库查询练习"})
        merged = validate_jd(data, jd_input())
        self.assertEqual(validate_jd(merged, jd_input()), merged)

    def test_unreliable_company_can_be_empty(self):
        data = jd_output()
        data["company"], data["job_title"] = "", "unknown"
        self.response(data)
        self.assertEqual(analyze_jd_text(jd_input())["company"], "")

    def test_jd_fabricated_requirement_rejected(self):
        data = jd_output()
        data["capabilities"][0]["evidence"] = "必须有 Agent 开发经验"
        self.response(data)
        with self.assertRaises(AnalysisError):
            analyze_jd_text(jd_input())

    def test_jd_missing_field_and_empty_capabilities(self):
        for data in ({"company": ""}, {"company": "", "job_title": "", "capabilities": []}):
            self.response(data)
            with self.assertRaises(AnalysisError):
                analyze_jd_text(jd_input())

    def test_normalization_aliases(self):
        for name in ("智能体", "AI Agent", "Agent开发", " ａｉ agent "):
            self.assertEqual(normalize_capability(name), "Agent")
        for name in ("数据能力", "业务数据分析", "指标分析"):
            self.assertEqual(normalize_capability(name), "Data Analysis")
        for name in ("SQL能力", "数据库查询", "MySQL查询"):
            self.assertEqual(normalize_capability(name), "SQL")
        for name in VOCABULARY:
            self.assertEqual(normalize_capability(name), name)

    def test_unknown_capability_preserved(self):
        self.assertEqual(normalize_capability("  CAD   建模  "), "CAD 建模")
