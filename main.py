from agent import agent
from memory_manager import load_memory


# =========================
# 1. 读取最新 Memory
# =========================

user_state = load_memory()


# =========================
# 2. 目标岗位 JD
# =========================

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


# =========================
# 3. 用户初始画像
# =========================

base_user_profile = """
用户是一名软件工程专业学生。

基础能力：
- 熟悉Python基础
- 做过RAG知识库项目
- 了解Prompt Engineering、Embedding、LangChain
- 有AI产品需求分析和原型设计经验
- 初始阶段刚开始学习Agent和Tool Calling
- SQL基础较弱
- 对AI Evaluation了解较少
"""


# =========================
# 4. 合并初始画像 + 最新 Memory
# =========================

current_user_context = f"""
【用户初始画像】

{base_user_profile}


【用户最新任务与学习状态】

{user_state}


重要说明：

用户初始画像只代表最开始的能力状态。

task_history、completed_tasks、pending_tasks 和 feedback
代表用户后续最新发生的学习和执行情况。

如果初始画像与最新 Memory 存在冲突，
必须以最新 Memory 为准。

例如：

如果初始画像写着：
“刚开始学习 Agent”

但最新 feedback 表示：
“已经理解 Agent 基本概念，但还不理解 Tool Calling 调用流程”

那么当前真实状态应该理解为：

“Agent 基础概念已经掌握，
当前主要卡点是 Tool Calling 的具体调用流程和 Tool 选择机制。”

不能继续把用户判断为：
“完全处于 Agent 入门阶段”。
"""


# =========================
# 5. 构造 Agent Prompt
# =========================

prompt = f"""
这是我的目标岗位 JD：

{jd}


这是我的当前用户状态：

{current_user_context}


请你作为 AI Career Copilot，
根据目标岗位、用户当前能力和最新历史状态，
自主判断用户今天最应该完成什么。

请根据需要依次使用：

1. analyze_jd
2. analyze_user
3. analyze_gap

进行分析，而不是直接凭感觉回答。


【重要规则】

用户最新 Memory 的优先级高于初始画像。

在调用 analyze_user 时，
必须同时考虑用户初始能力和最新 task_history / feedback，
判断用户现在真实处于什么阶段。

在进行 Gap 分析时，
不能仅根据用户初始画像判断能力，
必须使用更新后的当前能力状态。


如果最近任务状态为 partial：

必须先识别：

1. 用户已经完成了什么；
2. 用户还没有掌握什么；
3. feedback 中具体卡在哪里。

下一任务应优先针对剩余卡点继续推进，
而不是从头重复原任务，
也不要无理由突然切换到其他能力。


最终只能输出：

当前最高优先级Gap：
只允许一个。

今天应该完成的具体任务：
只允许一个。

为什么优先安排这个任务：
结合 JD、当前用户能力和最新 Memory 解释。
"""


# =========================
# 6. 调用 Agent
# =========================

result = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": prompt
        }
    ]
})


# =========================
# 7. 输出最终结果
# =========================

print(result["messages"][-1].content)