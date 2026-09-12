"""Read confirmed state, compute deterministic priority, save a task-free snapshot."""
from contextlib import nullcontext
from core.schemas import PlanningSnapshot
from core.priority_engine import calculate_priorities, empty_result
from services.common import storage_errors


class PlanningService:
    def __init__(self, repository):
        self.repo = repository

    @storage_errors
    def recompute(self, trigger="manual"):
        if not isinstance(trigger, str) or not trigger.strip():
            return {**empty_result("invalid_input", "Snapshot trigger 必须为非空文本。"), "snapshot_id": None}
        # Reuse the transaction owned by an injected Profile/JD workflow.
        scope = nullcontext() if self.repo.connection.in_transaction else self.repo.transaction()
        with scope:
            profile = self.repo.get_profile()
            jds = self.repo.get_active_jds()
            capabilities = self.repo.get_capabilities()
            capability_state = [{**item, "evidence": self.repo.get_evidence(item["id"])} for item in capabilities]
            if profile is None:
                result = empty_result("no_confirmed_profile")
            else:
                result = calculate_priorities(jds, capabilities)
            result["warnings"] = []
            if profile is not None and not any(item["evidence"] for item in capability_state):
                result["warnings"].append("当前没有 Capability Evidence 记录，请补充证据；已有确认等级不会被本计算改写。")
            if result["status"] == "invalid_input":
                # Invalid input is not saved as a valid decision snapshot.
                result["snapshot_id"] = None
                return result
            snapshot_id = self.repo.create_snapshot(PlanningSnapshot(
                trigger=trigger, active_jds_json=jds, capability_state_json=capability_state,
                priority_result_json=result, selected_task_json=None, reason=result["reason"]))
            return {**result, "snapshot_id": snapshot_id}
