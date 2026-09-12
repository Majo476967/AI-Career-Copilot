"""Small offline rendering smoke tests, not full browser automation."""
from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from tests.phase4_fixtures import Phase4Case
from tests.phase2_fixtures import profile, RESUME

APP = Path(__file__).resolve().parents[1] / "app.py"


class StreamlitSmokeTests(Phase4Case):
    def app(self):
        setting = patch.dict("os.environ", {"CAREER_COPILOT_DB": str(self.path)})
        setting.start(); self.addCleanup(setting.stop)
        return AppTest.from_file(str(APP), default_timeout=30)

    def test_empty_dashboard_renders_offline(self):
        self.connection.execute("DELETE FROM user_profile")
        app = self.app().run()
        self.assertFalse(app.exception)
        self.assertFalse(app.error)
        self.assertTrue(any("上传简历" in item.value for item in app.info))
        self.blocker.assert_not_called()

    def test_all_four_pages_rerun_without_model(self):
        self.first(); before = self.repo.event_head()
        app = self.app().run()
        for name in ["我的档案", "目标岗位", "进度与历史", "首页"]:
            app.sidebar.radio[0].set_value(name).run()
            self.assertFalse(app.exception, name)
            self.assertFalse(app.error, name)
        self.assertEqual(self.repo.event_head(), before)
        self.blocker.assert_not_called()

    def test_profile_draft_form_renders_without_confirming(self):
        self.repo.create_profile_draft(RESUME, "fictional", profile())
        app = self.app().run()
        app.sidebar.radio[0].set_value("我的档案").run()
        self.assertFalse(app.exception)
        self.assertFalse(app.error)
        self.assertTrue(any("草稿" in item.value for item in app.warning))
        self.assertEqual(len(self.repo.open_profile_drafts()), 1)
        self.assertEqual(self.repo.list_events(), [])

    def test_partial_submit_validation_and_rerun_safety(self):
        task = self.first()
        app = self.app().run()
        feedback_radio = next(r for r in app.radio if r.label == "完成情况")
        feedback_radio.set_value("partial")
        next(b for b in app.button if b.label == "提交反馈").click().run()
        self.assertTrue(app.error)
        self.assertEqual(self.repo.get_task(task["id"])["status"], "pending")
        self.blocker.assert_not_called()
        self.blocker.side_effect = self.task_request
        next(t for t in app.text_area if t.label == "执行反馈").set_value("JOIN 已完成，correlated subquery 还不会")
        next(b for b in app.button if b.label == "提交反馈").click().run()
        self.assertFalse(app.exception)
        self.assertFalse(app.error)
        self.assertEqual(self.repo.get_task(task["id"])["status"], "partial")
        before = self.repo.event_head()
        calls = self.blocker.call_count
        app.run()
        self.assertEqual(self.repo.event_head(), before)
        self.assertEqual(self.blocker.call_count, calls)
        self.assertEqual(len(self.repo.list_events(event_type="TASK_PARTIAL")), 1)

    def test_profile_form_confirmation_persists(self):
        draft_id = self.repo.create_profile_draft(RESUME, "fictional", profile())
        app = self.app().run()
        app.sidebar.radio[0].set_value("我的档案").run()
        self.blocker.side_effect = self.task_request
        next(b for b in app.button if b.label == "确认并更新正式档案").click().run()
        self.assertFalse(app.exception)
        self.assertFalse(app.error)
        self.assertEqual(self.repo.get_profile_draft(draft_id)["status"], "confirmed")
        before = self.repo.event_head()
        app.run()
        self.assertEqual(self.repo.event_head(), before)
