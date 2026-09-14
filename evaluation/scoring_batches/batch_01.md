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

本批 Case：C01, C07, C10, C13。

## C01 — single_jd

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
      "capability_name": "Programming",
      "level": 2,
      "evidence": [
        "虚构确认事实：Programming 当前为 2 级，有对应阶段的自报经历记录。"
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
      "jd_text": "SQL 要求等级 2，重要程度 must_have；Programming 要求等级 2，重要程度 important",
      "capabilities": [
        {
          "name": "SQL",
          "required_level": 2,
          "importance": "must_have",
          "category": "technical",
          "evidence": "SQL 要求等级 2，重要程度 must_have"
        },
        {
          "name": "Programming",
          "required_level": 2,
          "importance": "important",
          "category": "technical",
          "evidence": "Programming 要求等级 2，重要程度 important"
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
目标岗位对SQL的要求等级为2，重要程度为must_have，而用户当前SQL能力为1级，需要提升以满足岗位要求。
```

**Task**

```text
将SQL能力提升至2级
```

**预计时间**

```text
20 min
```

**验收标准**

```text
[
  "能够熟练完成SQL等级2对应的任务和项目",
  "通过SQL等级2的测试或评估"
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
当前处于SQL的Level 1，下一步gap_type为practice。根据最新反馈，没有提供具体的反馈信息，但已知需要提升到Level 2。因此，设计了一个符合Level 2要求的SQL查询练习任务，以帮助提升实际操作能力。
```

**Task**

```text
编写SQL查询语句，从一个包含员工信息的表中筛选出薪资大于5000的员工，并按照薪资降序排列。表结构如下：employees (employee_id, name, salary, department_id)。请将查询结果输出。
```

**预计时间**

```text
30 min
```

**验收标准**

```text
[
  "查询语句能够正确从包含员工信息的表中筛选出薪资大于5000的员工",
  "查询结果按照薪资降序排列"
]
```

**Replanning Result**

N/A：无历史首轮 Case。

评分：Actionability ____ / 5；Reasonableness ____ / 5；Replanning N/A；Constraint Violations ____；Notes ____。

preferred_output（A / B / Tie）：____

---

## C07 — completed

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
    "capability": "SQL",
    "task": "完成第1组 JOIN 查询练习，保存代码和输出",
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
SQL
```

**Reason**

```text
用户已完成第1组JOIN查询练习，根据任务要求，下一步应进行第2组JOIN查询练习，以进一步提升SQL技能，达到等级2的要求。
```

**Task**

```text
完成第2组JOIN查询练习，保存代码和输出
```

**预计时间**

```text
60 min
```

**验收标准**

```text
[
  "成功完成第2组JOIN查询练习，并保存代码和输出"
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
当前岗位对SQL要求等级为2，而用户目前SQL等级为1，需要继续练习提升，完成第1组JOIN查询练习后，下一步应进行第2组练习。
```

**Task**

```text
进行第2组JOIN查询练习，保存代码和输出
```

**预计时间**

```text
60 min
```

**验收标准**

```text
[
  "成功完成第2组JOIN查询练习，代码运行正确",
  "完整保存第2组JOIN查询练习的代码和输出"
]
```

**Replanning Result**

适用：依据上述原始回复对历史/反馈/目标变化的响应评分；无独立结果字段。

评分：Actionability ____ / 5；Reasonableness ____ / 5；Replanning ____ / 5；Constraint Violations ____；Notes ____。

preferred_output（A / B / Tie）：____

---

## C10 — partial

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
      "jd_text": "Agent 要求等级 3，重要程度 must_have",
      "capabilities": [
        {
          "name": "Agent",
          "required_level": 3,
          "importance": "must_have",
          "category": "technical",
          "evidence": "Agent 要求等级 3，重要程度 must_have"
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
      "status": "partial",
      "feedback": "已理解 Agent 概念，Tool Calling 参数校验仍出错。",
      "created_at": "2026-08-01T08:00:00+00:00"
    },
    {
      "id": 2,
      "capability": "Agent",
      "task": "完成第2组 Tool Calling 练习，保存工具定义、参数校验代码和输出",
      "status": "partial",
      "feedback": "只完成工具定义，仍卡在参数校验。",
      "created_at": "2026-08-02T08:00:00+00:00"
    }
  ]
}
```

### Latest Feedback

```text
{
  "latest_feedback": {
    "id": 2,
    "capability": "Agent",
    "task": "完成第2组 Tool Calling 练习，保存工具定义、参数校验代码和输出",
    "status": "partial",
    "feedback": "只完成工具定义，仍卡在参数校验。",
    "created_at": "2026-08-02T08:00:00+00:00"
  }
}
```

### Expected Facts / Constraints

```text
{
  "expected_facts": {
    "feedback_anchors": [
      "参数校验"
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
Agent
```

**Reason**

```text
当前岗位要求Agent等级3，而用户目前等级为1，且在Tool Calling参数校验方面存在问题，需要加强练习以提升能力达到岗位要求。
```

**Task**

```text
重新进行第2组Tool Calling练习，重点关注参数校验部分，完成后保存工具定义、参数校验代码和输出
```

**预计时间**

```text
60 min
```

**验收标准**

```text
[
  "成功完成第2组Tool Calling练习",
  "工具定义、参数校验代码正确",
  "有正确的输出"
]
```

**Replanning Result**

适用：依据上述原始回复对历史/反馈/目标变化的响应评分；无独立结果字段。

评分：Actionability ____ / 5；Reasonableness ____ / 5；Replanning ____ / 5；Constraint Violations ____；Notes ____。

### 方案 B

**Decision / Top Priority**

```text
Agent
```

**Reason**

```text
根据最新反馈，用户在第2组Tool Calling练习中只完成了工具定义，仍卡在参数校验部分。因此，下一步任务是完成参数校验部分，并保存代码和输出。
```

**Task**

```text
完成第2组Tool Calling练习中的参数校验部分，保存参数校验代码和输出
```

**预计时间**

```text
30 min
```

**验收标准**

```text
[
  "成功完成第2组Tool Calling练习中的参数校验部分",
  "保存了参数校验代码和输出"
]
```

**Replanning Result**

适用：依据上述原始回复对历史/反馈/目标变化的响应评分；无独立结果字段。

评分：Actionability ____ / 5；Reasonableness ____ / 5；Replanning ____ / 5；Constraint Violations ____；Notes ____。

preferred_output（A / B / Tie）：____

---

## C13 — target_change

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
      "capability_name": "Evaluation",
      "level": 1,
      "evidence": [
        "虚构确认事实：Evaluation 当前为 1 级，有对应阶段的自报经历记录。"
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
      "jd_text": "Evaluation 要求等级 2，重要程度 must_have",
      "capabilities": [
        {
          "name": "Evaluation",
          "required_level": 2,
          "importance": "must_have",
          "category": "technical",
          "evidence": "Evaluation 要求等级 2，重要程度 must_have"
        }
      ]
    }
  ],
  "archived_jds": [
    {
      "id": 9,
      "company": "虚构公司9",
      "job_title": "虚构实习岗位",
      "status": "archived",
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
  ]
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
    "capability": "SQL",
    "task": "完成第1组 JOIN 查询练习，保存代码和输出",
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
Evaluation
```

**Reason**

```text
根据最新反馈，当前处于Evaluation能力的Level 1，下一步需要进行实际练习以达到Level 2。任务要求完成一个包含至少5个不同类型数据的评估任务并撰写报告，这与提升评估能力的实践要求相匹配，能够帮助用户在实际操作中提高评估技能。
```

**Task**

```text
在接下来的60分钟内，完成一个包含至少5个不同类型数据的评估任务，并撰写评估报告，详细说明评估过程中使用的方法、遇到的问题及解决方案。
```

**预计时间**

```text
60 min
```

**验收标准**

```text
[
  "评估任务包含至少5个不同类型的数据",
  "评估报告详细说明了评估过程中使用的方法",
  "评估报告阐述了遇到的问题及解决方案"
]
```

**Replanning Result**

适用：依据上述原始回复对历史/反馈/目标变化的响应评分；无独立结果字段。

评分：Actionability ____ / 5；Reasonableness ____ / 5；Replanning ____ / 5；Constraint Violations ____；Notes ____。

### 方案 B

**Decision / Top Priority**

```text
Evaluation
```

**Reason**

```text
目标岗位要求Evaluation能力达到2级，而当前用户该能力为1级，需要提升以满足岗位要求
```

**Task**

```text
学习并实践提升Evaluation能力到2级的相关知识和技能，如学习评估方法、工具使用等，并记录学习过程和成果
```

**预计时间**

```text
8 hours
```

**验收标准**

```text
[
  "能够清晰阐述至少两种提升Evaluation能力的方法",
  "有相关学习实践的记录文档"
]
```

**Replanning Result**

适用：依据上述原始回复对历史/反馈/目标变化的响应评分；无独立结果字段。

评分：Actionability ____ / 5；Reasonableness ____ / 5；Replanning ____ / 5；Constraint Violations ____；Notes ____。

preferred_output（A / B / Tie）：____

---
