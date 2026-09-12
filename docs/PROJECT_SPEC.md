# AI Career Copilot V1.0 项目规格说明书

> **Project Specification / Source of Truth**

**项目名称：** AI Career Copilot
**版本：** V1.0
**文档状态：** Development Baseline
**更新日期：** 2026-09-11
**目标形态：** 可真实操作、可持续使用、可评测、可解释的 C 端 AI 求职准备产品
**主要技术栈：** Python 3.10 / Streamlit / LangChain / 豆包 LLM / SQLite

---

# 0. 文档用途

本文档是 AI Career Copilot V1.0 的唯一项目规格基线，同时服务于：

1. 产品范围定义；
2. Codex 开发任务约束；
3. 技术架构设计；
4. 功能验收；
5. Evaluation；
6. GitHub 项目展示；
7. AI 产品经理项目面试深挖。

## 0.1 开发基本原则

后续包括 Codex 在内的任何开发过程均应遵循以下规则：

* 本文档中未定义的功能，默认不进入 V1.0。
* 不允许为了“工程化”主动增加不必要的框架和基础设施。
* 产品完整度优先于技术复杂度。
* 核心业务逻辑必须保持可解释。
* 确定性逻辑优先使用 Python 规则实现。
* LLM 主要用于非结构化信息理解、语义归纳与个性化生成。
* 所有会直接影响用户求职决策的重要输入和状态必须可追溯。
* AI Coding 可以承担大量工程实现，但核心产品和架构决策必须由项目 Owner 理解并确认。
* Codex 不得自行扩大项目范围。
* 如实际开发与本文档产生冲突，应先修改 Spec，再修改代码。

---

# 1. 项目背景

求职用户在秋招、春招过程中通常不会只面对一个岗位，而是同时关注多个具有一定相似性但要求不同的 JD。

传统求职 AI 产品通常解决的是：

> 简历 + 单个 JD → 差距分析 → 给出建议。

但真实求职过程是一个持续变化的动态决策问题：

* 用户同时准备多个岗位；
* 不同岗位能力要求存在交集；
* 用户可投入的时间有限；
* 用户能力会随着任务执行持续变化；
* 新岗位不断加入，旧岗位可能退出；
* 一个任务完成、部分完成或失败都会改变下一步计划；
* 一次性的建议会快速失效。

因此用户真正需要解决的问题不是：

> “我有哪些不足？”

而是：

> **在多个目标岗位和有限准备时间下，我现在最值得补什么，下一步最应该做什么？**

AI Career Copilot V1.0 将这个问题定义为：

> **Multi-JD Career Preparation Decision Problem**

即：

> 通过持续维护用户能力、目标岗位和历史执行状态，动态优化有限时间下的求职准备优先级。

---

# 2. 产品定位

## 2.1 一句话定位

**AI Career Copilot 是一个面向校招用户的多岗位求职准备决策 Agent，根据多个目标 JD、用户能力以及历史任务执行情况，持续判断多岗位覆盖下的准备优先级，识别 high-leverage capability gap，并动态生成下一步准备任务。**

## 2.2 目标用户

V1.0 主要面向：

* 秋招 / 春招中的大学生；
* 同时准备多个相似岗位；
* 已具备部分基础能力，但存在多个短板；
* 每天可投入时间有限；
* 不清楚应该优先提升什么；
* 希望 AI 能持续理解自己的准备进度，而不是每次重新描述背景。

典型场景：

> 用户同时关注作业帮 AI 产品经理、极米 AI 产品经理、OPPO AI 产品、百词斩 C 端产品、得物用户产品等岗位，每天只有 3～5 小时准备时间，需要判断 SQL、Evaluation、Agent、数据分析、用户研究等能力中应该优先提升哪一项。

---

# 3. Product Thesis

AI Career Copilot 不试图证明：

> “Agent 比 GPT 更聪明。”

V1.0 的核心假设是：

> **对于单轮 JD 分析，直接调用大模型已经能够提供较好结果；Agent 的增量价值主要来自多目标、长期状态管理、历史反馈利用以及动态 Replanning。**

因此项目真正需要验证的是：

> **结构化 State + Multi-JD Priority + Feedback-driven Replanning 是否能够比一次性 Direct LLM 建议提供更稳定、更连续、更少重复的长期求职准备决策。**

---

# 4. 为什么不是普通 ChatGPT

Direct LLM 的典型工作方式：

```text
Resume + JD
      ↓
     LLM
      ↓
一次性建议
```

AI Career Copilot：

```text
User Profile
     +
Capabilities
     +
Multiple Active JDs
     +
Task History
     +
Execution Feedback
     ↓
Current State
     ↓
Priority Engine
     ↓
Task Planning
     ↓
Execution
     ↓
Feedback
     ↓
State Update
     ↓
Replanning
```

主要差异不是单次生成质量，而是：

* Persistent State；
* Multi-JD Decision；
* Structured Memory；
* Task History；
* Feedback Loop；
* Replanning；
* Explainable Priority；
* Historical Traceability。

---

# 5. Agent 与 Workflow 的设计原则

V1.0 不采用“所有逻辑都交给 Agent”的设计。

系统采用：

> **Deterministic Workflow + Agentic Planning**

混合架构。

## 5.1 Workflow 负责

适合固定、可预测、需要稳定执行的任务：

* PDF / DOCX 文本解析；
* JD 入库；
* Profile 更新；
* Task 状态更新；
* SQLite 数据读写；
* Priority Score 计算；
* Active / Archived JD 状态管理；
* Memory Retrieval；
* 基础数据统计。

## 5.2 LLM / Agent 负责

适合语义理解和开放决策的任务：

* JD 能力要求理解；
* Resume Capability Evidence 提取；
* Feedback 语义理解；
* Task Planning；
* Replanning；
* 长期 Memory Summary；
* Bad Case 语义归因。

## 5.3 Event Router

用户明确发生某类行为时，不依赖 LLM 猜测需要调用什么功能。

```text
                User Event
                    ↓
               Event Router
                    ↓
      ┌─────────────┼─────────────┐
      ↓             ↓             ↓
    ADD_JD     TASK_FEEDBACK   UPDATE_PROFILE
      ↓             ↓             ↓
 JD Workflow   Memory Update   User Analyzer
      └─────────────┼─────────────┘
                    ↓
             Priority Engine
                    ↓
               Task Planner
```

