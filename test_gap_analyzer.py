from tools.jd_analyzer import analyze_jd
from tools.user_analyzer import analyze_user
from tools.gap_analyzer import analyze_gap

from memory_manager import load_memory


# 读取最新 Memory
user_state = load_memory()


# 真实测试 JD
jd = """
岗位名称：AI产品经理实习生

岗位职责：
1. 参与大模型应用和AI Agent产品设计；
2. 负责AI产品需求分析、产品流程设计和原型设计；
3. 与算法、研发团队协作推进AI能力落地；
4. 根据用户反馈持续优化AI产品体验。

岗位要求：
1. 了解LLM、Prompt、RAG等大模型应用技术；
2. 对AI Agent、Tool Calling等技术有一定理解；
3. 具备产品需求分析、流程设计和原型能力；
4. 有AI产品项目实践经验优先；
5. 有基础数据分析能力者优先。
"""


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


# 合并初始画像 + 最新 Memory
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


# 第一步：JD Analyzer
jd_result = analyze_jd.invoke({
    "jd_text": jd
})

print("===== JD Analysis =====")
print(jd_result)


# 第二步：User Analyzer
user_result = analyze_user.invoke({
    "user_profile": current_user_profile
})

print("\n===== User Analysis =====")
print(user_result)


# 第三步：Gap Analyzer
gap_result = analyze_gap.invoke({
    "jd_analysis": jd_result,
    "user_analysis": user_result
})

print("\n===== Gap Analysis =====")
print(gap_result)