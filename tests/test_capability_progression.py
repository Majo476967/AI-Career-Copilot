import sqlite3
from unittest.mock import patch
from core.capability_progression import progress_capability
from core.errors import BusinessError
from core.schemas import Capability, EventType, Task, TargetJD
from tests.phase3_fixtures import requirement
from tests.phase4_fixtures import Phase4Case


class CapabilityProgressionTests(Phase4Case):
    def finish(self, task, status="completed", feedback=None):
        return self.tasks.submit_task_feedback(task["id"], status, feedback)

    def two(self, level):
        self.repo.upsert_capability(Capability("SQL", level))
        a = self.first(); first = self.finish(a)
        b = first["replanning"]["selected_task"]
        second = self.finish(b)
        return a, b, first, second

    def test_one_knowledge_completion_no_promotion(self):
        self.repo.upsert_capability(Capability("SQL", 0))
        self.finish(self.first())
        self.assertEqual(self.repo.get_capability("SQL")["level"], 0)

    def test_two_distinct_knowledge_tasks_promote(self):
        a, b, _, second = self.two(0)
        self.assertNotEqual(a["task_key"], b["task_key"])
        self.assertEqual((a["target_level"], a["gap_type"]), (1, "evidence_knowledge_verification"))
        self.assertEqual(self.repo.get_capability("SQL")["level"], 1)
        self.assertEqual(second["progression"]["new_level"], 1)

    def test_duplicate_feedback_not_counted(self):
        task = self.first(); self.finish(task)
        with self.assertRaises(BusinessError):
            self.finish(task)
        self.assertEqual(self.repo.get_capability("SQL")["level"], 1)
        self.assertEqual(len(self.repo.list_events(event_type="TASK_COMPLETED")), 1)

    def test_same_key_different_ids_count_once(self):
        task = self.first(); self.finish(task)
        repeat = self.tasks.create_task(Task("SQL", task["task_text"], task["reason"], "30 min",
            task["acceptance_criteria_json"], gap_type="practice", target_level=2))
        self.finish(repeat)
        self.assertEqual(self.repo.get_capability("SQL")["level"], 1)
        self.assertEqual(self.repo.list_events(event_type="CAPABILITY_LEVEL_CHANGED"), [])

    def test_one_practice_completion_no_promotion(self):
        self.finish(self.first())
        self.assertEqual(self.repo.get_capability("SQL")["level"], 1)

    def test_two_practice_completions_promote(self):
        a, b, _, second = self.two(1)
        self.assertEqual((a["gap_type"], b["target_level"]), ("practice", 2))
        self.assertEqual(self.repo.get_capability("SQL")["level"], 2)
        self.assertEqual(second["progression"]["previous_level"], 1)

    def test_experience_not_automatically_promoted(self):
        self.two(2)
        self.assertEqual(self.repo.get_capability("SQL")["level"], 2)
        self.assertEqual(self.repo.list_events(event_type="CAPABILITY_LEVEL_CHANGED"), [])

    def test_depth_not_automatically_promoted(self):
        self.repo.archive_jd(self.jd_id)
        self.repo.add_jd(TargetJD("虚构", "测试", "depth", {"capabilities": [requirement(level=4)]}))
        self.two(3)
        self.assertEqual(self.repo.get_capability("SQL")["level"], 3)

    def test_partial_does_not_reduce_level(self):
        self.finish(self.first(), "partial", "有一部分尚未完成")
        self.assertEqual(self.repo.get_capability("SQL")["level"], 1)

    def test_not_completed_does_not_reduce_level(self):
        self.finish(self.first(), "not_completed", "今天没时间")
        self.assertEqual(self.repo.get_capability("SQL")["level"], 1)

    def test_change_event_payload_and_evidence_ids(self):
        a, b, _, _ = self.two(1)
        events = self.repo.list_events(event_type="CAPABILITY_LEVEL_CHANGED")
        self.assertEqual(len(events), 1)
        payload = events[0]["payload_json"]
        self.assertEqual(payload["evidence_task_ids"], [a["id"], b["id"]])
        self.assertEqual((payload["capability"], payload["previous_level"], payload["new_level"]), ("SQL", 1, 2))
        self.assertTrue(payload["created_at"])
        self.assertIn("用户报告", payload["reason"])
        self.assertIn("self-reported", payload["source"])

    def test_level_event_failure_rolls_back_level_and_feedback(self):
        a = self.first(); b = self.finish(a)["replanning"]["selected_task"]
        before = self.repo.get_evidence(self.cap["id"])
        original = self.repo.append_event
        def failing(event):
            if event.event_type == EventType.CAPABILITY_LEVEL_CHANGED:
                raise sqlite3.OperationalError("synthetic failure")
            return original(event)
        with patch.object(self.repo, "append_event", side_effect=failing):
            with self.assertRaises(BusinessError):
                self.finish(b)
        self.assertEqual(self.repo.get_capability("SQL")["level"], 1)
        self.assertEqual(self.repo.get_task(b["id"])["status"], "pending")
        self.assertEqual(self.repo.get_evidence(self.cap["id"]), before)
        self.assertEqual(len(self.repo.list_events(event_type="TASK_COMPLETED")), 1)

    def test_recompute_observes_promoted_state(self):
        _, _, _, result = self.two(1)
        top = result["replanning"]["top_priority"]
        self.assertEqual(top["current_level"], 2)
        self.assertEqual(top["gap_severity"], 0.25)
        self.assertEqual(self.calls[-1][1]["top_priority"]["next_gap_type"], "experience")
        events = self.repo.list_events()
        change = next(e for e in events if e["event_type"] == "CAPABILITY_LEVEL_CHANGED")
        replan = events[-1]
        self.assertGreater(replan["id"], change["id"])

    def test_promotion_can_switch_priority(self):
        self.repo.archive_jd(self.jd_id)
        self.repo.upsert_capability(Capability("Data Analysis", 1))
        self.repo.add_jd(TargetJD("虚构", "数据岗位", "虚构要求", {"capabilities": [
            requirement("SQL", 2), requirement("Data Analysis", 2, "important")]}))
        _, _, first, second = self.two(1)
        self.assertEqual(first["replanning"]["top_priority"]["capability"], "SQL")
        self.assertEqual(second["replanning"]["selected_task"]["capability"], "Data Analysis")

    def test_no_promotion_still_replans_from_feedback(self):
        task = self.first(); result = self.finish(task, "partial", "JOIN 完成，correlated subquery 还不会")
        self.assertIsNone(result["progression"])
        self.assertIn("correlated subquery", result["replanning"]["selected_task"]["task_text"])

    def test_unknown_legacy_stage_not_counted(self):
        for i in range(2):
            task = self.tasks.create_task(Task("SQL", f"完成第{i}个虚构历史练习并保存结果", "虚构练习用于兼容性测试。", "30 min", ["保存代码和正确结果"]))
            self.finish(task)
        self.assertEqual(self.repo.get_capability("SQL")["level"], 1)

    def test_completed_without_feedback_evidence_not_counted(self):
        for i in range(2):
            self.repo.create_task(Task("SQL", f"虚构练习{i}", status="completed", gap_type="practice", target_level=2))
        with self.repo.transaction():
            self.assertIsNone(progress_capability(self.repo, "SQL"))
        self.assertEqual(self.repo.get_capability("SQL")["level"], 1)

    def test_other_capability_tasks_not_counted(self):
        self.repo.upsert_capability(Capability("Evaluation", 1))
        task = self.tasks.create_task(Task("Evaluation", "完成虚构评估练习并保存结果以供核对", "评估能力阶段性实践练习。", "30 min", ["保存结果并核对"], gap_type="practice", target_level=2))
        self.finish(task)
        self.finish(self.repo.pending_tasks()[0])
        self.assertEqual(self.repo.get_capability("SQL")["level"], 1)

    def test_invalid_stage_pair_rejected(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.repo.create_task(Task("SQL", "bad pair", gap_type="experience", target_level=2))

    def test_partial_completions_do_not_count(self):
        a = self.first(); b = self.finish(a, "partial", "部分完成")["replanning"]["selected_task"]
        self.finish(b)
        self.assertEqual(self.repo.get_capability("SQL")["level"], 1)