这样可以减少 Tool Misrouting，并使系统行为可预测。

---

# 6. V1.0 核心价值

V1.0 只重点证明三个能力。

## 6.1 Multi-JD Priority Planning

允许用户同时维护多个目标 JD。

系统从多个岗位中：

> 提取能力要求 → 聚合同类能力 → 找共性 Gap → 计算准备优先级。

核心目标：

> **最大化有限准备时间下的岗位覆盖收益。**

---

## 6.2 State-aware Replanning

任务不是一次性生成。

用户可以反馈：

* Completed；
* Partial；
* Not Completed。

状态变化后系统：

> 更新 Evidence → 更新 Capability → 重新计算 Priority → 决定继续、拆解、升级或切换任务。

---

## 6.3 Evaluation

V1.0 必须包含：

> Direct LLM Baseline VS Career Copilot

项目最终不能只声称：

> “Agent 更好。”

必须通过实际 Case 验证其价值和局限。

---

# 7. V1.0 Scope

## 7.1 P0：必须完成

V1.0 发布必须具备：

### 用户

* 简历上传；
* Resume Parsing；
* 用户 Profile；
* Capability Evidence；
* Profile 人工确认和修改。

### JD

* 手动粘贴 JD；
* PDF / DOCX / TXT JD 上传；
* 多 JD 管理；
* Active JD；
* Archived JD；
* 新增 JD；
* 替换 JD；
* 删除/退出当前目标。

### 分析

* JD Analyzer；
* User Analyzer；
* Capability Normalization；
* Multi-JD Capability Aggregation；
* Gap Analysis；
* Priority Engine。

### Planning

* 当前 Top Priority；
* 今日任务生成；
* Acceptance Criteria；
* Completed / Partial / Not Completed；
* Feedback；
* Replanning。

### Memory

* Current State；
* Append-only History；
* Rolling Summary；
* Relevant Memory Retrieval；
* SQLite 持久化。

### 产品

* Streamlit UI；
* Dashboard；
* Profile 页面；
* Target JD 页面；
* Current Task；
* History / Progress。

### Evaluation

* Direct LLM Baseline；
* Evaluation Cases；
* 指标计算；
* Bad Case 记录。

---

# 8. Out of Scope

以下能力明确不属于 V1.0。

Codex 不得自行实现：

* 自动投递；
* 招聘网站爬虫；
* BOSS / 猎聘自动登录；
* 自动搜索招聘岗位；
* 自动发送邮件；
* 求职社区；
* Offer 比较；
* AI 简历润色器；
* 完整模拟面试系统；
* MCP；
* Multi-Agent；
* 新增自定义 LangGraph 编排；
* Redis；
* Kafka；
* Celery；
* 微服务；
* Docker/Kubernetes；
* 用户付费系统；
* OCR 系统；
* JD 图片识别；
* 推荐算法平台；
* 向量数据库 Memory；
* 手机 App。

若后续增加，只能进入 V1.x / V2.0。

---

# 9. 核心用户流程

## 9.1 First-time User

```text
进入产品
   ↓
上传简历
   ↓
Resume Parser
   ↓
User Analyzer
   ↓
结构化 Profile
   ↓
用户确认 / 修改
   ↓
添加目标 JD
   ↓
JD Analyzer
   ↓
添加更多 JD
   ↓
Multi-JD Aggregation
   ↓
Gap Analysis
   ↓
Priority Engine
   ↓
生成当前任务
```

---

## 9.2 Daily Loop

```text
查看今日任务
      ↓
完成任务
      ↓
Completed / Partial / Not Completed
      ↓
填写 Feedback
      ↓
更新 Task History
      ↓
更新 Capability Evidence
      ↓
Priority Recompute
      ↓
Replanning
      ↓
下一任务
```

---

## 9.3 New JD

```text
新增 JD
   ↓
Parse
   ↓
JD Analyzer
   ↓
加入 Active JDs
   ↓
重新聚合岗位要求
   ↓
重新计算 Gap
   ↓
重新计算 Priority
   ↓
必要时 Replan
```

---

## 9.4 Replace JD

```text
Old JD
active → archived

New JD
→ active

User Profile      保留
Capabilities      保留
Task History      保留
Evidence          保留
Memory History    保留

Gap               重新计算
Priority          重新计算
Current Plan      重新评估
```

核心原则：

> **User State 与 Target State 解耦。**

更换岗位不会使用户“失忆”。

---

# 10. 输入规格

## 10.1 Resume

V1.0 支持：

| 格式        | 状态    |
| --------- | ----- |
| PDF       | 支持    |
| DOCX      | 支持    |
| JPG / PNG | 不支持   |
| 扫描 PDF    | 不保证支持 |

限制：

* 单个简历最大 10 MB；
* 一个用户只有一份 Current Resume；
* 后续上传新简历时重新解析；
* 原 Profile 不直接覆盖，先进入确认页面。

处理：

```text
Upload
↓
File Validation
↓
Parser
↓
Plain Text
↓
Resume Analyzer
↓
Structured Profile
↓
Human Confirmation
↓
Database
```

如果文本提取失败：

> “未能从文件中提取有效文本，请上传可编辑 PDF/DOCX 或使用其他文件。”

V1.0 不实现 OCR。

---

# 11. JD 输入规格

优先入口：

> **直接粘贴 JD 文本**

同时支持：

| 格式        | 状态      |
| --------- | ------- |
| 手动粘贴文本    | 支持 / 默认 |
| TXT       | 支持      |
| PDF       | 支持      |
| DOCX      | 支持      |
| JPG / PNG | 不支持     |
| URL 自动抓取  | 不支持     |

单个 JD 文件：

> ≤ 5 MB。

JD Analyzer 输出至少包含：

```json
{
  "company": "",
  "job_title": "",
  "capabilities": [
    {
      "name": "",
      "category": "",
      "importance": "",
      "required_level": 0,
      "evidence": ""
    }
  ]
}
```

用户可以修改自动识别出的：

* Company；
* Job Title。

---

# 12. Capability Model

V1.0 使用统一 Capability Vocabulary。

例如：

```text
Agent
RAG
Evaluation
Prompt Engineering
SQL
Data Analysis
User Research
Product Design
Growth
Commercial Analysis
Programming
```

