# 匿名 A/B 人工评分材料

共 16 个虚构 Case、32 份已保存回复。A/B 顺序按 Case 随机化，A 不固定代表同一方案。评分完成前不要查看映射密钥、运行目录或结果分析。

材料使用正式记录的数据修正有效版本，每例两份输出及其冻结事实来自同一轮。未重新采样，不代表当前修复版本已重新评测，也不是新的独立 Run。

仅逐字段排版原始回复，不润色、不纠错。可能暴露身份的内部字段/枚举统一替换为“[内部标识已隐藏]”，原文和位置由组织者单独保存。错误归因、笼统任务、不合理时间等均保留。盲审隐藏身份标识，但无法保证读者无法从语言风格猜测来源。

## 冻结评分标准

下表逐字摘录冻结 Rubric；每方案独立评分，允许多个合理方向，不以符合预设排名作为唯一标准。

| 分数 | Task Actionability | Decision Reasonableness | Replanning |
|---|---|---|---|
| 1 | 空泛，无可执行动作或产出 | 主要依据错误事实/非目标岗位，或严重误解证据 | 忽略已完成事实/明确卡点，原样重发或错误切换 |
| 2 | 有方向但步骤、产出或验收严重缺失 | 使用部分事实，但重要约束被遗漏 | 只泛泛提及历史，未作有效调整 |
| 3 | 基本可执行，有产出，验收或时间仍不清楚 | 方向可接受，有事实支持但权衡不完整 | 基本响应最新变化，但任务拆分/连续性不足 |
| 4 | 动作、产出、验收和时间清晰，仅少量需 澄清 | 符合岗位及用户证据，理由清楚，少量遗漏 | 针对明确反馈调整并保持连续性，只有小瑕疵 |
| 5 | 可直接执行，产出和通过条件明确，时间/难度合适 | 充分使用当前目标和证据，承认未知信息，权衡合理 | 清楚区分已完成/卡点并合理保留、推进或切换任务 |

Task Actionability、Decision Reasonableness、Replanning Quality：1～5。无历史首轮 Case 的 Replanning 填 N/A，不强行评分。其他分数保持空白，等待人工填写。

Constraint Violations：填 Yes / No，在 notes 引用具体事实和回复。检查重复 completed task、未使用明确 partial feedback、使用 archived JD、把 unknown evidence 当成能力弱、编造 feedback、任务不可验收、违反时间约束。此项是事实记录，不新增分档或自动扣分规则。preferred_output 填 A / B / Tie。

Replanning 根据原始 Decision / Reason / Task 对历史、反馈和目标变化的响应评分。没有两方共同保存的独立 Replanning Result 字段，不补造执行结果。目标变化以 Active / Archived JD 与历史为准，不推测变更时间。

请在独立填写副本中记录评审人和日期，完成全部评分后再解盲。Expected Facts / Constraints 仅供评分，未发送给模型。未评分不记作 0。

本批 Case：C03, C05, C09, C14。

## C03 — single_jd

### 用户背景与已确认能力

```text
{
  "user_profile": {
    "education": "虚构学院本科",
    "major": "软件工程",
    "target_direction": "实习岗位准备",
    "available_hours_per_day": 1,
    "resume_text": "虚构测试用户，仅用于评测。能力事实以已确认档案为准。"
  },
  "capabilities": [
    {
      "capability_name": "User Research",
      "level": 1,
      "evidence": [
        "虚构确认事实：User Research 当前为 1 级，有对应阶段的自报经历记录。"
      ]
    },
    {
      "capability_name": "Product Design",
      "level": 2,
      "evidence": [
        "虚构确认事实：Product Design 当前为 2 级，有对应阶段的自报经历记录。"
      ]
    }
  ]
}
```

### Active JD / Target Change（含归档目标）

```text
{
  "active_jds": [
    {
      "id": 1,
      "company": "虚构公司1",
      "job_title": "虚构实习岗位",
      "status": "active",
      "jd_text": "User Research 要求等级 2，重要程度 important；Product Design 要求等级 3，重要程度 important",
      "capabilities": [
        {
          "name": "User Research",
          "required_level": 2,
          "importance": "important",
          "category": "technical",
          "evidence": "User Research 要求等级 2，重要程度 important"
        },
        {
          "name": "Product Design",
          "required_level": 3,
          "importance": "important",
          "category": "technical",
          "evidence": "Product Design 要求等级 3，重要程度 important"
        }
      ]
    }
  ],
  "archived_jds": []
}
```

