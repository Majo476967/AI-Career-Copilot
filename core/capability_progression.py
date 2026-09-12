"""Conservative, deterministic progression from accumulated self-reported evidence."""
from core import config
from core.schemas import Capability, Event, EventType
from storage.repository import utc_now


def progress_capability(repository, name):
    if not repository.connection.in_transaction:
        raise RuntimeError("Progression must share the feedback transaction")
    capability = repository.get_capability(name)
    previous = capability["level"]
    if previous not in (0, 1):
        return None
    target = previous + 1
    gap_type = "evidence_knowledge_verification" if previous == 0 else "practice"
    threshold = (config.KNOWLEDGE_PROMOTION_COMPLETIONS if previous == 0
                 else config.PRACTICE_PROMOTION_COMPLETIONS)
    # Even an erroneous config must never enable single-task promotion.
    if type(threshold) is not int or threshold < 2:
        raise ValueError("Promotion threshold must be an integer >= 2")
    tasks = repository.progression_tasks(name, target, gap_type, threshold)
    if len(tasks) < threshold:
        return None
    payload = {"capability": name, "previous_level": previous, "new_level": target,
        "evidence_task_ids": [task["id"] for task in tasks], "created_at": utc_now(),
        "source": "self-reported completion evidence",
        "reason": "根据用户报告的任务完成情况，当前积累了足够的阶段性能力 Evidence；非客观考试认证。"}
    repository.upsert_capability(Capability(name, target))
    event_id = repository.append_event(Event(EventType.CAPABILITY_LEVEL_CHANGED, "capability", str(capability["id"]), payload))
    return {**payload, "event_id": event_id}