不同 JD 中的相似描述应尽量归一化。

例如：

```text
数据能力
数据分析能力
业务数据分析
指标分析

→ Data Analysis
```

避免同一能力因为文本不同被重复计算。

---

# 13. Capability Level

统一采用 0～4 级。

| Level | 定义                     |
| ----- | ---------------------- |
| 0     | 尚无可验证能力证据 / unknown evidence |
| 1     | Knowledge：理解概念         |
| 2     | Practice：完成过练习/Demo    |
| 3     | Experience：真实项目/业务使用   |
| 4     | Depth：能够独立优化、评估或承担复杂问题 |

旧项目中的：

> knowledge / practice / experience / depth

继续保留，但正式转换为能力成熟度体系。

Level 0 不能直接等价为“用户不会”或“能力很弱”。证据不足时，应允许用户补充或确认；UI 和 Explainability 必须明确标注这是 Evidence Gap（证据缺口），不能将计算中的 Level 0 描述为已证实的能力不足。

---

# 14. Evidence-driven User State

系统不能只根据用户一句：

> “我会 SQL。”

就将 SQL 判断为高水平。

Capability 必须同时保存 Evidence。

每条 Evidence 至少包含：

* `evidence_type`：证据类型；
* `content`：证据内容；
* `source_id` / `source`：可关联的来源标识和/或明确来源说明；
* `created_at`：证据记录时间。

必须保留证据来源和时间，不能只保存无来源的描述字符串。单次 Task completed 只增加相应证据，不能据此直接升级一个完整 Capability Level；等级调整必须结合证据内容、任务难度和对应等级定义。

示例：

```json
{
  "capability": "SQL",
  "level": 2,
  "evidence": [
    {
      "evidence_type": "task_feedback",
      "content": "JOIN Task completed；具体产出与验收情况见关联任务",
      "source_id": "task-001",
      "source": "task_feedback",
      "created_at": "2026-09-11T10:00:00+08:00"
    }
  ]
}
```

证据可信优先级：

```text
实际任务表现
>
明确执行反馈
>
真实项目/简历经历
>
用户自评
>
LLM 推断
```

发生冲突时：

> 优先依据更新、更高质量的 Evidence 调整 Current State。

---

# 15. Multi-JD Priority Engine

Priority 不由 LLM自由决定。

由 Python 计算。

Priority Score 表示 preparation priority，即多岗位覆盖下的准备优先级，用于识别 high-leverage capability gap。它是可解释的产品启发式，可以用于提高有限时间的准备收益，但不是严格数学或经济意义上的 ROI，也不代表已计算出最优 ROI。

## 15.0 候选过滤

计算 Priority Score 前，必须先过滤不存在正向 Gap 的 Capability。仅 `Gap Severity > 0` 的能力进入评分候选；没有 Gap 的能力不能因为 Coverage / Importance 高而进入 Top Priority。

没有候选时，返回“暂无明确 Gap”，不得强行选择一个无 Gap 的能力。没有 Active JD 时不计算排名，避免分母为零。Level 0 参与计算时，仍须遵守第 13 节的 Evidence Gap 语义。

## 15.1 输入

Active JD 等权；Archived JD 不参与计算。同一 JD 对同一归一化 Capability 只计一个岗位。

每项 Capability 计算：

### Coverage

该能力覆盖多少 Active JD。

```text
Coverage =
要求该能力的 Active JD 数
/
Active JD 总数
```

### Importance

JD 对该能力的重要程度：

```text
must_have = 1.0
important = 0.7
bonus = 0.3
```

Importance 仅在要求该能力的 Active JD 中求算术平均，不把未要求该能力的 JD 计入平均值分母，不使用岗位权重。

### Gap Severity

仅在要求该能力的 Active JD 中计算每个岗位的正向差值，再求平均并归一化：

```text
Gap Severity =
mean(max(required_level_jd - current_level, 0)) / 4
```

Required Level 与 Current Level 均采用 0～4 级，因此结果位于 0～1。不得先平均 Required Level 再计算正差值；已满足的岗位不能抵消其他岗位仍存在的 Gap。

### Feasibility

表示短期提升可能性。

V1.0 可以采用简单规则：

```text
高 = 1.0
中 = 0.7
低 = 0.4
```

---

## 15.2 V1.0 Priority Formula

```text
Priority Score =

0.35 × Coverage
+
0.25 × Importance
+
0.30 × Gap Severity
+
0.10 × Feasibility
```

最终归一化：

```text
0～1
```

### 设计理由

V1.0 优先考虑：

1. 是否能覆盖多个目标岗位；
2. 用户当前是否真的存在明显 Gap；
3. 岗位是否真正重视这项能力；
4. 短期提升是否具有现实可能。

权重属于 V1.0 产品假设。

Evaluation 后可以调整。

---

# 16. Gap Type

根据 Required Level 与 Current Level，生成：

```text
knowledge
practice
experience
depth
```

例如：

用户 Level 1：

> 已理解 SQL 基础概念。

岗位要求 Level 2：

> 需要实际 SQL 操作。

则：

```text
gap_type = practice
```

Task Planner 应根据不同 Gap Type 生成不同任务。

如果 Required Level 跨越多个等级，Task 只针对“下一未达到等级”设计：下一等级 1 / 2 / 3 / 4 分别对应 knowledge / practice / experience / depth。Level 0 的证据不足应先允许补充或确认，不能据此断言用户不懂基础知识。

例如 Level 0 → Required Level 3，不能用单个任务直接宣称用户达到 Experience Level。任务完成也不等于自动获得真实项目经验或整体能力升级。

不能出现：

> Experience Gap → 推荐“阅读两篇文章”。

---

# 17. Task Planner

Task Planner 使用 LLM。

输入包括：

* Current User State；
* Active JD Summary；
* Priority Result；
* Top Capability；
* Gap Type；
* Relevant Memory；
* 用户每天可投入时间。

输出必须结构化：

```json
{
  "capability": "",
  "task": "",
  "reason": "",
  "estimated_time": "",
  "acceptance_criteria": []
}
```

任务必须满足：

* 具体；
* 可执行；
* 可验收；
* 与 Gap Type 匹配；
* 不重复最近已经完成的任务；
* 不超过用户合理时间预算。

