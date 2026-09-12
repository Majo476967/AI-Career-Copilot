"""Offline Phase 4 fixtures: fictional state, isolated databases, fake model calls."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from core.planner import TaskPlanner
from core.schemas import Capability, Evidence, TargetJD, UserProfile
from services.memory_service import MemoryService
from services.planning_service import PlanningService
from services.task_service import TaskService
from storage.database import connect_database
from storage.repository import Repository
from tests.phase3_fixtures import requirement


def task_output(capability="SQL", text="完成三道 JOIN 查询练习并保存 SQL 文件和结果", minutes="30 min"):
    return {"capability": capability, "task": text, "reason": "针对当前下一等级设计可验收的实际练习。",
            "estimated_time": minutes, "acceptance_criteria": ["三道查询结果正确且已保存 SQL 与输出"]}


class Phase4Case(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "phase4.sqlite3"
        self.connection = connect_database(self.path)
        self.addCleanup(self.connection.close)
        self.repo = Repository(self.connection)
        self.repo.initialize()
        blocker = patch("llm.request_analysis", side_effect=AssertionError("Network forbidden in offline tests"))
        self.blocker = blocker.start()
        self.addCleanup(blocker.stop)
        self.repo.upsert_profile(UserProfile(education="虚构测试学院", available_hours_per_day=1))
        self.cap = self.repo.upsert_capability(Capability("SQL", 1))
        self.repo.add_evidence(Evidence(self.cap["id"], "skill", "虚构测试知识证据", "test", "fixture"))
        self.jd_id = self.repo.add_jd(TargetJD("虚构公司", "测试岗位", "虚构 SQL 要求",
                                               {"capabilities": [requirement(level=3)]}))
        self.calls, self.summary_calls = [], []
        self.memory = MemoryService(self.repo, request=self.summary_request)
        self.planner = TaskPlanner(request=self.task_request)
        self.planning = PlanningService(self.repo, enable_tasks=True, planner=self.planner, memory_service=self.memory)
        self.tasks = TaskService(self.repo, planning_service=self.planning)

    def task_request(self, system, text):
        self.assertFalse(self.connection.in_transaction)
        context = json.loads(text)
        self.calls.append((system, context))
        latest = context.get("latest_feedback") or {}
        feedback = latest.get("feedback", "")
        if "correlated subquery" in feedback:
            task = "完成一道 correlated subquery 分解练习，标注内外查询关联并保存结果"
        elif "时间不足" in feedback:
            task = "完成一道五分钟的前置查询小练习，保存查询与结果并核对"
        else:
            task = f"完成第 {len(self.calls)} 组查询练习，保存代码和结果并逐题核对"
        return json.dumps(task_output(context["top_priority"]["capability"], task,
                                     "5 min" if "时间不足" in feedback else "30 min"), ensure_ascii=False)

    def summary_request(self, system, text):
        self.assertFalse(self.connection.in_transaction)
        self.summary_calls.append((system, json.loads(text)))
        return "用户报告了相关任务执行情况；以原始事件中的具体反馈为准，不自动推断等级。"

    def first(self):
        result = self.planning.recompute()
        self.assertEqual(result["planning_status"], "created", result)
        return result["selected_task"]
