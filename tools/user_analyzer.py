from langchain_core.tools import tool
from llm import get_chat_model


model = get_chat_model(temperature=0)


@tool
def analyze_user(user_profile: str) -> str:
    """
    分析用户当前最新的能力状态。

    输入中可能同时包含：
    1. 用户初始画像
    2. completed_tasks
    3. pending_tasks
    4. task_history
    5. 用户 feedback

    必须综合这些信息判断用户“现在”真实具备的能力，
    而不是只根据初始画像判断。
    """

    prompt = f"""
你是一名求职能力分析助手。

你的任务是根据用户提供的全部信息，
判断用户“当前最新”的真实能力状态。

用户信息：

{user_profile}


【核心原则】

用户信息中可能同时包含：

- 初始能力画像
- completed_tasks
- pending_tasks
- task_history
- status
- feedback

这些信息可能代表不同时间点。

你必须优先判断用户“最新状态”，
而不是一直沿用初始画像。


【时间优先级规则】

如果初始画像与后续任务记录发生冲突：

最新的任务记录和 feedback 优先于初始画像。

例如：

初始画像：
“刚开始学习 Agent 和 Tool Calling”

后来 task_history 显示：

status = completed

feedback =
“已经能够完整解释用户请求、
Agent判断、Tool选择、Tool调用、
结果返回和后续决策的基本流程”

那么不能继续把用户判断为：

“刚开始学习 Agent”

而应该理解为：

用户已经具备 Agent 和 Tool Calling 的基础理解，
能够解释基本调用流程，
但不代表已经具备高级项目实践能力。


【任务状态解释规则】

completed：

表示该任务对应的学习或实践内容已经完成，
必须作为新的能力证据。

partial：

表示用户已经掌握任务中的一部分，
必须结合 feedback 判断：
已经掌握什么，
还没有掌握什么。

not_completed：

不能视为能力提升证据，
但可以作为当前卡点或前置知识不足的证据。


【能力证据映射】

不要只做字面关键词匹配。

例如：

RAG、Prompt Engineering、LangChain、Embedding、
LLM API、大模型项目实践

都可以作为“大模型应用能力”的证据。

Agent 基础概念、Tool Calling、
Agent自主选择Tool、多个Tool调用、
Agent项目实践

都可以作为“Agent能力”的证据。

需求分析、产品流程、PRD、原型设计、
AI产品项目经历

都可以作为“产品能力”的证据。


【评分说明】

评分仅用于相对能力判断，不代表客观考试分数。

评分范围：

0-20：
基本不了解

21-40：
了解基础概念

41-60：
能够解释核心流程，
或完成基础实践

61-80：
有真实项目实践，
能够独立完成相关任务

81-100：
能够较熟练应用，
并能够独立解决复杂问题


【重要约束】

1. 只能根据用户提供的信息判断。
2. 不允许虚构不存在的技能或经历。
3. 最新 completed / partial / feedback 必须参与能力判断。
4. 如果最新证据已经证明用户掌握基础内容，
   不允许继续沿用旧的“刚开始学习”判断。
5. 完成一个基础任务不代表能力已经达到熟练水平，
   必须根据任务难度合理调整。
6. 用户简历完全没有提到某项能力时，
   不要擅自判断为0分。
7. 每项能力必须给出 evidence。
8. 能力名称尽量标准化。
9. 输出必须是合法 JSON，不要输出任何额外文字。

如果用户信息中完全没有某项能力的正向或负向证据，
不要输出该能力，也不要擅自给低分。

没有提到 = unknown，
不等于能力弱。


请尽量分析以下具体能力：

Python
Prompt Engineering
RAG
LLM应用
Agent
Tool Calling
LangChain
Embedding
SQL
需求分析
产品流程设计
PRD
原型设计
AI产品设计
项目落地能力


输出格式：

{{
  "skills": [
    {{
      "name": "Agent",
      "score": 50,
      "evidence": "已完成Agent基础概念和Tool Calling流程学习，能够解释Agent判断和Tool调用基本流程，但尚缺少更完整项目实践"
    }}
  ],
  "strengths": [],
  "weaknesses": []
}}
"""

    response = model.invoke(prompt)

    return response.content