任务文本经过 NFKC Unicode 规范化、首尾空白去除、连续空白折叠和 casefold 后生成 `task_key`。SQLite partial unique index 仅限制 `status = 'pending'` 的任务：同一 normalized key 不允许同时存在多个 pending 任务，创建或状态更新均受此约束。

completed / partial / not_completed / superseded 历史任务不参与该唯一约束，不能阻止未来再次创建同文本任务；旧任务及 Events 保留，不通过删除历史实现去重。数据库允许历史后的再次创建，不代表 Planner 应机械重复最近已完成的任务。语义重复继续由 Planner Prompt + Evaluation 处理，V1.0 不声称彻底解决所有语义重复。

错误示例：

> 学习 SQL。

正确示例：

> 完成 3 道包含 GROUP BY、HAVING 和 JOIN 的查询题，并保存 SQL 与执行结果；3 道全部正确即通过。

---

# 18. Feedback & Replanning

用户必须能够选择：

```text
completed
partial
not_completed
```

## 18.1 Completed

Feedback 可选。

行为：

* 保存历史；
* 增加对应任务的正向 Evidence，但不因单次完成直接升级完整 Capability Level；
* 不机械原样再次推荐最近已完成的任务；历史记录不构成数据库永久禁止同文本任务的约束（见第 17 节）；
* 如 Gap 仍存在，可增加难度；
* 重新计算 Priority。

## 18.2 Partial

Feedback / reason 必填。未提供原因时，应提示用户补充，不能自行编造用户卡点。

例如：

> JOIN 已完成，但 correlated subquery 不会。

行为：

* 保存部分完成 Evidence；
* 识别具体卡点；
* 可以拆任务或补前置；
* 重新进行 Replanning。

## 18.3 Not Completed

Feedback / reason 必填。未提供原因时，应提示用户补充，不能自行编造用户卡点。

系统不能简单重复原任务。

应考虑：

* 任务是否过难；
* 是否过大；
* 是否缺少前置知识；
* 用户可投入时间是否不足；
* Priority 是否需要调整。

上述原因只能结合用户提供的 Feedback / reason 判断，不能将模型猜测写成用户事实。

## 18.4 Replanning 触发与当前任务保留

所有会影响决策的事件发生后，重新计算 Priority，并重新评估当前任务。不得机械废弃当前 pending task。

先判断当前任务是否仍与新的 Top Priority / Current State 一致：

* 仍有效 → 保留当前任务；
* 已失效 → 将旧任务设为 `superseded`，再生成新任务；如果没有有效 Gap 候选，不强行生成任务。

已完成或已反馈的任务保留其反馈状态和历史，再决定后续任务。Replanning 不等于每次都必须换任务；REPLAN 记录应说明保留或替换的理由。记录 REPLAN 本身不递归触发下一次 Replanning。

---

# 19. Memory Architecture

V1.0 不把完整聊天记录不断追加到 LLM Context。

采用：

> **Full History + Current State + Rolling Summary + Relevant Retrieval**

---

# 20. Memory Layer 1：Current State

Current State 采用 Upsert 更新。

包括：

```text
User Profile
Current Capabilities
Active JDs
Current Priority
Current Tasks
```

目标：

> 快速回答“用户现在是什么状态”。

旧版本不全部进入 Prompt。

---

# 21. Memory Layer 2：Event History

完整历史采用 Append-only。

包括：

* Task；
* Feedback；
* JD Change；
* Capability Change；
* Planning Snapshot；
* Replanning Reason。

历史不因新状态出现而删除。

使用第 25.7 节的轻量 `events` 表记录事件。Current State 可以更新；Events 只追加，不覆盖。能力变化等事实可保存在相关事件的 `payload_json` 中，保留必要的变化依据。

不实现复杂 Event Sourcing；不要求通过重放所有事件重建当前状态。

目的：

* 可追溯；
* Debug；
* Evaluation；
* Bad Case 分析。

---

# 22. Memory Layer 3：Rolling Summary

随着 History 增长，不将所有历史传入模型。

旧记录按 Capability 压缩。

示例：

```text
Scope: SQL

用户已完成 SELECT、WHERE、GROUP BY 和基础 JOIN；
JOIN 实践已经较稳定；
子查询任务曾两次 Partial；
主要卡点为 correlated subquery；
过去两周 SQL 任务整体完成情况较好。
```

原始记录仍存在数据库。

Summary 只是 Context Compression。

触发条件 V1.0 可以采用：

> 某 Capability 尚未被摘要覆盖的历史事件累计超过约 10 条时，增量更新摘要。

使用现有 Summary + `covered_until_event_id` 之后的新事件更新摘要，并推进覆盖位置；不得仅因总历史已超过阈值就反复汇总同一批记录。原始 Events 保留。

触发阈值、Summary 长度上限使用配置常量；上下文预算遵守第 43 节。

---

# 23. Memory Layer 4：Relevant Retrieval

每次 Planning 默认只加载：

```text
Current User State
+
Active JD Summary
+
Current Priority
+
Relevant Capability Summary
+
最近最多 5 条相关 History
+
最新 Feedback
```

不加载完整 History。

例如当前 Priority 为 SQL：

系统优先读取：

> SQL 相关历史。

不会默认加入：

> 一个月前的 Figma Task。

V1.0 直接使用 SQLite 条件查询。

不引入 Vector Database。

---

# 24. Memory Summary 数据结构

新增：

```text
memory_summaries
```

字段：

```text
id
scope
summary
covered_until_event_id
updated_at
```

`scope` 例：

```text
global
SQL
Agent
Evaluation
Data Analysis
```

---

# 25. SQLite 数据结构

V1.0 使用 Python 标准库：

```text
sqlite3
```

不引入 ORM。

---

## 25.1 user_profile

```text
id
education
major
target_direction
available_hours_per_day
resume_text
profile_json
updated_at
```

V1.0 为单用户本地状态，`id = 1`；`profile_json` 保存结构化画像，`available_hours_per_day` 可为空，否则位于 0～24。Profile 使用 Upsert。

---

## 25.2 user_capabilities

```text
id
capability_name
level
updated_at
```

`capability_name` 唯一且非空；`level` 为 0～4 整数，Level 0 仍只表示 unknown evidence。Evidence 不再全部放入能力表的 JSON 字段，独立存储如下。