### 相关历史（完整可用范围）

```text
{
  "history": []
}
```

### Latest Feedback

```text
{
  "latest_feedback": null
}
```

### Expected Facts / Constraints

```text
{
  "expected_facts": {
    "feedback_anchors": [],
    "unknown_is_not_weak": true
  },
  "expected_behavior": [
    "只根据当前 Active JD 与用户证据选择合理方向，不要求唯一标准答案。",
    "任务具体、可验收且符合每日时间预算。",
    "不原样重复已完成任务；有明确反馈时响应已完成部分与卡点，不编造未知事实。"
  ]
}
```

### 方案 A

**Decision / Top Priority**

```text
Product Design
```

**Reason**

```text
目标岗位要求 Product Design 等级为 3 级，而用户当前该能力等级为 2 级，所以应优先提升该能力等级
```

**Task**

```text
将 Product Design 能力等级从 2 级提升到 3 级
```

**预计时间**

```text
根据每天 1 小时的可用时间以及提升等级所需的工作量，预计需要 30 天
```

**验收标准**

```text
[
  "能够独立完成符合等级 3 要求的产品设计任务",
  "能够清晰阐述产品设计思路和方法",
  "设计成果得到导师或同行认可"
]
```

**Replanning Result**

N/A：无历史首轮 Case。

评分：Actionability ____ / 5；Reasonableness ____ / 5；Replanning N/A；Constraint Violations ____；Notes ____。

### 方案 B

**Decision / Top Priority**

```text
User Research
```

**Reason**

```text
当前处于User Research的Level 1，下一步需要进行实际练习。根据最新反馈，要求设计一份针对在线协作办公软件的用户调研问卷，以满足当前等级提升需求。
```

**Task**

```text
设计一份针对特定产品的用户调研问卷，该产品为一款在线协作办公软件，目标用户为企业办公人群。问卷内容需涵盖用户对软件功能的使用频率、满意度、改进建议等方面，不少于10个问题。
```

**预计时间**

```text
30 min
```

**验收标准**

```text
[
  "问卷问题数量不少于10个",
  "问卷内容涵盖用户对软件功能的使用频率、满意度、改进建议等方面",
  "问卷是针对在线协作办公软件和企业办公人群设计的"
]
```

**Replanning Result**

N/A：无历史首轮 Case。

评分：Actionability ____ / 5；Reasonableness ____ / 5；Replanning N/A；Constraint Violations ____；Notes ____。

preferred_output（A / B / Tie）：____

---

## C05 — multi_jd

### 用户背景与已确认能力

```text
{
  "user_profile": {
    "education": "虚构学院本科",
    "major": "软件工程",
    "target_direction": "实习岗位准备",
    "available_hours_per_day": 1,
    "resume_text": "虚构测试用户，仅用于评测。能力事实以已确认档案为准。"
  },
  "capabilities": [
    {
      "capability_name": "SQL",
      "level": 2,
      "evidence": [
        "虚构确认事实：SQL 当前为 2 级，有对应阶段的自报经历记录。"
      ]
    },
    {
      "capability_name": "Agent",
      "level": 1,
      "evidence": [
        "虚构确认事实：Agent 当前为 1 级，有对应阶段的自报经历记录。"
      ]
    }
  ]
}
```

### Active JD / Target Change（含归档目标）

