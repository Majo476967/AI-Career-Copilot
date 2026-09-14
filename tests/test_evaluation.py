import copy
import json
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from evaluation.baseline import shared_facts
from evaluation.evaluator import ROOT, metrics, run


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.cases = json.loads((ROOT / "cases.json").read_text(encoding="utf-8"))

    def test_frozen_cases_cover_categories(self):
        self.assertEqual(Counter(c["scenario_type"] for c in self.cases),
            {"single_jd": 3, "multi_jd": 3, "completed": 2, "partial": 2,
             "not_completed": 2, "target_change": 2, "long_history": 2})
        self.assertEqual(len({c["case_id"] for c in self.cases}), 16)

    def test_gold_constraints_are_not_prompt_facts(self):
        for case in self.cases:
            facts = shared_facts(case)
            self.assertNotIn("expected_facts", facts)
            self.assertNotIn("expected_behavior", facts)
            self.assertEqual(facts["history"], case["history"])

    def test_metrics_duplicate_and_unknown_format(self):
        case = self.cases[6]
        data = {"capability": "SQL", "task": "  " + case["history"][0]["task"] + "  ",
                "reason": "test", "estimated_time": "10 min", "acceptance_criteria": ["test"]}
        result = metrics(case, json.dumps(data))
        self.assertTrue(result["completed_duplicate"])
        self.assertFalse(result["state_checks"]["avoids_completed_duplicate"])
        self.assertFalse(metrics(case, "invalid")["structured"])
        self.assertIsNone(metrics(case, None, {"type": "APIError"})["structured"])

    def test_archived_capability_not_covered(self):
        data = {"capability": "SQL", "task": "a task", "reason": "test", "estimated_time": "10 min", "acceptance_criteria": ["test"]}
        result = metrics(self.cases[12], json.dumps(data))
        self.assertEqual(result["active_jd_coverage"], 0)
        self.assertFalse(result["state_checks"]["positive_gap"])

    def test_all_cases_use_real_product_with_fake_llm_and_unique_runs(self):
        original = copy.deepcopy(self.cases)
        calls = []
        def fake(system, user):
            facts = json.loads(user)
            cap = facts["top_priority"]["capability"] if "top_priority" in facts else facts["active_jds"][0]["capabilities"][0]["name"]
            calls.append(facts)
            return json.dumps({"capability": cap, "task": "创建一个新的具体练习并保存运行输出与说明文档", "reason": "根据当前能力证据与岗位要求安排下一步练习",
                               "estimated_time": "10 min", "acceptance_criteria": ["保存可复现代码以及实际运行输出"]}, ensure_ascii=False)
        with tempfile.TemporaryDirectory() as temp:
            first = run(self.cases, fake, temp, {"model": "offline_fake"})
            summary = json.loads((first / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["copilot"]["delivered_n"], 16)
            self.assertEqual(len(calls), 32)
            self.assertTrue(all(len(c["history"]) <= 5 for c in calls if "top_priority" in c))
            second = run(self.cases[:1], fake, temp, {"model": "offline_fake"})
            self.assertNotEqual(first, second)
            scores = json.loads((first / "human_scores.json").read_text(encoding="utf-8"))
            self.assertTrue(all(s["actionability"] is None for s in scores))
            self.assertEqual(self.cases, original)

    def test_api_failure_retained_and_excluded(self):
        def fail(system, user):
            raise TimeoutError("sensitive details must not be stored")
        with tempfile.TemporaryDirectory() as temp:
            folder = run(self.cases[:1], fail, temp, {})
            record = json.loads((folder / "C01-baseline.json").read_text(encoding="utf-8"))
            self.assertEqual(record["api_error"]["type"], "TimeoutError")
            self.assertNotIn("sensitive", json.dumps(record))
            summary = json.loads((folder / "summary.json").read_text(encoding="utf-8"))
            self.assertIsNone(summary["baseline"]["state_check_accuracy"])

    def test_fixture_history_matches_non_sql_capability(self):
        for case in self.cases:
            for history in case["history"]:
                if history["capability"] != "SQL":
                    self.assertNotIn("JOIN", history["task"])
            self.assertEqual(case["latest_feedback"], case["history"][-1] if case["history"] else None)

    def test_metrics_normalize_current_level_alias(self):
        case = copy.deepcopy(self.cases[2])
        case["capabilities"][0]["level"] = 4
        raw = json.dumps({"capability": "User Research", "task": "a task", "reason": "test",
                          "estimated_time": "10 min", "acceptance_criteria": ["test"]})
        self.assertFalse(metrics(case, raw)["state_checks"]["positive_gap"])
