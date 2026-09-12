import unittest
from core.errors import BusinessError
from core.gap_engine import calculate_gap


class GapEngineTests(unittest.TestCase):
    def test_positive_gap(self):
        gap = calculate_gap(1, [3])
        self.assertEqual(gap["raw_gaps"], [2])
        self.assertEqual(gap["gap_severity"], 0.5)

    def test_met_or_exceeded_requirements(self):
        gap = calculate_gap(3, [2, 3])
        self.assertEqual(gap["raw_gaps"], [0, 0])
        self.assertEqual(gap["gap_severity"], 0)
        self.assertIsNone(gap["next_gap_type"])

    def test_multi_jd_average_includes_zero_contributions(self):
        gap = calculate_gap(2, [1, 2, 3, 4])
        self.assertEqual(gap["raw_gaps"], [0, 0, 1, 2])
        self.assertEqual(gap["gap_severity"], 3 / 16)

    def test_level_zero_is_evidence_gap(self):
        self.assertTrue(calculate_gap(0, [3])["evidence_gap"])
        self.assertFalse(calculate_gap(1, [3])["evidence_gap"])

    def test_next_gap_mapping(self):
        for level, expected in enumerate(["evidence_knowledge_verification", "practice", "experience", "depth"]):
            with self.subTest(level=level):
                self.assertEqual(calculate_gap(level, [4])["next_gap_type"], expected)

    def test_cross_level_gap_only_next_level(self):
        self.assertEqual(calculate_gap(1, [3])["next_gap_type"], "practice")
        self.assertEqual(calculate_gap(0, [4])["next_gap_type"], "evidence_knowledge_verification")

    def test_zero_required_level_does_not_request_verification(self):
        gap = calculate_gap(0, [0])
        self.assertEqual(gap["gap_severity"], 0)
        self.assertIsNone(gap["next_gap_type"])

    def test_severity_extremes(self):
        self.assertEqual(calculate_gap(0, [4, 4])["gap_severity"], 1)
        self.assertEqual(calculate_gap(4, [0, 4])["gap_severity"], 0)

    def test_invalid_levels_are_business_errors(self):
        for level in (-1, 5, True, 1.5, "1", None):
            with self.subTest(level=level), self.assertRaises(BusinessError):
                calculate_gap(level, [3])
            with self.subTest(required=level), self.assertRaises(BusinessError):
                calculate_gap(0, [level])

    def test_missing_requirements_are_business_errors(self):
        for values in ([], None, "3"):
            with self.subTest(values=values), self.assertRaises(BusinessError):
                calculate_gap(0, values)