### 25.2.1 capability_evidence

```text
id
capability_id
evidence_type
content
source
source_id
created_at
```

`capability_id` 外键关联 `user_capabilities.id`；`evidence_type`、`content`、`source` 非空，`source_id` 可为空，记录来源和时间。添加 Evidence 不自动修改 Capability Level。

---

## 25.3 target_jds

```text
id
company
job_title
jd_text
jd_analysis_json
status
created_at
archived_at
```

`status`：

```text
active
archived
```

---

## 25.4 tasks

```text
id
capability
task_text
task_key
reason
estimated_time
acceptance_criteria_json
status
created_at
completed_at
```

`task_key` 由第 17 节的规范化规则生成，仅对 pending 任务唯一：

```sql
CREATE UNIQUE INDEX IF NOT EXISTS pending_task_key ON tasks(task_key)
WHERE status = 'pending';
```

`reason` 和 `estimated_time` 保存任务原因及预计耗时；验收条件以 JSON 数组保存。没有单独的 `tasks.feedback` 列：历次 Feedback 保存在关联 Task 的 Events `payload_json` 中，不随 Current Task 状态更新而覆盖。

正常新任务记录创建时间；迁移旧任务无法确认真实创建/完成时间时，`created_at` / `completed_at` 可为空，并在迁移事件 metadata 中标记 unknown。非 completed 任务的 `completed_at` 为空。

用户状态：

```text
pending
completed
partial
not_completed
```

系统可以额外使用：

```text
superseded
```

表示由于 Replanning，该任务已经不再是当前计划。

---

## 25.5 planning_snapshots

```text
id
trigger
active_jds_json
capability_state_json
priority_result_json
selected_task_json
reason
created_at
```

每次重要 Replanning 应保存 Snapshot。

目的：

> 回答“为什么之前推荐 A，现在推荐 B”。

---

## 25.6 memory_summaries

```text
id
scope
summary
covered_until_event_id
updated_at
```

`scope` 唯一；`covered_until_event_id` 可为空，非空时外键关联 `events.id`，标记已纳入摘要的事件覆盖位置，支持增量更新。

## 25.7 events

轻量 Append-only Events 表：

```text
id
event_type
entity_type
entity_id
payload_json
created_at
```

记录以下事件：

```text
TASK_CREATED
TASK_COMPLETED
TASK_PARTIAL
TASK_NOT_COMPLETED
JD_ADDED
JD_ARCHIVED
JD_REPLACED
PROFILE_CONFIRMED
REPLAN
```

`payload_json` 保存相关事实、变化依据或决策理由；通过 `entity_type` / `entity_id` 关联 Task、JD、Profile 或 Planning Snapshot。`event_type` 由上述枚举约束，`id` 为自增整数。`created_at` 是事件入库时间；迁移时不得将其冒充旧任务的真实发生时间，未知历史时间在 metadata 中明确标记。

### 25.8 Current State 与 Events 实现约束

* Current State 可以更新；Events 仅提供 append/query，不提供 update/delete 业务接口；SQLite 触发器同时阻止 Events UPDATE 和 DELETE。
* Repository 不隐式生成业务事件。调用方通过同一连接上的 `repository.transaction()` 组合 State 写入和 Event 追加，成功一起提交，失败整体回滚；事务外单次写入立即提交，不支持嵌套事务。
* SQLite 启用外键约束；JSON 字段保存合法 JSON，Repository 负责序列化与读取解码。
* 迁移幂等键保存在 Events `payload_json.migration.import_key`，由唯一索引约束，避免重复导入；原 JSON 不删除，V1.0 不双写 JSON。
* 不实现复杂 Event Sourcing，不通过重放所有事件重建 Current State。

以上为 Phase 1 Schema implementation clarification，不增加产品 Scope。

## 25.9 profile_drafts

`profile_drafts` 用于保存 Resume Analyzer 生成、但尚未经用户确认的 Profile Draft，以及确认或丢弃后的草稿状态。它是独立的暂存层，**Profile Draft 不属于 Current State**。

其目的是实现 **Human-in-the-loop Profile Confirmation**：用户先查看、修改、确认 AI 解析结果，避免解析错误直接污染正式用户状态。创建或修改 Draft 不得直接覆盖 Current Profile、Capabilities 或 Evidence。

表结构与当前 `storage/schema.sql` 一致：

```sql
CREATE TABLE IF NOT EXISTS profile_drafts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_text TEXT NOT NULL,
    resume_version TEXT NOT NULL,
    draft_json TEXT NOT NULL CHECK (json_valid(draft_json)),
    status TEXT NOT NULL CHECK (status IN ('draft', 'confirmed', 'discarded')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    confirmed_at TEXT
);
```

字段说明：

* `id`：自增草稿标识；
* `resume_text`：解析得到的简历文本；
* `resume_version`：简历文本版本标识，供确认后 Evidence 来源追溯和去重使用；
* `draft_json`：合法 JSON 格式的 Profile / Capability Evidence 草稿；
* `status`：`draft`、`confirmed` 或 `discarded`；
* `created_at` / `updated_at`：草稿创建和更新时间，不能为空；
* `confirmed_at`：确认时间，未确认时为空。

只有用户明确确认后，才允许将该 Draft 的数据写入正式状态，并在同一事务内：

1. 更新 `user_profile`；
2. 保存或更新 `user_capabilities`；
3. 添加 `capability_evidence`，对相同简历版本的同一条 Evidence 去重；
4. 追加 `PROFILE_CONFIRMED` Event；
5. 将 Draft 标记为 `confirmed` 并记录确认时间。

上述写入成功时一起提交，失败时一起回滚。重复确认同一已确认 Draft 不重复写入 Evidence 或 Event，也不重新覆盖 Current Profile。

Discard 将 Draft 标记为 `discarded`，此后不得再确认或修改；已确认 Draft 不能通过 discard 撤销正式状态。**Discard 后的 Draft 可以删除**，因为它不属于正式 Current State 或 append-only Event History。当前实现只标记 `discarded` 并保留记录，未自动执行物理删除；删除许可不要求本轮新增清理接口，也不得删除正式 Evidence 或 Events。