```text
{
  "active_jds": [
    {
      "id": 1,
      "company": "虚构公司1",
      "job_title": "虚构实习岗位",
      "status": "active",
      "jd_text": "SQL 要求等级 2，重要程度 must_have；Agent 要求等级 3，重要程度 bonus",
      "capabilities": [
        {
          "name": "SQL",
          "required_level": 2,
          "importance": "must_have",
          "category": "technical",
          "evidence": "SQL 要求等级 2，重要程度 must_have"
        },
        {
          "name": "Agent",
          "required_level": 3,
          "importance": "bonus",
          "category": "technical",
          "evidence": "Agent 要求等级 3，重要程度 bonus"
        }
      ]
    },
    {
      "id": 2,
      "company": "虚构公司2",
      "job_title": "虚构实习岗位",
      "status": "active",
      "jd_text": "SQL 要求等级 2，重要程度 must_have",
      "capabilities": [
        {
          "name": "SQL",
          "required_level": 2,
          "importance": "must_have",
          "category": "technical",
          "evidence": "SQL 要求等级 2，重要程度 must_have"
        }
      ]
    },
    {
      "id": 3,
      "company": "虚构公司3",
      "job_title": "虚构实习岗位",
      "status": "active",
      "jd_text": "SQL 要求等级 1，重要程度 must_have",
      "capabilities": [
        {
          "name": "SQL",
          "required_level": 1,
          "importance": "must_have",
          "category": "technical",
          "evidence": "SQL 要求等级 1，重要程度 must_have"
        }
      ]
    }
  ],
  "archived_jds": []
}
```

### 相关历史（完整可用范围）

```text
{
  "history": []
}
```

### Latest Feedback

```text
{
  "latest_feedback": null
}
```

### Expected Facts / Constraints

```text
{
  "expected_facts": {
    "feedback_anchors": [],
    "unknown_is_not_weak": true
  },
  "expected_behavior": [
    "只根据当前 Active JD 与用户证据选择合理方向，不要求唯一标准答案。",
    "任务具体、可验收且符合每日时间预算。",
    "不原样重复已完成任务；有明确反馈时响应已完成部分与卡点，不编造未知事实。"
  ]
}
```

### 方案 A

**Decision / Top Priority**

```text
Agent
```

**Reason**

```text
当前处于Agent能力等级1，下一步差距类型为practice，根据要求需要进行实际练习，设计该任务可以帮助用户熟悉Agent等级3的要求和相关操作，提升实践能力。
```

**Task**

```text
根据Agent等级3的要求，完成一个简单的Agent模拟任务，比如创建一个能够根据用户输入提供特定类型回复的简易Agent程序，并在程序中体现对常见用户意图的识别和相应回复逻辑。
```

**预计时间**

```text
30 min
```

**验收标准**

```text
[
  "成功创建一个能根据用户输入提供特定类型回复的简易Agent程序",
  "程序中体现出对常见用户意图的识别和相应回复逻辑"
]
```

**Replanning Result**

N/A：无历史首轮 Case。

评分：Actionability ____ / 5；Reasonableness ____ / 5；Replanning N/A；Constraint Violations ____；Notes ____。

### 方案 B

**Decision / Top Priority**

```text
Agent
```

**Reason**

```text
目标岗位要求 Agent 能力等级为 3 级，而用户当前为 1 级，需要提升该能力以满足岗位要求。
```

**Task**

```text
将 Agent 能力等级提升至 3 级
```

**预计时间**

```text
根据用户每天 可用 1 小时，预计提升 Agent 能力等级至 3 级需要 30 小时，即 30 天
```

**验收标准**

```text
[
  "成功将 Agent 能力等级提升至 3 级"
]
```

**Replanning Result**

N/A：无历史首轮 Case。

评分：Actionability ____ / 5；Reasonableness ____ / 5；Replanning N/A；Constraint Violations ____；Notes ____。

preferred_output（A / B / Tie）：____

---

## C09 — partial

### 用户背景与已确认能力

```text
{
  "user_profile": {
    "education": "虚构学院本科",
    "major": "软件工程",
    "target_direction": "实习岗位准备",
    "available_hours_per_day": 1,
    "resume_text": "虚构测试用户，仅用于评测。能力事实以已确认档案为准。"
  },
  "capabilities": [
    {
      "capability_name": "SQL",
      "level": 1,
      "evidence": [
        "虚构确认事实：SQL 当前为 1 级，有对应阶段的自报经历记录。"
      ]
    }
  ]
}
```

### Active JD / Target Change（含归档目标）

