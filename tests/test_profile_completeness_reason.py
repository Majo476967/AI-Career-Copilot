"""BC-PROFILE-002 / BC-TASK-001: no live API or production database."""
import copy
import json
import unittest
from unittest.mock import Mock
from core.capabilities import explicit_resume_capabilities
from core.errors import AnalysisError, BusinessError
from core.planner import TaskPlanner, user_visible_reason, GAP_LABELS
from tools.analysis_validation import validate_profile
from tests.phase4_fixtures import Phase4Case, task_output
from tests.phase2_fixtures import profile, RESUME
from services.profile_service import ProfileService


def draft(source, names):
    return {"education": [], "internships": [], "projects": [], "skills": [source],
            "capabilities": [{"name": name, "level": 1, "evidence": [
                {"evidence_type": "skill", "content": source, "source": "resume"}]} for name in names]}


class CompletenessTests(unittest.TestCase):
    def test_python_missing_from_nonempty_capabilities(self):
        source = "了解 SQL 基础、Python 基础。"
        with self.assertRaises(AnalysisError) as caught:
            validate_profile(draft(source, ["SQL"]), source)
        self.assertEqual(caught.exception.code, "incomplete_profile")
        self.assertIn("Programming", str(caught.exception))

    def test_python_present_passes(self):
        source = "了解 Python 基础。"
        result = validate_profile(draft(source, ["Programming"]), source)
        self.assertEqual(result["capabilities"][0]["name"], "Programming")

    def test_only_python_missing_in_three_capabilities(self):
        source = "了解 SQL 基础、Python 基础及数据分析概念。"
        with self.assertRaises(AnalysisError) as caught:
            validate_profile(draft(source, ["SQL", "Data Analysis"]), source)
        self.assertIn("Programming", str(caught.exception))
        self.assertNotIn("Data Analysis", str(caught.exception))

    def test_fuzzy_text_does_not_invent_requirement(self):
        source = "善于沟通，具有分析能力，积极学习新知识。"
        self.assertEqual(explicit_resume_capabilities(source), set())
        self.assertEqual(validate_profile(draft(source, []), source)["capabilities"], [])

    def test_all_explicit_aliases_align_with_canonical(self):
        source = "数据库查询、Python、业务指标、用户调研、智能体、检索增强、评测"
        names = ["SQL技能", "Python基础", "数据分析", "用户研究", "Agent", "RAG", "Evaluation"]
        result = validate_profile(draft(source, names), source)
        self.assertEqual({c["name"] for c in result["capabilities"]}, explicit_resume_capabilities(source))

    def test_same_sentence_collects_multiple_keywords(self):
        self.assertEqual(explicit_resume_capabilities("使用 SQL 和 Python 进行数据分析"), {"SQL", "Programming", "Data Analysis"})

    def test_latin_word_boundaries_and_fullwidth(self):
        self.assertEqual(explicit_resume_capabilities("NoSQL Pythonic fragrance reevaluation"), set())
        self.assertEqual(explicit_resume_capabilities("Ｐｙｔｈｏｎ、ｓｑｌ"), {"Programming", "SQL"})

    def test_no_automatic_capability_or_level_mutation(self):
        source = "了解 SQL 与 Python 基础"
        data = draft(source, ["SQL"]); before = copy.deepcopy(data)
        with self.assertRaises(AnalysisError): validate_profile(data, source)
        self.assertEqual(data, before)
        complete = draft(source, ["SQL", "Python"])
        complete["capabilities"][1]["level"] = 0
        self.assertEqual(validate_profile(complete, source)["capabilities"][1]["level"], 0)


class ReasonTests(unittest.TestCase):
    def plan(self, reason, feedback=None):
        output = task_output(); output["reason"] = reason
        request = Mock(return_value=json.dumps(output))
        return TaskPlanner(request).plan({"top_priority": {"capability": "SQL"},
                                         "task_budget_minutes": 60, "latest_feedback": feedback})

    def test_missing_feedback_rejects_false_attribution(self):
        for phrase in ["根据最新反馈", "根据你的反馈", "你反馈说", "用户反馈表明"]:
            with self.subTest(phrase=phrase), self.assertRaises(BusinessError) as caught:
                self.plan(phrase + "需要进一步完成 SQL 练习。")
            self.assertEqual(caught.exception.code, "unsupported_feedback_attribution")

    def test_real_feedback_allows_attribution(self):
        reason = "根据最新反馈，继续解决 JOIN 查询中的关联条件问题。"
        self.assertEqual(self.plan(reason, {"event_id": 1, "feedback": "JOIN 关联条件出错"}).reason, reason)

    def test_no_feedback_state_reason_passes(self):
        reason = "根据当前能力与岗位要求，安排下一阶段的 SQL 练习。"
        self.assertEqual(self.plan(reason).reason, reason)

    def test_enum_reason_translated_without_changing_task(self):
        task = self.plan("当前处于 evidence_knowledge_verification 阶段，需补充基础证据。")
        self.assertNotIn("evidence_knowledge_verification", task.reason)
        self.assertIn("补充或核实基础能力证据", task.reason)
        self.assertEqual(task.task_text, task_output()["task"])

    def test_all_enum_labels_and_legacy_ui_projection(self):
        for enum, label in GAP_LABELS.items():
            self.assertEqual(user_visible_reason("阶段：" + enum), "阶段：" + label)
        self.assertEqual(user_visible_reason("experienced practitioner"), "experienced practitioner")


class CompletenessIntegrationTests(Phase4Case):
    def test_partial_missing_cannot_confirm_or_change_state(self):
        data = profile(); data["capabilities"] = data["capabilities"][:1]
        key = self.repo.create_profile_draft(RESUME, "fictional", data)
        before = self.repo.get_capabilities()
        with self.assertRaises(AnalysisError): ProfileService(self.repo).confirm_profile(key)
        self.assertEqual(self.repo.get_capabilities(), before)
        self.assertEqual(self.repo.list_events(event_type="PROFILE_CONFIRMED"), [])

    def test_real_memory_none_blocks_bad_planner_write(self):
        self.planner.request = Mock(return_value=json.dumps({**task_output(), "reason": "根据最新反馈，需要进一步完成 SQL 查询练习。"}))
        result = self.planning.recompute()
        self.assertEqual(result["status"], "planning_failed")
        self.assertEqual(self.repo.pending_tasks(), [])
        context = json.loads(self.planner.request.call_args.args[1])
        self.assertIsNone(context["latest_feedback"])