本节仅同步已实现的 Draft 暂存与人工确认设计，属于实现说明，不属于 Scope Expansion。

---

# 26. Parsing Layer

新增：

```text
parsers/
```

包含：

```text
resume_parser.py
jd_parser.py
```

推荐依赖：

```text
pypdf
python-docx
```

职责只负责：

> File → Text

不负责：

> Text → AI Analysis。

解析与语义分析必须分层。

---

# 27. JD Analyzer

职责：

> JD Text → Structured Capability Requirements

必须输出：

* Company；
* Job Title；
* Capabilities；
* Importance；
* Required Level；
* Evidence。

不得直接决定最终 Priority。

---

# 28. User Analyzer

职责：

> Resume / User Input → User Capability Evidence

输出：

* Capability；
* Current Level；
* Evidence；
* Evidence Source。

不得直接决定任务。

---

# 29. Priority Engine

职责：

> Structured JD + User Capabilities → Priority Ranking

必须：

* Python 实现；
* 可单元测试；
* 相同输入产生相同输出；
* 输出每一项得分与原因。

例如：

```json
{
  "capability": "SQL",
  "score": 0.82,
  "coverage": 0.8,
  "importance": 0.9,
  "gap": 0.85,
  "feasibility": 0.9
}
```

---

# 30. System Architecture

```text
┌─────────────────────────────┐
│        Streamlit UI         │
│                             │
│ Profile / Target JDs        │
│ Gap / Priority / Tasks      │
│ Feedback / Progress         │
└──────────────┬──────────────┘
               │
             Event
               │
               ▼
┌─────────────────────────────┐
│        Event Router         │
└──────────────┬──────────────┘
               │
      ┌────────┼────────┐
      ▼        ▼        ▼
 JD Service  Task     Profile
             Service   Service
      │        │        │
      ▼        ▼        ▼
 Analyzer   Memory   Analyzer
      └────────┼────────┘
               ▼
┌─────────────────────────────┐
│        Current State        │
│ User + JDs + History        │
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│       Priority Engine       │
│       Python Rules          │
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│        Task Planner         │
│            LLM              │
└──────────────┬──────────────┘
               ▼
             Task
               │
               ▼
┌─────────────────────────────┐
│            SQLite           │
└─────────────────────────────┘
```

---

# 31. 推荐项目目录

```text
AI-Career-Copilot/

├── app.py
├── main.py
├── llm.py
├── requirements.txt
├── .env.example
├── README.md

├── core/
│   ├── router.py
│   ├── planner.py
│   ├── priority_engine.py
│   └── schemas.py

├── parsers/
│   ├── resume_parser.py
│   └── jd_parser.py

├── tools/
│   ├── jd_analyzer.py
│   ├── user_analyzer.py
│   └── task_planner.py

├── services/
│   ├── profile_service.py
│   ├── jd_service.py
│   ├── task_service.py
│   ├── memory_service.py
│   └── planning_service.py

├── storage/
│   ├── database.py
│   ├── repository.py
│   └── schema.sql

├── evaluation/
│   ├── baseline.py
│   ├── evaluator.py
│   ├── cases.json
│   └── results/

├── tests/
│   ├── test_database.py
│   ├── test_priority.py
│   ├── test_jd_management.py
│   ├── test_memory.py
│   └── test_replanning.py

├── scripts/
│   └── migrate_json_memory.py

└── docs/
    └── PROJECT_SPEC.md
```

---

# 32. UI Scope

Streamlit V1.0 只需要四个主要页面。

## 32.1 Dashboard

展示：

* Active JD 数量；
* 当前 Top Priority；
* 当前任务；
* 当前 Gap；
* 最近准备进度；
* Replanning Reason。

核心问题：

> “我今天到底应该干什么？”

---

## 32.2 Profile

展示：

* 当前简历；
* 教育；
* 实习；
* 项目；
* Capability；
* Evidence。

功能：

* 上传简历；
* 查看解析结果；
* 修改；
* 确认；
* 重新上传。

---

## 32.3 Target Jobs

功能：

* 粘贴 JD；
* 上传 JD；
* 添加；
* Archive；
* Replace；
* 查看 JD Analysis；
* 查看岗位共同能力。

---

## 32.4 Progress / History

展示：

* Task History；
* Status；
* Feedback；
* Capability Progress；
* Replanning History。

无需复杂图表。

---

# 33. Explainability

所有重要决策必须能够回答：

> **Why this?**

例如：

```text
当前优先补 SQL。

原因：

1. 4/5 个 Active JD 要求 SQL / Data Analysis；
2. 多数岗位将其列为 Important 或 Must-have；
3. 用户目前 SQL Capability Level = 1；
4. 岗位平均 Required Level ≈ 2～3；
5. SQL 属于短期可通过 Practice 明显提升的能力。

Priority Score = 0.82
```

不能只显示：

> “AI 推荐你学习 SQL。”

如果 Current Level = 0 源于证据不足，UI 和解释必须标明“尚无可验证能力证据 / Evidence Gap”，允许用户补充或确认，不得直接显示“用户不会”或“能力很弱”。Priority Score 应解释为多岗位覆盖下的准备优先级。

---

# 34. Evaluation Goal

Evaluation 的目标不是证明 Agent 一定优于 LLM。

真正问题：

> **在哪些场景下 Career Copilot 比 Direct LLM 更有价值？**

如果实验发现单轮任务差异很小，也属于有效结论。

---

# 35. Direct LLM Baseline

Baseline 使用：

> 与 Career Copilot 相同的底层 LLM。

为了公平：

Direct LLM 与 Career Copilot 必须使用相同事实数据和相同可用历史范围，包括用户信息、JD 与相关历史。不得通过隐藏事实或缩小 Baseline 的可用历史范围制造优势。

两组都必须保存原始输入、原始输出和评分；Evaluation Rubric 在正式实验前冻结。

Baseline 直接通过文本获得这些事实，但：

* 不使用结构化 Persistent State；
* 不使用 Priority Engine；
* 不使用 Capability Evidence Model；
* 不使用专门的 Replanning State；
* 直接通过 Prompt 生成建议。

核心比较：

> “结构化产品系统” VS “直接让模型给建议”。

而不是：

> “强模型 VS 弱模型”。

---

# 36. Evaluation Cases

V1.0 最少：

