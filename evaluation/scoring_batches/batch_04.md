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

本批 Case：C06, C08, C12, C16。

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
