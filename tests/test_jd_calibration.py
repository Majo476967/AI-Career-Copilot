"""Offline regressions for human smoke BC-JD-001 / BC-JD-002."""
import copy
import unittest
from unittest.mock import patch
from core.capabilities import normalize_capability, calibrate_required_level
from core.requirement_aggregation import aggregate_requirements
from core.priority_engine import calculate_priorities
from tools.analysis_validation import validate_jd
from tools.jd_analyzer import analyze_jd_text
from ui.adapter import requirement_rows, requirement_level_label, level_label
from tests.phase3_fixtures import jd, requirement, capability


class JDCalibrationTests(unittest.TestCase):
    def analyze(self, evidence, value=0, name="SQL技能"):
        item = {**requirement(name, value, evidence=evidence), "category": "technical"}
        return validate_jd({"company": "", "job_title": "", "capabilities": [item]}, evidence)

    def test_python_aliases(self):
        for name in ["Python基础", "Python技能", "Ｐｙｔｈｏｎ 开发能力"]:
            self.assertEqual(normalize_capability(name), "Programming")

    def test_sql_aliases(self):
        for name in ["SQL实践能力", "SQL技能", "SQL查询和分析业务数据", "数据库查询能力", "查询业务数据能力"]:
            self.assertEqual(normalize_capability(name), "SQL")

    def test_analysis_aliases(self):
        for name in ["数据分析理解", "数据分析与指标拆解", "解释指标变化", "业务指标理解"]:
            self.assertEqual(normalize_capability(name), "Data Analysis")

    def test_research_aliases(self):
        for name in ["用户研究能力", "用户调研经验", "用户访谈技巧", "问卷设计能力"]:
            self.assertEqual(normalize_capability(name), "User Research")

    def test_unknown_and_ambiguous_names_preserved(self):
        for name in ["CAD 建模", "NoSQL", "Pythonic", "Python 与 SQL"]:
            self.assertEqual(normalize_capability(name), name)

    def test_coverage_and_archived(self):
        jobs = [jd(1, [requirement("SQL实践能力"), requirement("Python基础")]),
                jd(2, [requirement("SQL技能"), requirement("Python技能")]),
                jd(3, [requirement("SQL查询和分析业务数据")]),
                jd(4, [requirement("Python")], "archived")]
        result = calculate_priorities(jobs, [capability()])
        rows = {r["capability"]: r for r in result["ranked_priorities"]}
        self.assertEqual(rows["SQL"]["coverage"], 1)
        self.assertEqual(rows["Programming"]["coverage"], 2/3)
        self.assertEqual(result["total_active_jd_count"], 3)

    def test_analysis_coverage(self):
        jobs = [jd(i, [requirement(name)]) for i, name in enumerate(
            ["数据分析理解", "数据分析与指标拆解", "解释指标变化"], 1)]
        row = aggregate_requirements(jobs)["requirements"][0]
        self.assertEqual(row["active_jd_count"], 3)
        self.assertEqual(row["capability_name"], "Data Analysis")

    def test_join_groupby_is_practice(self):
        result = self.analyze("熟悉 SQL，能用 JOIN 和 GROUP BY 完成查询练习")
        self.assertEqual(result["capabilities"][0]["required_level"], 2)

    def test_business_queries_are_practice(self):
        for evidence in ["必须能够用 SQL 查询和分析业务数据", "能够使用 Python 分析订单数据", "使用数据库工具完成业务查询"]:
            self.assertEqual(calibrate_required_level(0, evidence), 2)

    def test_project_experience(self):
        for evidence in ["有真实 SQL 项目经验", "有 SQL 数据分析项目/实习经验", "实际负责过 SQL 业务落地"]:
            self.assertEqual(calibrate_required_level(0, evidence), 3)

    def test_understanding_and_depth(self):
        self.assertEqual(calibrate_required_level(0, "了解 SQL 基础概念"), 1)
        self.assertEqual(calibrate_required_level(0, "负责复杂系统设计与深度优化"), 4)

    def test_negated_experience_does_not_promote(self):
        self.assertEqual(calibrate_required_level(0, "不要求项目经验，能用 SQL 完成查询"), 2)
        self.assertEqual(calibrate_required_level(3, "不要求项目经验"), 0)

    def test_explicit_practice_corrects_overstated_model(self):
        self.assertEqual(calibrate_required_level(4, "能用 SQL 完成查询练习"), 2)

    def test_unknown_requirement_blocks_zero_gap(self):
        jobs = [jd(1, [requirement(level=0, evidence="SQL能力")])]
        result = calculate_priorities(jobs, [capability(level=4)])
        self.assertEqual(result["status"], "insufficient_requirement_data")
        self.assertIsNone(result["top_priority"])
        self.assertEqual(result["gaps"], [])
        self.assertIn("岗位要求深度未明确", result["reason"])

    def test_legacy_zero_is_calibrated_without_mutation(self):
        jobs = [jd(1, [requirement("SQL技能", 0, evidence="必须能够用 SQL 查询和分析业务数据")])]
        original = copy.deepcopy(jobs)
        result = calculate_priorities(jobs, [capability(level=1)])
        self.assertEqual(result["top_priority"]["required_levels"], [2])
        self.assertEqual(jobs, original)

    def test_raw_names_retained_and_merge_idempotent(self):
        source = "能用 SQL 完成查询练习"
        a = {**requirement("SQL技能", 0, evidence=source), "category": "technical"}
        b = {**a, "name": "SQL实践能力"}
        result = validate_jd({"company": "", "job_title": "", "capabilities": [a,b]}, source)
        self.assertEqual(result["capabilities"][0]["raw_names"], ["SQL技能", "SQL实践能力"])
        self.assertEqual(validate_jd(result, source), result)

    def test_jd_ui_does_not_use_user_unknown_label(self):
        data = self.analyze("SQL能力")
        rows = requirement_rows(data)
        self.assertEqual(rows[0]["要求等级"], "岗位未明确等级")
        self.assertNotIn("当前证据不足", str(rows))
        self.assertEqual(requirement_level_label(2), "2 · 实践使用")

    def test_user_zero_label_unchanged(self):
        self.assertEqual(level_label(0), "0 · 当前证据不足")

    def test_analyzer_uses_one_fake_request(self):
        import json
        evidence = "必须能够用 SQL 查询和分析业务数据"
        data = {"company": "", "job_title": "", "capabilities": [
            {**requirement("SQL技能", 0, evidence=evidence), "category": "technical"}]}
        with patch("llm.request_analysis", return_value=json.dumps(data)) as request:
            result = analyze_jd_text(evidence)
        request.assert_called_once()
        self.assertEqual(result["capabilities"][0]["required_level"], 2)

    def test_unknown_only_skips_its_capability(self):
        jobs = [jd(1, [requirement("SQL", 2), requirement("Agent", 0, evidence="Agent能力")])]
        result = calculate_priorities(jobs, [capability(level=1)])
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["top_priority"]["capability"], "SQL")
        self.assertEqual([r["capability"] for r in result["gaps"]], ["SQL"])
        self.assertEqual(result["unknown_requirement_capabilities"], ["Agent"])
        self.assertIn("岗位要求深度未明确", result["warnings"][0])
        self.assertIn("Agent", result["warnings"][0])
        row = next(r for r in result["requirements"] if r["capability_name"] == "Agent")
        self.assertTrue(row["requirement_level_unknown"])

    def test_partly_unknown_same_capability_excluded_as_a_whole(self):
        jobs = [jd(1, [requirement("SQL", 0, evidence="SQL技能"), requirement("Agent", 2)]),
                jd(2, [requirement("SQL", 3)])]
        result = calculate_priorities(jobs, [capability()])
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["top_priority"]["capability"], "Agent")
        self.assertEqual([r["capability"] for r in result["gaps"]], ["Agent"])
        self.assertEqual(result["top_priority"]["coverage"], 0.5)

    def test_unknown_and_satisfied_known_are_insufficient(self):
        jobs = [jd(1, [requirement("SQL", 2), requirement("Agent", 0, evidence="Agent能力")])]
        result = calculate_priorities(jobs, [capability(level=2)])
        self.assertEqual(result["status"], "insufficient_requirement_data")
        self.assertEqual(result["ranked_priorities"], [])
        self.assertEqual([r["capability"] for r in result["gaps"]], ["SQL"])

    def test_all_known_satisfied_still_no_positive_gap(self):
        result = calculate_priorities([jd()], [capability(level=4)])
        self.assertEqual(result["status"], "no_positive_gap")
        self.assertEqual(result["warnings"], [])

    def test_archived_unknown_does_not_warn_or_block(self):
        result = calculate_priorities([jd(), jd(2, [requirement("Agent", 0, evidence="Agent能力")], "archived")], [capability()])
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["warnings"], [])
        self.assertEqual(result["top_priority"]["coverage"], 1)

    def test_no_active_jd_keeps_original_status(self):
        self.assertEqual(calculate_priorities([], [])['status'], 'no_active_jd')


from tests.phase4_fixtures import Phase4Case
from core.schemas import TargetJD


class UnknownRequirementPlanningTests(Phase4Case):
    def test_known_task_still_created_and_retained(self):
        self.repo.add_jd(TargetJD("虚构公司", "未知深度", "Agent能力", {"capabilities": [
            requirement("Agent", 0, evidence="Agent能力")]}))
        first = self.first()
        result = self.planning.recompute()
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["planning_status"], "retained")
        self.assertEqual(result["selected_task"]["id"], first["id"])
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(result["unknown_requirement_capabilities"], ["Agent"])