> **12 个 Case**

建议组成：

### Single-JD

3 个。

验证基础 Gap/Task。

### Multi-JD

3 个。

验证岗位覆盖和 Priority。

### Feedback/Replanning

4 个。

包含：

* completed；
* partial；
* not_completed；
* 连续 partial。

### Target Change

2 个。

验证：

* 新 JD；
* Replace JD。

---

# 37. Evaluation Metrics

至少记录：

## 37.1 State Utilization Accuracy

系统是否正确利用：

* 用户能力；
* 历史完成任务；
* 最新 Feedback；
* 当前 JD。

---

## 37.2 Duplicate Task Rate

是否重复推荐已经完成的任务。

---

## 37.3 Replanning Reasonableness

状态变化后：

> 是否合理调整任务。

人工 1～5 分。

---

## 37.4 Multi-JD Coverage

Top Priority 是否真正覆盖多个目标 JD。

---

## 37.5 Task Actionability

任务是否：

* 具体；
* 可执行；
* 可验收。

人工 1～5 分。

---

## 37.6 Gap Accuracy

人工判断：

> Gap 是否与 JD 和用户证据一致。

---

# 38. Evaluation 原则

任何实验结果：

> 必须真实记录。

禁止为了简历修改实验数据。

如果结果：

> Direct LLM 与 Career Copilot 差异不大，

应记录：

> 哪些场景 Agent 没有产生明显增量。

如果存在 Bad Case：

> 必须保留并分析。

---

# 39. Bad Case 分类

建议至少使用：

```text
Resume Parsing Error
JD Understanding Error
Capability Mapping Error
State Conflict
Priority Error
Memory Retrieval Error
Task Planning Error
Duplicate Task
Replanning Error
```

处理：

```text
Bad Case
↓
定位错误层
↓
修复
↓
重新 Evaluation
```

---

# 40. Non-functional Requirements

## 40.1 可解释

核心 Priority 必须能够拆分。

## 40.2 可重复

确定性模块相同输入应获得相同结果。

## 40.3 持久化

重新启动程序后：

* User Profile；
* JD；
* Task；
* History；

必须仍存在。

## 40.4 Graceful Failure

遇到：

* 空文件；
* 无文本 PDF；
* 无效 JD；
* LLM JSON 输出异常；
* API失败；

不能使整个应用崩溃。

应该给用户明确错误信息。

## 40.5 简单

V1.0 应优先：

> 可理解 > 高度抽象。

---

# 41. Privacy

简历属于高敏感个人输入。

V1.0 原则：

```text
Upload
↓
Temporary File
↓
Extract Text
↓
Parse
↓
Structured Data
```

Demo 默认：

> 不需要永久保存原始上传文件。

只保存后续业务所需的：

* resume_text；
* structured_profile；
* capability evidence。

GitHub 中：

* 不上传真实用户简历；
* 不上传数据库；
* 不上传 API Key；
* `.env` 必须加入 `.gitignore`；
* 提供 `.env.example`。

开发阶段必须补齐以下工程基础：

* `requirements.txt`：声明运行所需依赖，支持 Python 3.10 环境复建；
* `.env.example`：仅提供配置项和占位值，不包含真实密钥；
* SQLite 数据库及 runtime 数据的 `.gitignore` 规则；
* 检查旧 `memory/user_state.json` 是否包含真实个人数据，确保真实个人数据不进入公开仓库。

真实 runtime Memory `memory/user_state.json` 必须由 `.gitignore` 忽略；如已被 Git 跟踪，使用 `git rm --cached` 停止后续跟踪，保留本地文件，不重写 Git 历史。公开 Demo / migration 示例使用完全虚构的 `memory/user_state.example.json`。停止跟踪会修改 Git index，不代表已经 commit，也不会清除历史提交中的内容。

---

# 42. LLM Configuration

继续使用当前项目已有：

> 豆包 Ark OpenAPI / OpenAI-compatible SDK。

V1.0 不主动切换模型供应商。

LLM 接入集中在：

```text
llm.py
```

避免业务代码各自初始化模型。

---

# 43. Context Construction

Task Planner 每次默认只使用：

```text
Current State
+
Active JD Summary
+
Current Priority
+
相关 Capability Summary
+
最近最多 5 条相关 History
+
最新 Feedback
```

禁止：

> SELECT 所有 Task History 后直接全部拼进 Prompt。

同时必须限制 Summary、单条 Feedback 和总 Context 的长度；仅限制记录条数不足以控制上下文增长。

具体阈值使用配置常量，例如：

* `MEMORY_SUMMARY_MAX_CHARS`；
* `FEEDBACK_CONTEXT_MAX_CHARS`；
* `PLANNER_CONTEXT_MAX_CHARS`；
* `MEMORY_SUMMARY_EVENT_THRESHOLD`。

实现时明确并统一长度计量单位，构造完成的总 Prompt 必须在总预算内；超限时对入模文本进行有界摘要或截取，不改写数据库中的原始 Feedback / Events。Current State 也只加载当前所需字段，不夹带完整历史。

这是解决长期使用 Context Growth 的核心机制。Relevant Retrieval 继续使用 SQLite 条件查询，不引入 Vector Database。

---

# 44. Acceptance Criteria

V1.0 必须通过以下核心验收。

## AC-01 Resume

用户可以上传：

> PDF / DOCX

并看到结构化解析结果。

解析结果必须：

> 用户确认后才正式写入 Current Profile。

---

## AC-02 Multi-JD

用户至少可以：

> 同时维护 3 个以上 Active JD。

系统能够展示：

> 共性 Capability。

---

## AC-03 Replace JD

Replace 后：

旧 JD：

> archived。

新 JD：

> active。

User State / Task History：

> 不得清空。

Priority：

> 自动重新计算。

---

## AC-04 Priority

同一输入：

> Priority Engine 输出稳定一致。

输出包含：

* Score；
* Coverage；
* Importance；
* Gap；
* Feasibility。

---

## AC-05 Task

Task 必须具备：

* Capability；
* Task；
* Reason；
* Acceptance Criteria；
* Estimated Time。

---

## AC-06 Feedback

Completed / Partial / Not Completed：

> 都必须成功持久化。

completed 的 Feedback 可选；partial / not_completed 的 Feedback / reason 必填。缺少原因时不得编造卡点。

