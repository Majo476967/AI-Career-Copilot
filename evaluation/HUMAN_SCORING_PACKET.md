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

## C06 — multi_jd

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
      "capability_name": "RAG",
      "level": 2,
      "evidence": [
        "虚构确认事实：RAG 当前为 2 级，有对应阶段的自报经历记录。"
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
      "jd_text": "RAG 要求等级 1，重要程度 important；Evaluation 要求等级 2，重要程度 important",
      "capabilities": [
        {
          "name": "RAG",
          "required_level": 1,
          "importance": "important",
          "category": "technical",
          "evidence": "RAG 要求等级 1，重要程度 important"
        },
        {
          "name": "Evaluation",
          "required_level": 2,
          "importance": "important",
          "category": "technical",
          "evidence": "Evaluation 要求等级 2，重要程度 important"
        }
      ]
    },
    {
      "id": 2,
      "company": "虚构公司2",
      "job_title": "虚构实习岗位",
      "status": "active",
      "jd_text": "RAG 要求等级 4，重要程度 important",
      "capabilities": [
        {
          "name": "RAG",
          "required_level": 4,
          "importance": "important",
          "category": "technical",
          "evidence": "RAG 要求等级 4，重要程度 important"
        }
      ]
    },
    {
      "id": 3,
      "company": "虚构公司3",
      "job_title": "虚构实习岗位",
      "status": "active",
      "jd_text": "Evaluation 要求等级 3，重要程度 bonus",
      "capabilities": [
        {
          "name": "Evaluation",
          "required_level": 3,
          "importance": "bonus",
          "category": "technical",
          "evidence": "Evaluation 要求等级 3，重要程度 bonus"
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
当前活跃岗位中，虚构公司1的实习岗位对 Evaluation 要求等级为 2 级，重要程度为 important，而用户目前 Evaluation 能力为 1 级，需要提升以满足该岗位要求。
```

**Task**

```text
提升 Evaluation 能力至 2 级
```

**预计时间**

```text
根据用户每天 1 小时的可用时间，以及提升能力所需的努力程度，估计需要 20 天左右。
```

**验收标准**

```text
[
  "能够独立完成符合 Evaluation 2 级水平的任务",
  "在相关测试或评估中达到 Evaluation 2 级的标准"
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
根据用户当前Evaluation能力等级为1，下一等级要求为practice，且任务预算为60分钟，所以设计此任务，让用户通过实际练习案例提升能力至Level 2。
```

**Task**

```text
在接下来的60分钟内，完成至少2个Evaluation相关的实际练习案例，要求案例的难度和复杂度符合Level 2的要求。
```

**预计时间**

```text
60 min
```

**验收标准**

```text
[
  "成功完成至少2个符合Level 2要求的Evaluation实际练习案例。"
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

## C08 — completed

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
      "jd_text": "SQL 要求等级 2，重要程度 important；Data Analysis 要求等级 2，重要程度 important",
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
  "history": [
    {
      "id": 1,
      "capability": "SQL",
      "task": "完成第1组 JOIN 查询练习，保存代码和输出",
      "status": "completed",
      "feedback": "",
      "created_at": "2026-08-01T08:00:00+00:00"
    },
    {
      "id": 2,
      "capability": "SQL",
      "task": "完成第2组 JOIN 查询练习，保存代码和输出",
      "status": "completed",
      "feedback": "",
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
    "capability": "SQL",
    "task": "完成第2组 JOIN 查询练习，保存代码和输出",
    "status": "completed",
    "feedback": "",
    "created_at": "2026-08-02T08:00:00+00:00"
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
目标岗位要求Data Analysis等级为2级，当前水平为1级，需要提升以满足岗位要求
```

**Task**

```text
学习Data Analysis达到2级水平，可通过在线课程、书籍或实践项目进行提升
```

**预计时间**

```text
20 min
```

**验收标准**

```text
[
  "能够清晰阐述Data Analysis达到2级水平所掌握的知识和技能",
  "通过相关测试或完成具有一定难度的实践项目来证明达到2级水平"
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
当前处于数据分析Level 1，下一步需要进行实际练习以提升到Level 2。通过在数据集上执行数据清洗操作，可以锻炼相关技能，符合practice的任务类型要求。
```

**Task**

```text
在一个数据集上执行数据清洗操作，包括处理缺失值、重复值和异常值。完成后记录操作步骤和遇到的问题。
```

**预计时间**

```text
30 min
```

**验收标准**

```text
[
  "有完整的数据清洗操作步骤记录",
  "记录了遇到的问题及解决方法"
]
```

**Replanning Result**

适用：依据上述原始回复对历史/反馈/目标变化的响应评分；无独立结果字段。

评分：Actionability ____ / 5；Reasonableness ____ / 5；Replanning ____ / 5；Constraint Violations ____；Notes ____。

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

## C12 — not_completed

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
  "archived_jds": []
}
```

### 相关历史（完整可用范围）

```text
{
  "history": [
    {
      "id": 1,
      "capability": "Evaluation",
      "task": "完成第1组模型回答评测练习，保存测试数据、评分依据和报告",
      "status": "not_completed",
      "feedback": "缺少可用的测试数据，请先安排构建小样本测试集。",
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
    "capability": "Evaluation",
    "task": "完成第1组模型回答评测练习，保存测试数据、评分依据和报告",
    "status": "not_completed",
    "feedback": "缺少可用的测试数据，请先安排构建小样本测试集。",
    "created_at": "2026-08-01T08:00:00+00:00"
  }
}
```

### Expected Facts / Constraints

```text
{
  "expected_facts": {
    "feedback_anchors": [
      "测试集",
      "测试数据"
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
Evaluation
```

**Reason**

```text
当前岗位要求 Evaluation 达到 2 级，而用户当前为 1 级，且之前进行模型回答评测练习时缺少测试数据，所以优先构建小样本测试集是推进能力提升以满足岗位要求的关键步骤。
```

**Task**

```text
构建小样本测试集
```

**预计时间**

```text
30 min
```

**验收标准**

```text
[
  "成功构建包含多种类型数据的小样本测试集"
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
根据最新反馈，之前的模型回答评测练习未完成是因为缺少可用的测试数据，所以下一步任务是构建小样本测试集
```

**Task**

```text
构建一个包含10个样本的小样本测试集，样本应涵盖不同类型的数据情况
```

**预计时间**

```text
30 min
```

**验收标准**

```text
[
  "成功构建一个包含10个样本的小样本测试集",
  "测试集样本涵盖不同类型的数据情况"
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

## C16 — long_history

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
    },
    {
      "id": 2,
      "capability": "SQL",
      "task": "完成第2组 JOIN 查询练习，保存代码和输出",
      "status": "completed",
      "feedback": "",
      "created_at": "2026-08-02T08:00:00+00:00"
    },
    {
      "id": 3,
      "capability": "SQL",
      "task": "完成第3组 JOIN 查询练习，保存代码和输出",
      "status": "completed",
      "feedback": "",
      "created_at": "2026-08-03T08:00:00+00:00"
    },
    {
      "id": 4,
      "capability": "SQL",
      "task": "完成第4组 JOIN 查询练习，保存代码和输出",
      "status": "completed",
      "feedback": "",
      "created_at": "2026-08-04T08:00:00+00:00"
    },
    {
      "id": 5,
      "capability": "SQL",
      "task": "完成第5组 JOIN 查询练习，保存代码和输出",
      "status": "completed",
      "feedback": "",
      "created_at": "2026-08-05T08:00:00+00:00"
    },
    {
      "id": 6,
      "capability": "SQL",
      "task": "完成第6组 JOIN 查询练习，保存代码和输出",
      "status": "completed",
      "feedback": "",
      "created_at": "2026-08-06T08:00:00+00:00"
    },
    {
      "id": 7,
      "capability": "SQL",
      "task": "完成第7组 JOIN 查询练习，保存代码和输出",
      "status": "completed",
      "feedback": "",
      "created_at": "2026-08-07T08:00:00+00:00"
    },
    {
      "id": 8,
      "capability": "SQL",
      "task": "完成第8组 JOIN 查询练习，保存代码和输出",
      "status": "completed",
      "feedback": "",
      "created_at": "2026-08-08T08:00:00+00:00"
    },
    {
      "id": 9,
      "capability": "SQL",
      "task": "完成第9组 JOIN 查询练习，保存代码和输出",
      "status": "completed",
      "feedback": "",
      "created_at": "2026-08-09T08:00:00+00:00"
    },
    {
      "id": 10,
      "capability": "SQL",
      "task": "完成第10组 JOIN 查询练习，保存代码和输出",
      "status": "completed",
      "feedback": "",
      "created_at": "2026-08-10T08:00:00+00:00"
    },
    {
      "id": 11,
      "capability": "SQL",
      "task": "完成第11组 JOIN 查询练习，保存代码和输出",
      "status": "completed",
      "feedback": "",
      "created_at": "2026-08-11T08:00:00+00:00"
    },
    {
      "id": 12,
      "capability": "SQL",
      "task": "完成第12组 JOIN 查询练习，保存代码和输出",
      "status": "completed",
      "feedback": "",
      "created_at": "2026-08-12T08:00:00+00:00"
    },
    {
      "id": 13,
      "capability": "SQL",
      "task": "完成第13组 JOIN 查询练习，保存代码和输出",
      "status": "not_completed",
      "feedback": "任务超时，下一步只做一道 GROUP BY 查询。",
      "created_at": "2026-08-13T08:00:00+00:00"
    }
  ]
}
```

### Latest Feedback

```text
{
  "latest_feedback": {
    "id": 13,
    "capability": "SQL",
    "task": "完成第13组 JOIN 查询练习，保存代码和输出",
    "status": "not_completed",
    "feedback": "任务超时，下一步只做一道 GROUP BY 查询。",
    "created_at": "2026-08-13T08:00:00+00:00"
  }
}
```

### Expected Facts / Constraints

```text
{
  "expected_facts": {
    "feedback_anchors": [
      "GROUP BY"
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
根据最新反馈，由于之前的 JOIN 查询练习任务超时，所以下一步安排一道 GROUP BY 查询练习，帮助巩固 SQL 技能，为达到 Level 2 做准备。
```

**Task**

```text
完成一道 GROUP BY 查询练习，保存代码和输出
```

**预计时间**

```text
60 min
```

**验收标准**

```text
[
  "成功完成 GROUP BY 查询练习，并保存代码和输出"
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
当前申请的实习岗位对 SQL 的要求等级为 2，而用户目前 SQL 等级为 1，需要继续练习提升。根据最新反馈，由于第13组JOIN查询练习任务超时，下一步应先完成一道GROUP BY查询练习。
```

**Task**

```text
完成一道 GROUP BY 查询练习，保存代码和输出
```

**预计时间**

```text
60 min
```

**验收标准**

```text
[
  "成功完成一道GROUP BY查询练习，并保存完整的代码和输出结果。"
]
```

**Replanning Result**

适用：依据上述原始回复对历史/反馈/目标变化的响应评分；无独立结果字段。

评分：Actionability ____ / 5；Reasonableness ____ / 5；Replanning ____ / 5；Constraint Violations ____；Notes ____。

preferred_output（A / B / Tie）：____

---
