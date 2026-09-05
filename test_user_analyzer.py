from tools.user_analyzer import analyze_user
from memory_manager import load_memory


# 读取最新 Memory
user_state = load_memory()


# 用户初始画像
base_user_profile = """
我是软件工程专业大三学生。

掌握Python、Prompt Engineering，

做过企业RAG知识库问答助手，

项目中使用LangChain、FAISS、Embedding和豆包大模型。

有AI产品经理实习经历，

参与用户需求分析、竞品调研、产品流程设计、

AI产品方案设计和墨刀原型设计。

初始阶段刚开始学习Agent。

SQL和AI Evaluation基础相对薄弱。
"""


# 合并“初始画像 + 最新 Memory”
current_user_profile = f"""
【用户初始画像】

{base_user_profile}


【用户最新任务状态】

{user_state}


重要说明：

初始画像只代表用户最开始的状态。

completed_tasks、pending_tasks、task_history和feedback
代表用户之后最新发生的学习和执行情况。

如果初始画像和最新任务记录发生冲突，
必须以最新任务记录和feedback为准。

请分析用户“现在”的真实能力，
而不是只分析初始状态。
"""


result = analyze_user.invoke({
    "user_profile": current_user_profile
})

print(result)