---

## AC-07 Replanning

Feedback 后：

> 系统必须重新检查 Priority / Task。

不得只更新数据库而不影响下一次决策。所有影响决策的事件均须重算 Priority；仍有效的 pending task 保留，已失效的任务才设为 superseded 并按第 18.4 节决定新任务。

---

## AC-08 Memory Persistence

关闭程序重新启动：

> State 不丢失。

---

## AC-09 Long-term Context

即使数据库已有大量历史：

> Planner 不得把完整 History 全量传给 LLM。

最近相关 History 最多 5 条；Summary、单条 Feedback 和总 Context 均必须满足第 43 节的配置长度上限。

---

## AC-10 Evaluation

至少完成：

> 12 个正式 Evaluation Cases。

结果：

> 可重复运行并生成结果文件。

两组同底层模型、同事实数据、同可用历史范围，保存原始输入、原始输出和评分；正式实验使用预先冻结的 Rubric。

---

# 45. Definition of Done

只有同时满足以下条件，Career Copilot V1.0 才算完成：

* 核心用户链路跑通；
* Resume Upload 可用；
* Multi-JD 可用；
* Capability State 可用；
* Priority Engine 可用；
* Task Planning 可用；
* Feedback 可用；
* Replanning 可用；
* Memory 可跨会话；
* Context 不无限增长；
* JD Replace 可用；
* Evaluation 完成；
* Bad Case 有记录；
* 所有 P0 自动化测试通过；
* README 更新；
* PROJECT_SPEC 与实际实现一致；
* Demo 可以稳定完整跑一次。

---

# 46. Codex Development Rules

Codex 在本项目中的角色：

> **Engineering Execution Agent**

不是：

> Product Owner。

Codex 必须：

1. 修改现有 Repo，而不是重建项目；
2. 先阅读现有代码；
3. 尽量复用有效模块；
4. 每轮只完成指定范围；
5. 开发完成必须运行测试；
6. 测试失败必须先修复；
7. 输出修改文件列表；
8. 解释关键数据流；
9. 不得擅自继续下一阶段；
10. 对架构性修改先说明原因。

---

# 47. 禁止 Codex 主动增加的技术

除非 Project Spec 后续明确修改，否则禁止主动引入：

```text
React
Vue
FastAPI
Django
Redis
Kafka
Celery
新增自定义 LangGraph 编排
AutoGen
CrewAI
Multi-Agent
MCP
PostgreSQL
MongoDB
Vector Database
Docker
Kubernetes
Microservices
```

LangGraph 边界：禁止新增自定义 LangGraph 编排。如果 LangChain `create_agent` 的内部依赖包含 LangGraph，不视为违反 Spec；不要求移除该传递依赖。

原因：

> 这些技术目前不会直接提升 V1.0 核心用户价值，却会明显增加项目复杂度和项目面试解释成本。

---

# 48. 关键架构决策必须回答的问题

任何新增核心模块必须能够回答：

1. 它解决什么问题？
2. 为什么需要它？
3. 输入和输出是什么？
4. 不使用它的替代方案是什么？
5. 为什么选择当前方案？
6. 它可能产生什么 Bad Case？
7. 如何测试？
8. 如何判断它产生了价值？

若无法回答：

> 不进入 V1.0。

---

# 49. 项目证据输出

项目完成后 GitHub 至少应具备：

```text
README.md
docs/PROJECT_SPEC.md
系统架构图
产品核心流程图
真实 Demo 截图
Evaluation 方法
Evaluation Results
Bad Case 分析
Tests
Git Commit History
Demo Video（可选链接）
```

这些输出共同证明：

> 项目不是一次 Prompt 调试或课程式 Demo，而经历了需求定义、产品设计、系统设计、开发、测试、评估和迭代。

---

# 50. V1.0 项目成功标准

V1.0 不以：

> 功能数量

判断成功。

真正成功标准为：

### Product

能够解决一个明确的多 JD 求职准备问题。

### Engineering

能够真实运行并支持持续使用。

### AI

Agent / LLM 使用有明确边界和必要性。

### Memory

长期状态可保存，但 Context 不无限增长。

### Decision

Priority 可解释。

### Evaluation

能够通过 Baseline 和 Case 验证实际价值。

### Interview

项目 Owner 能够解释：

> 用户问题 → 产品方案 → AI 边界 → Agent 架构 → Memory → Priority → Replanning → Evaluation → Bad Case。

---

# 51. Future Roadmap

以下只作为未来方向，不属于 V1.0。

## V1.1

可能包括：

* JD Screenshot OCR；
* JD URL Parsing；
* 更细能力体系；
* Deadline / Interview Urgency；
* 更完整统计 Dashboard。

## V1.2

可能包括：

* Job Search；
* Interview Preparation；
* Resume Optimization；
* Calendar Integration。

## V2.0

只有获得真实用户验证后再考虑：

* 多用户账号；
* Cloud Database；
* Vector Memory；
* 自动职位发现；
* 更完整 Career Agent。

---

# 52. 最终项目定义

AI Career Copilot V1.0 不是：

> “一个能够分析简历和 JD 的聊天机器人。”

也不是：

> “为了展示 LangChain、Tool Calling 和 Memory 而搭建的 Agent Demo。”

它最终希望验证的是：

> **面对多个求职目标、有限准备时间和持续变化的用户能力，能否通过结构化 State、Multi-JD Priority、长期 Memory 和 Feedback-driven Replanning，持续帮助用户做出下一步求职准备决策。**

其核心产品价值不是：

> “告诉用户很多建议。”

而是：

> **帮助用户持续决定现在最值得做什么。**

---

# 53. Development Baseline

从本版本文档冻结开始：

> **PROJECT_SPEC.md 即 V1.0 开发 Source of Truth。**

开发顺序：

```text
Specification
↓
Storage & State
↓
Input Parsing
↓
JD / User Analyzer
↓
Multi-JD Priority
↓
Task Planner
↓
Feedback
↓
Memory & Replanning
↓
Streamlit Product UI
↓
Evaluation
↓
Bad Case
↓
README / Demo
↓
V1.0 Freeze
```

除 Bug 修复、Evaluation 发现的问题以及本文档明确要求的功能外：

> **V1.0 开发期间不新增 Scope。**
