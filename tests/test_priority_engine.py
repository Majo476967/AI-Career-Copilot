import copy
import unittest
from core.priority_engine import calculate_priorities
from core.requirement_aggregation import aggregate_requirements
from tests.phase3_fixtures import capability, jd, requirement


class PriorityEngineTests(unittest.TestCase):
    def top(self, jds=None, caps=None):
        return calculate_priorities([jd()] if jds is None else jds,
                                    [capability()] if caps is None else caps)["top_priority"]

    def test_four_of_five_coverage(self):
        jobs = [jd(i) for i in range(1, 5)] + [jd(5, [requirement("Agent")])]
        self.assertEqual(self.top(jobs)["coverage"], 0.8)

    def test_archived_jds_excluded(self):
        jobs = [jd(), jd(2, [requirement("Agent", 4)], "archived")]
        result = calculate_priorities(jobs, [capability()])
        self.assertEqual(result["total_active_jd_count"], 1)
        self.assertEqual([r["capability"] for r in result["ranked_priorities"]], ["SQL"])
        self.assertEqual(result["top_priority"]["coverage"], 1)

    def test_duplicate_aliases_count_once_and_keep_evidence(self):
        jobs = [jd(1, [requirement("SQL能力", 2, "bonus", "First quote"),
                       requirement("数据库查询", 3, "important", "Second quote")])]
        row = aggregate_requirements(jobs)["requirements"][0]
        self.assertEqual(row["capability_name"], "SQL")
        self.assertEqual(row["active_jd_count"], 1)
        self.assertEqual(row["required_levels"], [3])
        self.assertEqual(row["importance_values"], [0.7])
        self.assertEqual(row["evidence_by_jd"], {"1": ["First quote", "Second quote"]})

    def test_importance_mapping(self):
        for label, value in [("must_have", 1), ("important", 0.7), ("bonus", 0.3)]:
            with self.subTest(label=label):
                self.assertEqual(self.top([jd(1, [requirement(importance=label)])])["importance"], value)

    def test_importance_averaged_only_over_requiring_jds(self):
        jobs = [jd(1, [requirement(importance="must_have")]),
                jd(2, [requirement(importance="bonus")]), jd(3, [])]
        row = self.top(jobs)
        self.assertEqual(row["importance"], 0.65)
        self.assertEqual(row["coverage"], 2 / 3)

    def test_formula(self):
        row = self.top()
        # One of one JD, must_have, current=1 required=2, practice feasibility.
        self.assertAlmostEqual(row["score"], 0.35 + 0.25 + 0.30 * 0.25 + 0.10 * 0.9)
        self.assertAlmostEqual(sum(row["reason"]["weighted_components"].values()), row["score"])

    def test_no_gap_filtered_before_scoring(self):
        result = calculate_priorities([jd()], [capability(level=2)])
        self.assertEqual(result["ranked_priorities"], [])
        self.assertEqual(result["gaps"][0]["gap_severity"], 0)

    def test_high_coverage_without_gap_cannot_win(self):
        jobs = [jd(1, [requirement(), requirement("Agent", 2, "bonus")]), jd(2)]
        result = calculate_priorities(jobs, [capability(level=4), capability("Agent", 1)])
        self.assertEqual([r["capability"] for r in result["ranked_priorities"]], ["Agent"])

    def test_feasibility_mapping(self):
        for level, expected in enumerate([1.0, 0.9, 0.6, 0.4]):
            with self.subTest(level=level):
                self.assertEqual(self.top([jd(1, [requirement(level=4)])], [capability(level=level)])["feasibility"], expected)

    def test_tie_prefers_larger_gap(self):
        jobs = [jd(1, [requirement("Agent", 2), requirement("SQL", 3, "important")])]
        result = calculate_priorities(jobs, [capability("Agent", 1), capability("SQL", 1)])
        self.assertEqual(result["ranked_priorities"][0]["score"], result["ranked_priorities"][1]["score"])
        self.assertEqual(result["top_priority"]["capability"], "SQL")

    def test_tie_prefers_larger_coverage(self):
        jobs = [jd(1, [requirement("Agent"), requirement("SQL", 2, "bonus")]),
                jd(2, [requirement("SQL", 2, "bonus")])]
        result = calculate_priorities(jobs, [capability("Agent", 1), capability("SQL", 1)])
        self.assertEqual(result["ranked_priorities"][0]["score"], result["ranked_priorities"][1]["score"])
        self.assertEqual(result["top_priority"]["capability"], "SQL")

    def test_tie_lexical_order_independent_of_input_order(self):
        rows = [requirement("SQL"), requirement("Agent")]
        caps = [capability("SQL"), capability("Agent")]
        first = calculate_priorities([jd(1, rows)], caps)
        second = calculate_priorities([jd(1, list(reversed(rows)))], list(reversed(caps)))
        self.assertEqual(first, second)
        self.assertEqual(first["top_priority"]["capability"], "Agent")

    def test_repeated_and_reordered_jds_are_deterministic(self):
        jobs = [jd(2, [requirement(level=4)]), jd(1)]
        first = calculate_priorities(jobs, [capability()])
        for _ in range(3):
            self.assertEqual(first, calculate_priorities(jobs, [capability()]))
        self.assertEqual(first, calculate_priorities(list(reversed(jobs)), [capability()]))

    def test_no_positive_gap_status(self):
        result = calculate_priorities([jd()], [capability(level=4)])
        self.assertEqual(result["status"], "no_positive_gap")
        self.assertIsNone(result["top_priority"])

    def test_missing_capability_is_unknown_evidence(self):
        row = self.top(caps=[])
        self.assertEqual(row["current_level"], 0)
        self.assertTrue(row["evidence_gap"])
        self.assertEqual(row["reason"]["gap_kind"], "Evidence Gap")
        self.assertIn("当前缺少可验证证据", row["reason"]["state_explanation"])
        self.assertNotIn("很弱", str(row))
        self.assertNotIn("不会", str(row))

    def test_confirmed_level_is_skill_gap(self):
        self.assertEqual(self.top()["reason"]["gap_kind"], "Skill Gap")

    def test_no_active_jd(self):
        self.assertEqual(calculate_priorities([], [capability()])["status"], "no_active_jd")

    def test_no_valid_capabilities(self):
        self.assertEqual(calculate_priorities([jd(1, [])], [])["status"], "no_valid_capabilities")

    def test_widely_different_required_levels(self):
        row = self.top([jd(1, [requirement(level=1)]), jd(2, [requirement(level=4)])], [capability(level=2)])
        self.assertEqual(row["raw_gaps"], [0, 2])
        self.assertEqual(row["gap_severity"], 0.25)
        self.assertEqual(row["next_gap_type"], "experience")

    def test_invalid_input_has_readable_result(self):
        invalid_jobs = [None, [{}], [jd(), jd()], [jd(1, [{"name": "SQL"}])],
                        [jd(1, [requirement(level=9)])], [jd(1, [requirement(importance="urgent")])],
                        [jd(1, [requirement(evidence="")])]]
        for jobs in invalid_jobs:
            with self.subTest(jobs=jobs):
                result = calculate_priorities(jobs, [])
                self.assertEqual(result["status"], "invalid_input")
                self.assertTrue(result["reason"])
                self.assertIsNone(result["top_priority"])

    def test_conflicting_normalized_user_levels_rejected(self):
        result = calculate_priorities([jd()], [capability("SQL", 1), capability("数据库查询", 3)])
        self.assertEqual(result["status"], "invalid_input")

    def test_inputs_not_mutated(self):
        jobs, caps = [jd()], [capability()]
        original = copy.deepcopy((jobs, caps))
        calculate_priorities(jobs, caps)
        self.assertEqual((jobs, caps), original)

    def test_explanation_preserves_fact_sources(self):
        row = self.top()
        reason = row["reason"]
        self.assertEqual(reason["jd_ids"], [1])
        self.assertEqual(reason["evidence_by_jd"], {"1": ["Synthetic SQL requirement"]})
        self.assertEqual(reason["required_levels"], [2])
        self.assertEqual(reason["rank"], 1)
        self.assertTrue(reason["selection"])
        self.assertIn("尚未经过实验验证", reason["feasibility_basis"]["heuristic"])
