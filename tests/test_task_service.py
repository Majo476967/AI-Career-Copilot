import json
import sqlite3
from unittest.mock import patch
from core.errors import BusinessError
from core.router import EventRouter
from core.schemas import Capability, Event, EventType, TargetJD, Task, UserProfile
from tests.phase3_fixtures import requirement
from tests.phase4_fixtures import Phase4Case


class TaskLoopTests(Phase4Case):
    def test_creation_event_and_task(self):
        task = self.first()
        self.assertEqual(self.repo.get_task(task["id"]), task)
        event = self.repo.task_creation_event(task["id"])
        self.assertEqual(event["payload_json"]["capability"], "SQL")
        self.assertEqual(event["payload_json"]["planning_basis"]["next_gap_type"], "practice")

    def test_complete_snapshot_selected_task(self):
        task = self.first()
        snapshot = self.repo.list_snapshots()[0]
        self.assertEqual(snapshot["selected_task_json"], task)
        self.assertEqual(snapshot["priority_result_json"]["planning"]["status"], "created")
        self.assertTrue(snapshot["created_at"])

    def test_duplicate_pending_rejected(self):
        task = self.first()
        with self.assertRaises(BusinessError) as caught:
            self.tasks.create_task(Task("SQL", "  " + task["task_text"].upper() + "  ", task["reason"],
                                        task["estimated_time"], task["acceptance_criteria_json"]))
        self.assertEqual(caught.exception.code, "duplicate_pending_task")
        self.assertEqual(len(self.repo.pending_tasks()), 1)

    def test_historical_completed_allows_future_same_text(self):
        task = self.first()
        self.repo.update_task_status(task["id"], "completed")
        new = self.tasks.create_task(Task("SQL", task["task_text"], task["reason"], task["estimated_time"], task["acceptance_criteria_json"]))
        self.assertNotEqual(new["id"], task["id"])
        self.assertEqual(self.repo.get_task(task["id"])["status"], "completed")

    def test_completed_saves_status_and_event(self):
        task = self.first()
        result = self.tasks.submit_task_feedback(task["id"], "completed")
        self.assertEqual(result["status"], "feedback_saved")
        self.assertEqual(self.repo.get_task(task["id"])["status"], "completed")
        event = self.repo.list_events(event_type="TASK_COMPLETED")[0]
        self.assertEqual(event["payload_json"]["previous_status"], "pending")
        self.assertEqual(event["payload_json"]["new_status"], "completed")
        self.assertEqual(event["payload_json"]["feedback"], "")

    def test_completed_evidence_traceable(self):
        task = self.first()
        self.tasks.submit_task_feedback(task["id"], "completed", "结果已保存")
        evidence = self.repo.get_evidence(self.cap["id"])[-1]
        self.assertEqual(evidence["evidence_type"], "task_result")
        self.assertEqual(evidence["source"], "task")
        self.assertEqual(evidence["source_id"], str(task["id"]))
        self.assertEqual(json.loads(evidence["content"])["feedback"], "结果已保存")
        self.assertTrue(evidence["created_at"])

    def test_no_automatic_level_upgrade(self):
        task = self.first()
        before = self.repo.get_capability("SQL")
        self.tasks.submit_task_feedback(task["id"], "completed")
        self.assertEqual(self.repo.get_capability("SQL"), before)

    def test_completed_replans_and_does_not_repeat(self):
        task = self.first()
        result = self.tasks.submit_task_feedback(task["id"], "completed")
        new = result["replanning"]["selected_task"]
        self.assertNotEqual(new["task_key"], task["task_key"])
        self.assertEqual(len(self.calls), 2)
        self.assertEqual(self.repo.list_snapshots()[0]["trigger"], "TASK_COMPLETED")

    def test_repeated_generated_task_rejected(self):
        task = self.first()
        self.planner.request = lambda *args: json.dumps({"capability": "SQL", "task": task["task_text"],
            "reason": task["reason"], "estimated_time": "30 min", "acceptance_criteria": task["acceptance_criteria_json"]})
        result = self.tasks.submit_task_feedback(task["id"], "completed")
        self.assertEqual(result["replanning"]["error_code"], "duplicate_recent_task")
        self.assertEqual(self.repo.pending_tasks(), [])

    def test_partial_requires_reason(self):
        task = self.first()
        with self.assertRaises(BusinessError):
            self.tasks.submit_task_feedback(task["id"], "partial", "  ")
        self.assertEqual(self.repo.get_task(task["id"])["status"], "pending")
        self.assertEqual(self.repo.list_events(event_type="TASK_PARTIAL"), [])

    def test_partial_event_and_raw_feedback(self):
        task = self.first(); feedback = "JOIN 完成了，但 correlated subquery 不会。"
        self.tasks.submit_task_feedback(task["id"], "partial", feedback)
        event = self.repo.list_events(event_type="TASK_PARTIAL")[0]
        self.assertEqual(event["payload_json"]["feedback"], feedback)
        self.assertEqual(self.repo.get_task(task["id"])["status"], "partial")

    def test_partial_evidence_does_not_invent(self):
        task = self.first(); feedback = "有一部分没做完。"
        self.tasks.submit_task_feedback(task["id"], "partial", feedback)
        content = json.loads(self.repo.get_evidence(self.cap["id"])[-1]["content"])
        self.assertEqual(content["feedback"], feedback)
        self.assertEqual(content["reported_status"], "partial")
        self.assertNotIn("correlated", str(content))

    def test_partial_context_and_new_task_use_explicit_blocker(self):
        task = self.first(); feedback = "JOIN 完成了，但 correlated subquery 不会。"
        result = self.tasks.submit_task_feedback(task["id"], "partial", feedback)
        self.assertEqual(self.calls[-1][1]["latest_feedback"]["feedback"], feedback)
        self.assertIn("correlated subquery", result["replanning"]["selected_task"]["task_text"])
        self.assertNotEqual(result["replanning"]["selected_task"]["task_key"], task["task_key"])

    def test_not_completed_requires_reason(self):
        task = self.first()
        with self.assertRaises(BusinessError):
            self.tasks.submit_task_feedback(task["id"], "not_completed")
        self.assertEqual(self.repo.list_events(event_type="TASK_NOT_COMPLETED"), [])

    def test_not_completed_event_and_evidence(self):
        task = self.first(); reason = "今天时间不足。"
        self.tasks.submit_task_feedback(task["id"], "not_completed", reason)
        self.assertEqual(self.repo.list_events(event_type="TASK_NOT_COMPLETED")[0]["payload_json"]["feedback"], reason)
        evidence = json.loads(self.repo.get_evidence(self.cap["id"])[-1]["content"])
        self.assertEqual(evidence["reported_status"], "not_completed")
        self.assertEqual(evidence["feedback"], reason)

    def test_not_completed_reason_reaches_planner_and_smaller_task(self):
        task = self.first(); reason = "今天时间不足。"
        result = self.tasks.submit_task_feedback(task["id"], "not_completed", reason)
        self.assertEqual(self.calls[-1][1]["latest_feedback"]["feedback"], reason)
        new = result["replanning"]["selected_task"]
        self.assertEqual(new["estimated_time"], "5 min")
        self.assertNotEqual(new["task_key"], task["task_key"])

    def test_missing_task_rejected(self):
        with self.assertRaises(BusinessError) as caught:
            self.tasks.submit_task_feedback(999, "completed")
        self.assertEqual(caught.exception.code, "task_missing")
        self.assertEqual(self.repo.list_events(), [])

    def test_superseded_feedback_rejected(self):
        task = self.first(); self.repo.update_task_status(task["id"], "superseded")
        with self.assertRaises(BusinessError):
            self.tasks.submit_task_feedback(task["id"], "completed")
        self.assertEqual(self.repo.list_events(event_type="TASK_COMPLETED"), [])

    def test_duplicate_feedback_rejected_without_duplicate_event(self):
        task = self.first(); self.tasks.submit_task_feedback(task["id"], "completed")
        before = self.repo.list_events()
        with self.assertRaises(BusinessError):
            self.tasks.submit_task_feedback(task["id"], "completed")
        self.assertEqual(self.repo.list_events(), before)

    def test_valid_pending_retained_no_model_call(self):
        task = self.first(); result = self.planning.recompute("JD_ADDED")
        self.assertEqual(result["planning_status"], "retained")
        self.assertEqual(result["selected_task"], task)
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(len(self.repo.list_events(event_type="TASK_CREATED")), 1)

    def test_priority_change_supersedes(self):
        task = self.first(); self.repo.archive_jd(self.jd_id)
        self.repo.add_jd(TargetJD("虚构二公司", "评估", "虚构评估要求", {"capabilities": [requirement("Evaluation", 4)]}))
        result = self.planning.recompute("JD_REPLACED")
        self.assertEqual(self.repo.get_task(task["id"])["status"], "superseded")
        self.assertEqual(result["selected_task"]["capability"], "Evaluation")
        self.assertEqual(self.repo.list_snapshots()[0]["selected_task_json"], self.repo.pending_tasks()[0])

    def test_changed_level_invalidates_old_task(self):
        task = self.first(); self.repo.upsert_capability(Capability("SQL", 2))
        result = self.planning.recompute("PROFILE_CONFIRMED")
        self.assertEqual(self.repo.get_task(task["id"])["status"], "superseded")
        self.assertEqual(result["top_priority"]["next_gap_type"], "experience")

    def test_no_top_priority_supersedes_without_fake_task(self):
        task = self.first(); self.repo.archive_jd(self.jd_id)
        result = self.planning.recompute("JD_ARCHIVED")
        self.assertIsNone(result["selected_task"])
        self.assertEqual(self.repo.get_task(task["id"])["status"], "superseded")
        self.assertIsNone(self.repo.list_snapshots()[0]["selected_task_json"])
        self.assertEqual(len(self.calls), 1)

    def test_feedback_event_failure_rolls_back_all_core_writes(self):
        task = self.first(); evidence_before = self.repo.get_evidence(self.cap["id"])
        with patch.object(self.repo, "append_event", side_effect=sqlite3.OperationalError("fail")):
            with self.assertRaises(BusinessError):
                self.tasks.submit_task_feedback(task["id"], "completed")
        self.assertEqual(self.repo.get_task(task["id"])["status"], "pending")
        self.assertEqual(self.repo.get_evidence(self.cap["id"]), evidence_before)

    def test_evidence_failure_rolls_back_feedback_and_event(self):
        task = self.first()
        with patch.object(self.repo, "add_evidence", side_effect=sqlite3.OperationalError("fail")):
            with self.assertRaises(BusinessError):
                self.tasks.submit_task_feedback(task["id"], "completed")
        self.assertEqual(self.repo.get_task(task["id"])["status"], "pending")
        self.assertEqual(self.repo.list_events(event_type="TASK_COMPLETED"), [])

    def test_planner_failure_preserves_feedback_and_records_retry(self):
        task = self.first()
        self.planner.request = lambda *args: (_ for _ in ()).throw(RuntimeError("fail"))
        result = self.tasks.submit_task_feedback(task["id"], "completed", "真实反馈")
        self.assertTrue(result["replanning"]["needs_retry"])
        self.assertEqual(self.repo.get_task(task["id"])["status"], "completed")
        self.assertEqual(self.repo.pending_tasks(), [])
        self.assertEqual(len(self.repo.list_events(event_type="TASK_COMPLETED")), 1)
        self.assertEqual(len(self.repo.list_events(event_type="TASK_CREATED")), 1)
        self.assertTrue(self.repo.list_events(event_type="REPLAN")[-1]["payload_json"]["needs_retry"])

    def test_snapshot_failure_does_not_lose_feedback_or_create_task(self):
        task = self.first()
        with patch.object(self.repo, "create_snapshot", side_effect=sqlite3.OperationalError("fail")):
            result = self.tasks.submit_task_feedback(task["id"], "partial", "需要拆分任务")
        self.assertTrue(result["replanning"]["needs_retry"])
        self.assertEqual(self.repo.get_task(task["id"])["status"], "partial")
        self.assertEqual(self.repo.pending_tasks(), [])
        self.assertEqual(len(self.repo.list_events(event_type="TASK_CREATED")), 1)

    def test_retry_after_planner_failure(self):
        task = self.first()
        original = self.planner.request
        self.planner.request = lambda *args: "invalid"
        self.tasks.submit_task_feedback(task["id"], "completed")
        self.planner.request = original
        result = self.planning.recompute("retry")
        self.assertEqual(result["planning_status"], "created")
        self.assertEqual(len(self.repo.list_events(event_type="TASK_COMPLETED")), 1)

    def test_context_failure_preserves_feedback(self):
        task = self.first()
        with patch.object(self.memory, "build_context", side_effect=ValueError("fail")):
            result = self.tasks.submit_task_feedback(task["id"], "completed")
        self.assertTrue(result["replanning"]["needs_retry"])
        self.assertEqual(self.repo.get_task(task["id"])["status"], "completed")

    def test_router_three_feedback_events(self):
        router = EventRouter(self.planning)
        for event in ("TASK_COMPLETED", "TASK_PARTIAL", "TASK_NOT_COMPLETED"):
            with self.subTest(event=event):
                result = router.dispatch(event)
                self.assertFalse(result["needs_retry"])
                self.assertEqual(self.repo.list_snapshots()[0]["trigger"], event)

    def test_router_ignores_creation_and_replan(self):
        router = EventRouter(self.planning)
        for event in ("TASK_CREATED", "REPLAN", "OTHER"):
            self.assertEqual(router.dispatch(event)["status"], "ignored")
        self.assertEqual(self.repo.list_snapshots(), [])
        self.assertEqual(self.calls, [])

    def test_state_changed_during_model_call_is_not_overwritten(self):
        original = self.planner.request
        def changed(system, text):
            response = original(system, text)
            self.repo.upsert_capability(Capability("SQL", 2))
            return response
        self.planner.request = changed
        result = self.planning.recompute()
        self.assertEqual(result["error_code"], "stale_state")
        self.assertEqual(self.repo.pending_tasks(), [])
        self.assertEqual(self.repo.get_capability("SQL")["level"], 2)

    def test_zero_time_budget(self):
        self.repo.upsert_profile(UserProfile(available_hours_per_day=0))
        result = self.planning.recompute()
        self.assertEqual(result["planning_status"], "no_time_budget")
        self.assertIsNone(result["selected_task"])
        self.assertEqual(self.calls, [])

    def test_jd_hook_commits_before_model_and_survives_failure(self):
        from services.jd_service import JDService
        from tests.phase2_fixtures import jd_input, jd_output
        self.planner.request = lambda *args: "invalid"
        self.blocker.side_effect = None
        self.blocker.return_value = json.dumps(jd_output())
        service = JDService(self.repo, event_router=EventRouter(self.planning))
        added = service.add_jd(jd_input())
        self.assertEqual(self.repo.get_jd(added["id"])["status"], "active")
        self.assertEqual(len(self.repo.list_events(event_type="JD_ADDED")), 1)
        self.assertTrue(self.repo.list_events(event_type="REPLAN")[-1]["payload_json"]["needs_retry"])

    def test_failed_replacement_retains_old_task_and_history(self):
        task = self.first(); self.repo.upsert_capability(Capability("SQL", 2))
        self.planner.request = lambda *args: "invalid"
        result = self.planning.recompute("PROFILE_CONFIRMED")
        self.assertTrue(result["needs_retry"])
        self.assertEqual(self.repo.get_task(task["id"]), task)
        self.assertEqual(len(self.repo.list_events(event_type="TASK_CREATED")), 1)

    def test_late_feedback_orders_recent_tasks_by_event(self):
        task = self.first()
        for i in range(6):
            other = self.repo.create_task(Task("SQL", f"虚构历史练习 {i}", status="completed"))
            self.repo.append_event(Event(EventType.TASK_COMPLETED, "task", str(other), {"capability": "SQL"}))
        self.tasks.submit_task_feedback(task["id"], "completed")
        self.assertEqual(self.repo.recent_terminal_tasks("SQL")[0]["id"], task["id"])

    def test_reduced_time_budget_replaces_task(self):
        task = self.first(); self.repo.upsert_profile(UserProfile(available_hours_per_day=0.1))
        self.planner.request = lambda *args: json.dumps({"capability": "SQL",
            "task": "完成一道五分钟查询练习，保存代码和结果", "reason": "时间预算减少，缩小为单题可验收练习。",
            "estimated_time": "5 min", "acceptance_criteria": ["保存查询和正确结果"]})
        result = self.planning.recompute("PROFILE_CONFIRMED")
        self.assertEqual(self.repo.get_task(task["id"])["status"], "superseded")
        self.assertEqual(result["selected_task"]["estimated_time"], "5 min")
