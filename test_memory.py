from memory_manager import update_task_feedback

task = "通过一个具体案例梳理Agent如何判断和调用Tool"

result = update_task_feedback(
    task,
    "completed",
    "已经能够完整解释用户请求、Agent判断、Tool选择、Tool调用、结果返回和后续决策的基本流程"
)

print("Memory更新成功：")
print(result)