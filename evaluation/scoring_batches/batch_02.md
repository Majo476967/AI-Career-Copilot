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

本批 Case：C02, C04, C11, C15。

## C02 — single_jd

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
      "capability_name": "Evaluation",
      "level": 0,
      "evidence": []
    },
    {
      "capability_name": "Agent",
      "level": 2,
      "evidence": [
        "虚构确认事实：Agent 当前为 2 级，有对应阶段的自报经历记录。"
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
      "jd_text": "Evaluation 要求等级 2，重要程度 important；Agent 要求等级 2，重要程度 must_have",
      "capabilities": [
        {
          "name": "Evaluation",
          "required_level": 2,
          "importance": "important",
          "category": "technical",
          "evidence": "Evaluation 要求等级 2，重要程度 important"
        },
        {
          "name": "Agent",
          "required_level": 2,
          "importance": "must_have",
          "category": "technical",
          "evidence": "Agent 要求等级 2，重要程度 must_have"
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
Evaluation
```

**Reason**

```text
当前处于Evaluation能力的Level 0，next_gap_type为evidence_knowledge_verification，需要核实或补充基础知识证据。通过查找并阅读权威文档，总结评估等级2的关键要点，可帮助获取相关基础知识证据。
```

**Task**

```text
查找并阅读至少3篇关于评估方法和标准的权威文档，总结其中关于评估等级2的关键要点，并记录下来。
```

**预计时间**

```text
30 min
```

**验收标准**

```text
[
  "提交至少3篇权威文档的阅读记录",
  "准确总结出评估等级2的关键要点并清晰记录"
]
```

**Replanning Result**

N/A：无历史首轮 Case。

评分：Actionability ____ / 5；Reasonableness ____ / 5；Replanning N/A；Constraint Violations ____；Notes ____。

### 方案 B

**Decision / Top Priority**

```text
Evaluation
```

**Reason**

```text
当前活跃岗位要求 Evaluation 能力等级为 2 级，而用户目前该能力等级为 0 级，需要优先提升以满足岗位要求。
```

**Task**

```text
提升 Evaluation 能力至 2 级
```

**预计时间**

```text
根据每天 1 小时的可用时间，假设提升一个能力等级需要 10 小时，大约需要 10 天（具体时间可根据实际提升难度调整）
```

**验收标准**

```text
[
  "成功将 Evaluation 能力提升至 2 级"
]
```

**Replanning Result**

N/A：无历史首轮 Case。

评分：Actionability ____ / 5；Reasonableness ____ / 5；Replanning N/A；Constraint Violations ____；Notes ____。

preferred_output（A / B / Tie）：____

---

## C04 — multi_jd

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
      "jd_text": "SQL 要求等级 2，重要程度 important；Data Analysis 要求等级 2，重要程度 bonus",
      "capabilities": [
        {
          "name": "SQL",
          "required_level": 2,
          "importance": "important",
          "category": "technical",
          "evidence": "SQL 要求等级 2，重要程度 important"
        },
        {
          "name": "Data Analysis",
          "required_level": 2,
          "importance": "bonus",
          "category": "technical",
          "evidence": "Data Analysis 要求等级 2，重要程度 bonus"
        }
      ]
    },
    {
      "id": 2,
      "company": "虚构公司2",
      "job_title": "虚构实习岗位",
      "status": "active",
      "jd_text": "SQL 要求等级 2，重要程度 important；Data Analysis 要求等级 2，重要程度 bonus",
      "capabilities": [
        {
          "name": "SQL",
          "required_level": 2,
          "importance": "important",
          "category": "technical",
          "evidence": "SQL 要求等级 2，重要程度 important"
        },
        {
          "name": "Data Analysis",
          "required_level": 2,
          "importance": "bonus",
          "category": "technical",
          "evidence": "Data Analysis 要求等级 2，重要程度 bonus"
        }
      ]
    },
    {
      "id": 3,
      "company": "虚构公司3",
      "job_title": "虚构实习岗位",
      "status": "active",
      "jd_text": "SQL 要求等级 2，重要程度 important；Data Analysis 要求等级 2，重要程度 bonus",
      "capabilities": [
        {
          "name": "SQL",
          "required_level": 2,
          "importance": "important",
          "category": "technical",
          "evidence": "SQL 要求等级 2，重要程度 important"
        },
        {
          "name": "Data Analysis",
          "required_level": 2,
          "importance": "bonus",
          "category": "technical",
          "evidence": "Data Analysis 要求等级 2，重要程度 bonus"
        }
      ]
    },
    {
      "id": 4,
      "company": "虚构公司4",
      "job_title": "虚构实习岗位",
      "status": "active",
      "jd_text": "SQL 要求等级 2，重要程度 important；Data Analysis 要求等级 2，重要程度 bonus",
      "capabilities": [
        {
          "name": "SQL",
          "required_level": 2,
          "importance": "important",
          "category": "technical",
          "evidence": "SQL 要求等级 2，重要程度 important"
        },
        {
          "name": "Data Analysis",
          "required_level": 2,
          "importance": "bonus",
          "category": "technical",
          "evidence": "Data Analysis 要求等级 2，重要程度 bonus"
        }
      ]
    },
    {
      "id": 5,
      "company": "虚构公司5",
      "job_title": "虚构实习岗位",
      "status": "active",
      "jd_text": "Data Analysis 要求等级 2，重要程度 important",
      "capabilities": [
        {
          "name": "Data Analysis",
          "required_level": 2,
          "importance": "important",
          "category": "technical",
          "evidence": "Data Analysis 要求等级 2，重要程度 important"
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
SQL
```

**Reason**

```text
所有活跃岗位对SQL的要求等级均为2级且重要程度为important，而用户当前SQL等级为1级，所以应优先提升SQL能力
```

**Task**

```text
学习SQL，将其提升至2级
```

**预计时间**

```text
20 min
```

**验收标准**

```text
[
  "能够熟练完成SQL等级2对应的练习题",
  "能够独立完成一些简单的SQL实际应用案例"
]
```

**Replanning Result**

N/A：无历史首轮 Case。

评分：Actionability ____ / 5；Reasonableness ____ / 5；Replanning N/A；Constraint Violations ____；Notes ____。

### 方案 B

**Decision / Top Priority**

```text
SQL
```

**Reason**

```text
当前处于SQL的Level 1，下一步需要进行实际练习以提升到Level 2。根据最新反馈，没有提供具体的练习任务，所以设计了一个简单的数据分析任务，通过实际操作来巩固所学知识，提升SQL技能。
```

**Task**

```text
使用SQL完成一个简单的数据分析任务，比如从一个包含销售记录的表中查询出每个月的总销售额，并按月份进行排序。
```

**预计时间**

```text
30 min
```

**验收标准**

```text
[
  "能够正确编写SQL查询语句，从销售记录表中准确查询出每个月的总销售额。",
  "查询结果按月份进行了正确排序。"
]
```

**Replanning Result**

N/A：无历史首轮 Case。

评分：Actionability ____ / 5；Reasonableness ____ / 5；Replanning N/A；Constraint Violations ____；Notes ____。

preferred_output（A / B / Tie）：____

---

## C11 — not_completed

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
      "status": "not_completed",
      "feedback": "昨天任务太大，今天只能投入十分钟。",
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
    "status": "not_completed",
    "feedback": "昨天任务太大，今天只能投入十分钟。",
    "created_at": "2026-08-01T08:00:00+00:00"
  }
}
```

### Expected Facts / Constraints

```text
{
  "expected_facts": {
    "feedback_anchors": [
      "十分钟",
      "10 min",
      "10分钟"
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
根据最新反馈，用户因昨天任务量过大且今天时间有限只能投入十分钟，所以设计简化后的 JOIN 查询练习任务，确保在十分钟内完成，以适应其时间限制。
```

**Task**

```text
完成简化后的 JOIN 查询练习，练习时间限定在十分钟以内，并保存代码和输出
```

**预计时间**

```text
10 min
```

**验收标准**

```text
[
  "成功完成限定十分钟内的 JOIN 查询练习",
  "保存了代码和输出"
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
当前岗位对SQL要求等级为2，而用户目前SQL水平为1级，需要提升SQL能力以满足岗位要求。完成第1组JOIN查询练习是提升SQL能力的具体步骤，且用户表示今天只能投入十分钟，该任务符合时间限制。
```

**Task**

```text
花十分钟完成第1组JOIN查询练习，并保存代码和输出
```

**预计时间**

```text
10 min
```

**验收标准**

```text
[
  "成功完成第1组JOIN查询练习",
  "保存了代码和输出"
]
```

**Replanning Result**

适用：依据上述原始回复对历史/反馈/目标变化的响应评分；无独立结果字段。

评分：Actionability ____ / 5；Reasonableness ____ / 5；Replanning ____ / 5；Constraint Violations ____；Notes ____。

preferred_output（A / B / Tie）：____

---

## C15 — long_history

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
      "capability": "Product Design",
      "task": "完成第1组虚构产品原型练习，保存交互图和设计说明",
      "status": "completed",
      "feedback": "",
      "created_at": "2026-08-01T08:00:00+00:00"
    },
    {
      "id": 2,
      "capability": "Product Design",
      "task": "完成第2组虚构产品原型练习，保存交互图和设计说明",
      "status": "completed",
      "feedback": "",
      "created_at": "2026-08-02T08:00:00+00:00"
    },
    {
      "id": 3,
      "capability": "Product Design",
      "task": "完成第3组虚构产品原型练习，保存交互图和设计说明",
      "status": "completed",
      "feedback": "",
      "created_at": "2026-08-03T08:00:00+00:00"
    },
    {
      "id": 4,
      "capability": "Product Design",
      "task": "完成第4组虚构产品原型练习，保存交互图和设计说明",
      "status": "completed",
      "feedback": "",
      "created_at": "2026-08-04T08:00:00+00:00"
    },
    {
      "id": 5,
      "capability": "Product Design",
      "task": "完成第5组虚构产品原型练习，保存交互图和设计说明",
      "status": "completed",
      "feedback": "",
      "created_at": "2026-08-05T08:00:00+00:00"
    },
    {
      "id": 6,
      "capability": "Product Design",
      "task": "完成第6组虚构产品原型练习，保存交互图和设计说明",
      "status": "completed",
      "feedback": "",
      "created_at": "2026-08-06T08:00:00+00:00"
    },
    {
      "id": 7,
      "capability": "Product Design",
      "task": "完成第7组虚构产品原型练习，保存交互图和设计说明",
      "status": "completed",
      "feedback": "",
      "created_at": "2026-08-07T08:00:00+00:00"
    },
    {
      "id": 8,
      "capability": "Product Design",
      "task": "完成第8组虚构产品原型练习，保存交互图和设计说明",
      "status": "completed",
      "feedback": "",
      "created_at": "2026-08-08T08:00:00+00:00"
    },
    {
      "id": 9,
      "capability": "Product Design",
      "task": "完成第9组虚构产品原型练习，保存交互图和设计说明",
      "status": "completed",
      "feedback": "",
      "created_at": "2026-08-09T08:00:00+00:00"
    },
    {
      "id": 10,
      "capability": "Product Design",
      "task": "完成第10组虚构产品原型练习，保存交互图和设计说明",
      "status": "completed",
      "feedback": "",
      "created_at": "2026-08-10T08:00:00+00:00"
    },
    {
      "id": 11,
      "capability": "Product Design",
      "task": "完成第11组虚构产品原型练习，保存交互图和设计说明",
      "status": "completed",
      "feedback": "",
      "created_at": "2026-08-11T08:00:00+00:00"
    },
    {
      "id": 12,
      "capability": "Product Design",
      "task": "完成第12组虚构产品原型练习，保存交互图和设计说明",
      "status": "completed",
      "feedback": "",
      "created_at": "2026-08-12T08:00:00+00:00"
    },
    {
      "id": 13,
      "capability": "Product Design",
      "task": "完成第13组虚构产品原型练习，保存交互图和设计说明",
      "status": "completed",
      "feedback": "",
      "created_at": "2026-08-13T08:00:00+00:00"
    },
    {
      "id": 14,
      "capability": "Product Design",
      "task": "完成第14组虚构产品原型练习，保存交互图和设计说明",
      "status": "completed",
      "feedback": "",
      "created_at": "2026-08-14T08:00:00+00:00"
    },
    {
      "id": 15,
      "capability": "Product Design",
      "task": "完成第15组虚构产品原型练习，保存交互图和设计说明",
      "status": "completed",
      "feedback": "",
      "created_at": "2026-08-15T08:00:00+00:00"
    },
    {
      "id": 16,
      "capability": "Product Design",
      "task": "完成第16组虚构产品原型练习，保存交互图和设计说明",
      "status": "completed",
      "feedback": "",
      "created_at": "2026-08-16T08:00:00+00:00"
    },
    {
      "id": 17,
      "capability": "Product Design",
      "task": "完成第17组虚构产品原型练习，保存交互图和设计说明",
      "status": "completed",
      "feedback": "",
      "created_at": "2026-08-17T08:00:00+00:00"
    },
    {
      "id": 18,
      "capability": "Product Design",
      "task": "完成第18组虚构产品原型练习，保存交互图和设计说明",
      "status": "completed",
      "feedback": "",
      "created_at": "2026-08-18T08:00:00+00:00"
    },
    {
      "id": 19,
      "capability": "Product Design",
      "task": "完成第19组虚构产品原型练习，保存交互图和设计说明",
      "status": "completed",
      "feedback": "",
      "created_at": "2026-08-19T08:00:00+00:00"
    },
    {
      "id": 20,
      "capability": "Product Design",
      "task": "完成第20组虚构产品原型练习，保存交互图和设计说明",
      "status": "completed",
      "feedback": "",
      "created_at": "2026-08-20T08:00:00+00:00"
    },
    {
      "id": 21,
      "capability": "SQL",
      "task": "完成第21组 JOIN 查询练习，保存代码和输出",
      "status": "partial",
      "feedback": "JOIN 已完成，请聚焦窗口函数。",
      "created_at": "2026-08-21T08:00:00+00:00"
    }
  ]
}
```

### Latest Feedback

```text
{
  "latest_feedback": {
    "id": 21,
    "capability": "SQL",
    "task": "完成第21组 JOIN 查询练习，保存代码和输出",
    "status": "partial",
    "feedback": "JOIN 已完成，请聚焦窗口函数。",
    "created_at": "2026-08-21T08:00:00+00:00"
  }
}
```

### Expected Facts / Constraints

```text
{
  "expected_facts": {
    "feedback_anchors": [
      "窗口函数"
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
目标岗位要求SQL等级3，当前为1级，需要提升SQL能力以满足岗位要求。最新反馈指出JOIN已完成，应聚焦窗口函数进行练习。
```

**Task**

```text
完成第22组窗口函数查询练习，保存代码和输出
```

**预计时间**

```text
60 min
```

**验收标准**

```text
[
  "成功完成第22组窗口函数查询练习",
  "代码运行正确",
  "保存了代码和输出"
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
根据最新反馈，用户已完成JOIN查询练习，接下来应聚焦窗口函数练习，因此设计此任务。
```

**Task**

```text
完成第22组窗口函数练习，保存代码和输出
```

**预计时间**

```text
60 min
```

**验收标准**

```text
[
  "成功完成第22组窗口函数练习并保存代码和输出"
]
```

**Replanning Result**

适用：依据上述原始回复对历史/反馈/目标变化的响应评分；无独立结果字段。

评分：Actionability ____ / 5；Reasonableness ____ / 5；Replanning ____ / 5；Constraint Violations ____；Notes ____。

preferred_output（A / B / Tie）：____

---
