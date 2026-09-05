from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

import os

load_dotenv()


model = ChatOpenAI(
    model="doubao-1-5-lite-32k-250115",
    api_key=os.getenv("ARK_API_KEY"),
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    temperature=0
)


@tool
def analyze_gap(jd_analysis: str, user_analysis: str) -> str:
    """
    对比岗位能力要求和用户当前能力，
    找出真正的岗位能力Gap，
    判断Gap类型、严重程度和优先级。
    """

    prompt = f"""
你是 AI Career Copilot 中的能力 Gap 分析模块。

你会收到两部分信息：

【目标岗位能力要求】

{jd_analysis}


【用户当前能力分析】

{user_analysis}


你的任务不是简单找出“用户不会什么”，
而是判断：

1. 目标岗位真正需要什么；
2. 用户当前已经具备什么；
3. 用户还差什么；
4. 这个差距属于哪一种类型；
5. 哪一个 Gap 当前最值得优先解决。


【一、Gap 判断原则】

用户弱项不等于岗位 Gap。

只有同时满足以下两个条件，
某项能力才可以进入 Gap：

1. 目标岗位明确要求或高度相关；
2. 用户当前在该能力上存在不足。

JD 没有要求的能力，
不能仅仅因为用户较弱就加入高优先级 Gap。


【二、必须区分 Gap 类型】

每一个 Gap 必须判断 gap_type。

gap_type 只能从以下类型中选择：

knowledge：
缺少基础概念、原理或理论理解。

practice：
已经理解基础知识，
但缺少实际操作或项目实践。

experience：
已经有基础实践，
但缺少完整项目经验、产品经验或真实场景经验。

depth：
已经有相关项目经验，
但深度、复杂度或独立解决问题能力不足。

none：
用户已有充分证据，
当前不应作为主要 Gap。


例如：

如果用户 Agent 分析结果是：

“已经理解 Agent 基础概念和 Tool Calling 基本流程，
但尚缺少完整项目实践”

那么：

gap_type 应该是 practice 或 experience，

而不能继续判断成：

“缺少 Agent 基础知识”。


如果用户已经做过 RAG、Prompt Engineering、
LangChain、Embedding、LLM API 或大模型项目，

那么“大模型应用能力”不能被判断为完全缺失。

如果岗位只要求“了解 LLM 应用技术”，
而用户已经有相关项目实践，
该项 Gap 应较小，甚至可以不作为高优先级。


【三、能力语义映射】

不能只做字面关键词匹配。

以下能力可以作为“大模型应用能力”的证据：

- RAG
- Prompt Engineering
- LangChain
- Embedding
- LLM API
- 豆包或其他大模型项目实践


以下能力可以作为“Agent能力”的证据：

- Agent 基础概念
- Tool Calling
- Agent 自主选择 Tool
- 多 Tool 调用
- Agent Demo
- Agent 项目实践


以下能力可以作为“产品能力”的证据：

- 需求分析
- 产品流程设计
- PRD
- 原型设计
- AI 产品方案设计
- AI 产品项目经历


【四、优先级判断】

判断优先级时综合考虑：

1. 岗位重要程度；
2. 用户当前能力水平；
3. Gap 类型；
4. Gap 严重程度；
5. 是否属于岗位核心要求；
6. 补齐后对当前求职的直接价值。


岗位核心要求优先于普通加分项。

但不能简单认为：

“分数越低 = 优先级越高”。

例如：

SQL 只有 20 分，
但如果 JD 只是“有基础数据能力者优先”，
它可能仍然低于一个岗位明确核心要求的 Agent 实践 Gap。


【五、唯一 Top Priority】

最终必须选出一个且只能一个 top_priority。

不允许同时输出：

“LLM + Agent”
“SQL + Evaluation”

如果多个 Gap 都比较重要，
必须强制比较后选出一个。


【六、重要约束】

1. 只输出和目标 JD 有关的 Gap。
2. 不允许虚构岗位要求。
3. 不允许虚构用户能力。
4. 用户已有项目或任务完成证据时，
   不允许判断为完全未知。
5. 必须参考 user_analysis 中的 score 和 evidence。
6. 必须判断 gap_type。
7. 输出必须是合法 JSON。
8. 不要输出 JSON 之外的任何文字。

【岗位要求边界规则】

必须严格区分：

1. JD明确写出的能力
2. 与JD能力高度相关的上位/下位能力
3. 仅凭行业常识推测的能力

只有第1类和证据充分的第2类可以进入Gap。

不得仅凭常识把JD没有明确要求的具体技能提升为高优先级Gap。

例如：

如果JD写：
“具备产品需求分析、流程设计和原型能力”

不能仅因为PRD通常属于产品工作的一部分，
就自动判断“PRD”是高优先级核心Gap。

除非JD明确写出PRD，
或用户能力证据与岗位要求之间确实存在直接缺口。

同样：

如果JD只写“有基础数据分析能力者优先”，
不能直接等同为“SQL是岗位明确要求”。

应该优先使用“基础数据分析能力”这一岗位原始表述，
SQL只能作为可能的支撑技能，而不是自动替代岗位要求。

如果某项能力只是JD中的加分项或优先项，
即使用户很弱，也不能因为gap_level很高就自动成为top_priority。

如果 gap_type = "none"，
则 gap_level 和 priority 都必须为 "none"，
且不得进入任何优先级Gap列表，
更不能成为 top_priority。

unknown 不等于 low。
没有证据证明用户薄弱时，
不得制造能力Gap。

输出格式：

{{
  "gaps": [
    {{
      "skill": "Agent",
      "job_importance": "high",
      "user_level": "basic_practice",
      "gap_type": "practice",
      "gap_level": "medium",
      "priority": "high",
      "reason": "岗位明确要求AI Agent能力，用户已经理解Agent和Tool Calling基础流程，但缺少完整Agent项目实践，因此当前主要差距不是理论知识，而是实践经验"
    }}
  ],
  "high_priority_gaps": [],
  "medium_priority_gaps": [],
  "low_priority_gaps": [],
  "top_priority": "",
  "top_priority_gap_type": "",
  "decision_reason": ""
}}
"""

    response = model.invoke(prompt)

    return response.content