```text
{
  "active_jds": [
    {
      "id": 1,
      "company": "虚构公司1",
      "job_title": "虚构实习岗位",
      "status": "active",
      "jd_text": "SQL 要求等级 3，重要程度 must_have",
      "capabilities": [
        {
          "name": "SQL",
          "required_level": 3,
          "importance": "must_have",
          "category": "technical",
          "evidence": "SQL 要求等级 3，重要程度 must_have"
        }
      ]
    }
  ],
  "archived_jds": []
}
```

### 相关历史（完整可用范围）

```text
{
  "history": [
    {
      "id": 1,
      "capability": "SQL",
      "task": "完成第1组 JOIN 查询练习，保存代码和输出",
      "status": "partial",
      "feedback": "JOIN 已完成，但 correlated subquery 还不会。",
      "created_at": "2026-08-01T08:00:00+00:00"
    }
  ]
}
```

### Latest Feedback

```text
{
  "latest_feedback": {
    "id": 1,
    "capability": "SQL",
    "task": "完成第1组 JOIN 查询练习，保存代码和输出",
    "status": "partial",
    "feedback": "JOIN 已完成，但 correlated subquery 还不会。",
    "created_at": "2026-08-01T08:00:00+00:00"
  }
}
```

### Expected Facts / Constraints

```text
{
  "expected_facts": {
    "feedback_anchors": [
      "correlated subquery",
      "关联子查询"
    ],
    "unknown_is_not_weak": true
  },
  "expected_behavior": [
    "只根据当前 Active JD 与用户证据选择合理方向，不要求唯一标准答案。",
    "任务具体、可验收且符合每日时间预算。",
    "不原样重复已完成任务；有明确反馈时响应已完成部分与卡点，不编造未知事实。"
  ]
}
```

### 方案 A

**Decision / Top Priority**

```text
SQL
```

**Reason**

```text
用户在之前的JOIN查询练习中已完成JOIN部分，但还不会correlated subquery。当前处于practice阶段，所以安排针对correlated subquery的练习任务。
```

**Task**

```text
完成第2组 JOIN 查询练习，重点练习 correlated subquery，保存代码和输出
```

**预计时间**

```text
60 min
```

**验收标准**

```text
[
  "成功完成第2组JOIN查询练习，其中包含对correlated subquery的正确使用",
  "保存了完整的代码和输出"
]
```

**Replanning Result**

适用：依据上述原始回复对历史/反馈/目标变化的响应评分；无独立结果字段。

评分：Actionability ____ / 5；Reasonableness ____ / 5；Replanning ____ / 5；Constraint Violations ____；Notes ____。

### 方案 B

**Decision / Top Priority**

```text
SQL
```

**Reason**

```text
目标岗位要求SQL等级3，当前等级1，已完成JOIN查询练习，下一步应学习并练习correlated subquery以提升SQL能力
```

**Task**

```text
学习并练习correlated subquery，完成后保存代码和输出
```

**预计时间**

```text
60 min
```

**验收标准**

```text
[
  "能够正确编写correlated subquery代码",
  "代码运行输出正确"
]
```

**Replanning Result**

适用：依据上述原始回复对历史/反馈/目标变化的响应评分；无独立结果字段。

评分：Actionability ____ / 5；Reasonableness ____ / 5；Replanning ____ / 5；Constraint Violations ____；Notes ____。

preferred_output（A / B / Tie）：____

---

## C14 — target_change

### 用户背景与已确认能力

```text
{
  "user_profile": {
    "education": "虚构学院本科",
    "major": "软件工程",
    "target_direction": "实习岗位准备",
    "available_hours_per_day": 1,
    "resume_text": "虚构测试用户，仅用于评测。能力事实以已确认档案为准。"
  },
  "capabilities": [
    {
      "capability_name": "Agent",
      "level": 1,
      "evidence": [
        "虚构确认事实：Agent 当前为 1 级，有对应阶段的自报经历记录。"
      ]
    },
    {
      "capability_name": "Data Analysis",
      "level": 1,
      "evidence": [
        "虚构确认事实：Data Analysis 当前为 1 级，有对应阶段的自报经历记录。"
      ]
    }
  ]
}
```

### Active JD / Target Change（含归档目标）

