import json
from unittest.mock import Mock, patch
from core.errors import BusinessError
from core.schemas import Capability
from tests.phase2_fixtures import jd_input, jd_output, profile, RESUME
from tests.phase4_fixtures import Phase4Case
from ui.adapter import ProductAdapter, level_label, validate_feedback, run_once, profile_changes


class UIAdapterTests(Phase4Case):
    def ui(self):
        return ProductAdapter(self.repo, planning=self.planning)

    def test_dashboard_uses_existing_priority(self):
        vm = self.ui().dashboard()
        self.assertEqual(vm["priority"], self.planning.get_priority())
        self.assertEqual(vm["priority"]["top_priority"]["capability"], "SQL")
        self.assertIn("1/1", vm["explanation"])

    def test_dashboard_reads_do_not_create_events_or_call_model(self):
        before = self.repo.list_events()
        for _ in range(3):
            self.ui().dashboard()
        self.assertEqual(self.repo.list_events(), before)
        self.assertEqual(self.repo.list_snapshots(), [])
        self.assertEqual(self.calls, [])
        self.blocker.assert_not_called()

    def test_level_zero_chinese(self):
        self.assertIn("证据不足", level_label(0))
        self.assertNotIn("能力弱", level_label(0))

    def test_active_jd_summary(self):
        self.assertEqual(self.ui().job_summary()[0]["岗位覆盖"], "1/1")
        self.assertEqual(self.ui().job_summary()[0]["能力"], "SQL")

    def test_completed_feedback_optional(self):
        validate_feedback("completed", "")

    def test_partial_feedback_required(self):
        with self.assertRaises(BusinessError):
            validate_feedback("partial", " ")

    def test_not_completed_feedback_required(self):
        with self.assertRaises(BusinessError):
            validate_feedback("not_completed", "")

    def test_no_profile_empty_state(self):
        self.connection.execute("DELETE FROM user_profile")
        self.assertIn("上传简历", self.ui().dashboard()["empty_message"])
        self.assertFalse(self.ui().dashboard()["profile_confirmed"])

    def test_no_jobs_empty_state(self):
        self.repo.archive_jd(self.jd_id)
        self.assertIn("添加至少一个", self.ui().dashboard()["empty_message"])

    def test_no_positive_gap_empty_state(self):
        self.repo.upsert_capability(Capability("SQL", 3))
        self.assertIn("没有识别到", self.ui().dashboard()["empty_message"])

    def test_unconfirmed_draft_is_not_current(self):
        self.connection.execute("DELETE FROM user_profile")
        draft_id = self.repo.create_profile_draft(RESUME, "fictional", profile())
        vm = self.ui().profile()
        self.assertIsNone(vm["current"])
        self.assertEqual(vm["drafts"][0]["id"], draft_id)
        self.assertFalse(self.ui().dashboard()["profile_confirmed"])

    def test_archived_job_excluded(self):
        self.repo.archive_jd(self.jd_id)
        self.assertEqual(self.ui().jobs.list_active_jds(), [])
        self.assertEqual(len(self.ui().jobs.list_archived_jds()), 1)
        self.assertEqual(self.ui().job_summary(), [])

    def test_rerun_action_success_executes_once(self):
        state = {}; operation = Mock(return_value={"saved": True})
        self.assertEqual(run_once(state, "key", operation), run_once(state, "key", operation))
        operation.assert_called_once()

    def test_failed_action_can_retry(self):
        state = {}; operation = Mock(side_effect=[BusinessError("fail", "fail"), "saved"])
        with self.assertRaises(BusinessError):
            run_once(state, "key", operation)
        self.assertEqual(run_once(state, "key", operation), "saved")
        self.assertEqual(operation.call_count, 2)

    def test_saved_feedback_not_resubmitted_after_planner_failure(self):
        task = self.first(); self.planner.request = lambda *args: "invalid"
        state = {}; ui = self.ui()
        action = lambda: ui.feedback(task["id"], "completed", "已完成")
        result = run_once(state, "feedback", action)
        self.assertTrue(result["replanning"]["needs_retry"])
        run_once(state, "feedback", action)
        self.assertEqual(len(self.repo.list_events(event_type="TASK_COMPLETED")), 1)
        self.assertTrue(ui.dashboard()["needs_retry"])
        self.assertIsNone(ui.dashboard()["task"])

    def test_profile_form_preserves_evidence(self):
        draft = {"draft_json": profile()}
        fields = {"education": "人工修正教育", "internships": "", "projects": "", "skills": "SQL",
                  "major": "测试专业", "target_direction": "数据岗位", "available_hours_per_day": 2.0}
        rows = [{"保留": True, "能力": "SQL", "等级": "1 · 知识理解"}]
        data = profile_changes(draft, fields, rows)
        self.assertEqual(data["capabilities"][0]["evidence"], profile()["capabilities"][0]["evidence"])
        self.assertEqual(data["capabilities"][0]["level"], 1)
        self.assertEqual(data["education"], ["人工修正教育"])

    def test_jd_preview_does_not_write(self):
        self.blocker.side_effect = None; self.blocker.return_value = json.dumps(jd_output())
        ui = self.ui(); before = self.repo.list_jds()
        preview = ui.jobs.preview_jd(jd_input())
        self.assertEqual(self.repo.list_jds(), before)
        self.assertEqual(preview["analysis"]["company"], "虚构公司1")
        self.assertEqual(self.repo.list_events(), [])

    def test_confirm_preview_no_second_analysis(self):
        self.blocker.side_effect = None; self.blocker.return_value = json.dumps(jd_output())
        ui = self.ui(); preview = ui.jobs.preview_jd(jd_input())
        result = ui.jobs.add_jd(prepared=preview, company="人工修正公司", job_title="人工修正岗位")
        self.assertEqual(self.blocker.call_count, 1)
        self.assertEqual(result["company"], "人工修正公司")
        self.assertEqual(result["job_title"], "人工修正岗位")

    def test_replace_preview_preserves_old_job(self):
        self.blocker.side_effect = None; self.blocker.return_value = json.dumps(jd_output())
        ui = self.ui(); preview = ui.jobs.preview_jd(jd_input())
        new = ui.jobs.replace_jd(self.jd_id, prepared=preview)
        self.assertEqual(ui.jobs.get_jd(self.jd_id)["status"], "archived")
        self.assertEqual(ui.jobs.list_active_jds()[0]["id"], new["id"])
        self.assertEqual(self.blocker.call_count, 1)

    def test_preview_modified_evidence_rejected(self):
        self.blocker.side_effect = None; self.blocker.return_value = json.dumps(jd_output())
        ui = self.ui(); preview = ui.jobs.preview_jd(jd_input())
        preview["analysis"]["capabilities"][0]["evidence"] = "原文不存在的证据"
        with self.assertRaises(BusinessError):
            ui.jobs.add_jd(prepared=preview)

    def test_task_and_feedback_history(self):
        task = self.first(); self.ui().feedback(task["id"], "partial", "还有待完成部分")
        history = self.ui().history()
        old = next(t for t in history["tasks"] if t["id"] == task["id"])
        self.assertEqual(old["feedback"], "还有待完成部分")
        self.assertEqual(old["status"], "partial")
        self.assertTrue(history["snapshots"])
