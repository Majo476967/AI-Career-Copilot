import json
from unittest.mock import Mock
from core.errors import BusinessError
from core.planner import TaskPlanner, PROMPT
from tests.phase4_fixtures import Phase4Case, task_output


class TaskPlannerTests(Phase4Case):
    def context(self):
        from core.priority_engine import calculate_priorities
        result = calculate_priorities(self.repo.get_active_jds(), self.repo.get_capabilities())
        return self.memory.build_context(result, self.repo.get_profile())

    def check_invalid(self, data, code):
        planner = TaskPlanner(request=Mock(return_value=json.dumps(data)))
        with self.assertRaises(BusinessError) as caught:
            planner.plan(self.context())
        self.assertEqual(caught.exception.code, code)

    def test_structured_task(self):
        task = self.planner.plan(self.context())
        self.assertEqual(task.capability, "SQL")
        self.assertEqual(task.estimated_time, "30 min")
        self.assertTrue(task.acceptance_criteria_json)

    def test_non_json(self):
        with self.assertRaises(BusinessError) as caught:
            TaskPlanner(request=Mock(return_value="not JSON")).plan(self.context())
        self.assertEqual(caught.exception.code, "invalid_task_json")

    def test_direction_change_rejected(self):
        self.check_invalid(task_output("Evaluation"), "wrong_capability")

    def test_empty_acceptance_rejected(self):
        data = task_output(); data["acceptance_criteria"] = []
        self.check_invalid(data, "invalid_criteria")

    def test_missing_acceptance_rejected(self):
        data = task_output(); del data["acceptance_criteria"]
        self.check_invalid(data, "invalid_task")

    def test_invalid_time(self):
        for value in ("soon", "-1 min", "999 min", 30, "NaN h"):
            with self.subTest(value=value):
                self.check_invalid(task_output(minutes=value), "invalid_time")

    def test_over_time_budget(self):
        self.check_invalid(task_output(minutes="2 hours"), "time_budget_exceeded")

    def test_generic_task_rejected(self):
        self.check_invalid(task_output(text="学习 SQL"), "invalid_task")

    def test_api_error_readable(self):
        with self.assertRaises(BusinessError) as caught:
            TaskPlanner(request=Mock(side_effect=RuntimeError("secret"))).plan(self.context())
        self.assertEqual(caught.exception.code, "planner_api_error")
        self.assertNotIn("secret", str(caught.exception))

    def test_prompt_constrains_next_gap_and_feedback(self):
        self.planner.plan(self.context())
        self.assertEqual(self.calls[0][1]["top_priority"]["next_gap_type"], "practice")
        for phrase in ("partial", "not_completed", "evidence_knowledge_verification", "experience", "depth", "不得改变能力方向"):
            self.assertIn(phrase, PROMPT)

    def test_empty_reason(self):
        data = task_output(); data["reason"] = ""
        self.check_invalid(data, "invalid_task")
