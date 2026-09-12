import json
from unittest.mock import patch
from core import config
from core.planner import PROMPT
from core.priority_engine import calculate_priorities
from core.schemas import Event, EventType, MemorySummary, TargetJD
from tests.phase3_fixtures import requirement
from tests.phase4_fixtures import Phase4Case


class MemoryServiceTests(Phase4Case):
    def events(self, count, capability="SQL", feedback="虚构反馈"):
        return [self.repo.append_event(Event(EventType.TASK_COMPLETED, "task", "999", {
            "capability": capability, "task_text": "虚构任务练习记录", "feedback": feedback})) for _ in range(count)]

    def context(self):
        priority = calculate_priorities(self.repo.get_active_jds(), self.repo.get_capabilities())
        return self.memory.build_context(priority, self.repo.get_profile())

    def test_related_only(self):
        ids = self.events(1); self.events(4, "Evaluation", "不相关反馈")
        context = self.context()
        self.assertEqual([e["event_id"] for e in context["history"]], ids)
        self.assertNotIn("不相关反馈", json.dumps(context, ensure_ascii=False))

    def test_latest_five_only(self):
        ids = self.events(25)
        self.assertEqual([e["event_id"] for e in self.context()["history"]], list(reversed(ids[-5:])))

    def test_archived_jd_excluded(self):
        jd = self.repo.add_jd(TargetJD("虚构", "归档", "归档文本", {"capabilities": [requirement(evidence="归档文本")]}))
        self.repo.archive_jd(jd)
        self.assertNotIn("归档文本", json.dumps(self.context(), ensure_ascii=False))

    def test_feedback_budget_preserves_original(self):
        text = "长反馈" * 5000; ids = self.events(1, feedback=text)
        self.assertLessEqual(len(self.context()["latest_feedback"]["feedback"]), config.FEEDBACK_CONTEXT_MAX_CHARS)
        self.assertEqual(self.repo.list_events(after_id=ids[0]-1)[0]["payload_json"]["feedback"], text)

    def test_history_item_budget(self):
        self.events(5, feedback='\n"' * 5000)
        for row in self.context()["history"]:
            self.assertLessEqual(len(json.dumps(row, ensure_ascii=False)), config.HISTORY_ITEM_MAX_CHARS)

    def test_summary_budget_preserves_original(self):
        text = "摘要" * 5000; self.repo.upsert_summary(MemorySummary("SQL", text))
        self.assertLessEqual(len(self.context()["memory_summary"]), config.MEMORY_SUMMARY_MAX_CHARS)
        self.assertEqual(self.repo.get_summary("SQL")["summary"], text)

    def test_total_budget_valid_json(self):
        self.events(10, feedback='\n"' * 5000)
        self.repo.upsert_summary(MemorySummary("SQL", "摘要" * 5000))
        with patch.object(config, "PLANNER_CONTEXT_MAX_CHARS", 2200):
            context = self.context(); text = json.dumps(context, ensure_ascii=False)
            self.assertLessEqual(len(PROMPT) + len(text), 2200)
            self.assertEqual(json.loads(text)["top_priority"]["capability"], "SQL")
            self.assertTrue(context["context_truncated"])

    def test_queries_filter_and_limit(self):
        self.events(100); queries = []; self.connection.set_trace_callback(queries.append)
        try:
            self.context()
        finally:
            self.connection.set_trace_callback(None)
        history = [q for q in queries if "SELECT e.* FROM events" in q]
        self.assertTrue(history)
        for q in history:
            self.assertIn("LIMIT", q); self.assertIn("SQL", q)

    def test_threshold_and_watermark(self):
        ids = self.events(10); self.events(2, "Evaluation")
        self.assertEqual(self.memory.maybe_summarize("SQL")["status"], "updated")
        self.assertEqual(self.repo.get_summary("SQL")["covered_until_event_id"], ids[-1])
        self.assertEqual(len(self.summary_calls), 1)

    def test_below_threshold(self):
        self.events(9)
        self.assertEqual(self.memory.maybe_summarize("SQL")["status"], "below_threshold")
        self.assertEqual(self.summary_calls, [])

    def test_repeat_does_not_summarize_again(self):
        self.events(10); self.memory.maybe_summarize("SQL")
        before = self.repo.get_summary("SQL")
        self.memory.maybe_summarize("SQL")
        self.assertEqual(len(self.summary_calls), 1)
        self.assertEqual(self.repo.get_summary("SQL"), before)

    def test_incremental_only(self):
        self.events(10); self.memory.maybe_summarize("SQL")
        old = self.repo.get_summary("SQL")["summary"]; ids = self.events(10)
        self.memory.maybe_summarize("SQL")
        data = self.summary_calls[-1][1]
        self.assertEqual(data["previous_summary"], old)
        self.assertEqual([e["event_id"] for e in data["new_events"]], ids)

    def test_raw_history_retained(self):
        self.events(10); before = self.repo.list_events()
        self.memory.maybe_summarize("SQL")
        self.assertEqual(self.repo.list_events(), before)

    def test_summary_failure_preserves_watermark(self):
        self.events(10); self.memory.maybe_summarize("SQL")
        old = self.repo.get_summary("SQL"); self.events(10)
        self.memory.request = lambda *args: (_ for _ in ()).throw(RuntimeError("fail"))
        self.assertEqual(self.memory.maybe_summarize("SQL")["status"], "summary_failed")
        self.assertEqual(self.repo.get_summary("SQL"), old)

    def test_summary_failure_preserves_feedback(self):
        task = self.first(); self.events(9)
        self.memory.request = lambda *args: (_ for _ in ()).throw(RuntimeError("fail"))
        result = self.tasks.submit_task_feedback(task["id"], "completed", "保留反馈")
        self.assertEqual(result["summary"]["status"], "summary_failed")
        self.assertEqual(self.repo.get_task(task["id"])["status"], "completed")
        self.assertEqual(self.repo.capability_events("SQL", limit=1, feedback_only=True)[0]["payload_json"]["feedback"], "保留反馈")
        self.assertIsNone(self.repo.get_summary("SQL"))

    def test_bounded_batch(self):
        ids = self.events(50); self.memory.maybe_summarize("SQL")
        self.assertEqual(len(self.summary_calls[0][1]["new_events"]), 20)
        self.assertEqual(self.repo.get_summary("SQL")["covered_until_event_id"], ids[19])

    def test_retry_and_output_budget(self):
        self.events(10); self.memory.request = lambda *args: " "
        self.assertEqual(self.memory.maybe_summarize("SQL")["status"], "summary_failed")
        self.assertIsNone(self.repo.get_summary("SQL"))
        self.memory.request = lambda *args: "虚构摘要" * 5000
        self.assertEqual(self.memory.maybe_summarize("SQL")["status"], "updated")
        self.assertLessEqual(len(self.repo.get_summary("SQL")["summary"]), config.MEMORY_SUMMARY_MAX_CHARS)

    def test_latest_feedback_survives_new_creation_events(self):
        ids = self.events(1, feedback="明确卡点")
        for _ in range(8):
            self.repo.append_event(Event(EventType.TASK_CREATED, "task", "999", {"capability": "SQL"}))
        self.assertEqual(self.context()["latest_feedback"]["event_id"], ids[0])

    def test_aligned_level_with_legacy_alias(self):
        self.connection.execute("UPDATE user_capabilities SET capability_name='数据库查询' WHERE id=?", (self.cap["id"],))
        context = self.context()
        self.assertEqual(context["current_capability_state"]["level"], context["top_priority"]["current_level"])
        self.assertEqual(context["current_capability_state"]["level"], 1)