```text
{
  "active_jds": [
    {
      "id": 1,
      "company": "虚构公司1",
      "job_title": "虚构实习岗位",
      "status": "active",
      "jd_text": "Agent 要求等级 2，重要程度 bonus",
      "capabilities": [
        {
          "name": "Agent",
          "required_level": 2,
          "importance": "bonus",
          "category": "technical",
          "evidence": "Agent 要求等级 2，重要程度 bonus"
        }
      ]
    },
    {
      "id": 2,
      "company": "虚构公司2",
      "job_title": "虚构实习岗位",
      "status": "active",
      "jd_text": "Data Analysis 要求等级 2，重要程度 must_have",
      "capabilities": [
        {
          "name": "Data Analysis",
          "required_level": 2,
          "importance": "must_have",
          "category": "technical",
          "evidence": "Data Analysis 要求等级 2，重要程度 must_have"
        }
      ]
    },
    {
      "id": 3,
      "company": "虚构公司3",
      "job_title": "虚构实习岗位",
      "status": "active",
      "jd_text": "Data Analysis 要求等级 2，重要程度 must_have",
      "capabilities": [
        {
          "name": "Data Analysis",
          "required_level": 2,
          "importance": "must_have",
          "category": "technical",
          "evidence": "Data Analysis 要求等级 2，重要程度 must_have"
        }
      ]
    }
  ],
  "archived_jds": []
}
```

### 相关历史（完整可用范围）

```text
{
  "history": [
    {
      "id": 1,
      "capability": "Agent",
      "task": "完成第1组 Tool Calling 练习，保存工具定义、参数校验代码和输出",
      "status": "completed",
      "feedback": "",
      "created_at": "2026-08-01T08:00:00+00:00"
    }
  ]
}
```

### Latest Feedback

```text
{
  "latest_feedback": {
    "id": 1,
    "capability": "Agent",
    "task": "完成第1组 Tool Calling 练习，保存工具定义、参数校验代码和输出",
    "status": "completed",
    "feedback": "",
    "created_at": "2026-08-01T08:00:00+00:00"
  }
}
```

### Expected Facts / Constraints

```text
{
  "expected_facts": {
    "feedback_anchors": [],
    "unknown_is_not_weak": true
  },
  "expected_behavior": [
    "只根据当前 Active JD 与用户证据选择合理方向，不要求唯一标准答案。",
    "任务具体、可验收且符合每日时间预算。",
    "不原样重复已完成任务；有明确反馈时响应已完成部分与卡点，不编造未知事实。"
  ]
}
```

### 方案 A

**Decision / Top Priority**

```text
Data Analysis
```

**Reason**

```text
当前处于数据分析能力等级1，下一步差距类型为实践，根据任务要求，需要进行实际练习以提升到等级2。通过完成这个具体的数据分析实践任务，可以帮助巩固和应用所学的基础知识，提升实践能力。
```

**Task**

```text
在一个小时内完成一个简单的数据分析实践任务，比如使用Python的pandas库对给定的数据集进行清洗、探索性分析，并生成一份简单的报告，包括数据的基本统计信息、缺失值情况等。
```

**预计时间**

```text
60 min
```

**验收标准**

```text
[
  "成功完成给定数据集的清洗、探索性分析",
  "生成包含数据基本统计信息、缺失值情况等的简单报告"
]
```

**Replanning Result**

适用：依据上述原始回复对历史/反馈/目标变化的响应评分；无独立结果字段。

评分：Actionability ____ / 5；Reasonableness ____ / 5；Replanning ____ / 5；Constraint Violations ____；Notes ____。

### 方案 B

**Decision / Top Priority**

```text
Data Analysis
```

**Reason**

```text
用户目标是实习岗位准备，当前有多个岗位对Data Analysis要求等级2且重要程度为must_have，而用户Data Analysis当前等级为1级，所以优先提升该能力
```

**Task**

```text
开始学习Data Analysis 2级相关知识，记录学习笔记
```

**预计时间**

```text
60 min
```

**验收标准**

```text
[
  "有清晰的Data Analysis 2级知识学习笔记"
]
```

**Replanning Result**

适用：依据上述原始回复对历史/反馈/目标变化的响应评分；无独立结果字段。

评分：Actionability ____ / 5；Reasonableness ____ / 5；Replanning ____ / 5；Constraint Violations ____；Notes ____。

preferred_output（A / B / Tie）：____

---
