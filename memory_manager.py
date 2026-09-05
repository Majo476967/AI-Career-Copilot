import json
import os


MEMORY_FILE = os.path.join(
    os.path.dirname(__file__),
    "memory",
    "user_state.json"
)


def load_memory():
    """读取用户Memory"""

    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_memory(memory):
    """保存用户Memory"""

    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(
            memory,
            f,
            ensure_ascii=False,
            indent=4
        )


def update_task_feedback(task, status, feedback=""):
    """
    根据用户任务反馈更新Memory。

    status只允许：
    completed
    partial
    not_completed
    """

    memory = load_memory()

    if status not in [
        "completed",
        "partial",
        "not_completed"
    ]:
        raise ValueError(
            "status必须是 completed、partial 或 not_completed"
        )

    record = {
        "task": task,
        "status": status,
        "feedback": feedback
    }

    memory["task_history"].append(record)

    # 已完成
    if status == "completed":

        if task not in memory["completed_tasks"]:
            memory["completed_tasks"].append(task)

        if task in memory["pending_tasks"]:
            memory["pending_tasks"].remove(task)

    # 部分完成
    elif status == "partial":

        if task not in memory["pending_tasks"]:
            memory["pending_tasks"].append(task)

    # 未完成
    elif status == "not_completed":

        if task not in memory["pending_tasks"]:
            memory["pending_tasks"].append(task)

    save_memory(memory)

    return memory