# V1.0 Evaluation Rubric — frozen v1

冻结日期：2026-09-13。正式 Run 前冻结；每次 Run 保存本文 SHA-256 与副本，禁止根据结果改分档。
评分人逐个查看同一 Case 的事实与原始输出，尽量先隐藏系统标签；允许多个合理方向，不以与 Python 排名一致作为唯一正确答案。

| 分数 | Task Actionability | Decision Reasonableness | Replanning |
|---|---|---|---|
| 1 | 空泛，无可执行动作或产出 | 主要依据错误事实/非目标岗位，或严重误解证据 | 忽略已完成事实/明确卡点，原样重发或错误切换 |
| 2 | 有方向但步骤、产出或验收严重缺失 | 使用部分事实，但重要约束被遗漏 | 只泛泛提及历史，未作有效调整 |
| 3 | 基本可执行，有产出，验收或时间仍不清楚 | 方向可接受，有事实支持但权衡不完整 | 基本响应最新变化，但任务拆分/连续性不足 |
| 4 | 动作、产出、验收和时间清晰，仅少量需 澄清 | 符合岗位及用户证据，理由清楚，少量遗漏 | 针对明确反馈调整并保持连续性，只有小瑕疵 |
| 5 | 可直接执行，产出和通过条件明确，时间/难度合适 | 充分使用当前目标和证据，承认未知信息，权衡合理 | 清楚区分已完成/卡点并合理保留、推进或切换任务 |

无历史的首轮 Case：Replanning 为 N/A，不强行打 5 分。API Error 为请求失败，不计为模型质量 1 分。
模型正常返回但格式错误须保留并记录 Structured Output Error；人工仍可阅读原始内容，标明产品未交付。
人工评分与评语默认 null，只有人类评审填写后才汇总。未评分不可当作 0 或自动填入推测分数。

## 自动指标及边界

* State Utilization Accuracy（确定性子集）：选择能力是否出现在 Active JD、是否存在正向等级差、存在 completed 历史时是否避免完全重复。汇总通过检查数/适用检查数。它不证明完整理解 Current State。
* Duplicate Task Rate：规范化 NFKC/空白/casefold 后是否重复任意已完成 Task。格式无法解析时为 N/A，另计格式失败率，不把失败当作无重复。
* Multi-JD Coverage：选择能力覆盖的 Active JD 数/Active JD 总数，单 JD 同能力只计一次。不代表覆盖越高必然决策更好。
* Replanning Consistency：completed 不重复、target change 选择属于当前 JD 的能力可自动检查；partial/not_completed 的词语命中仅作为审阅线索，不当作语义评分。
* Task Actionability / Decision Reasonableness / Replanning 均按上表人工 1～5 分。
* 证据不足是否被解释成能力弱、实际是否利用反馈，以及语义重复，必须人工审阅。

## 实验边界与公平性

16 个完全虚构案例：single_jd 3、multi_jd 3、completed 2、partial 2、not_completed 2、target_change 2、long_history 2。
本轮是“已给定确认事实与历史的下一步决策”配对实验，不是 Resume/JD Analyzer 正确率或纵向真人学习收益实验。
两组共享相同 Case 事实、当前能力、Active/Archived JD 和完整可用历史。Baseline 直接读取这些事实；Copilot 将同一事实载入临时 SQLite，再由现有 Memory 检索最多 5 条相关历史。这种检索差异是被评估的系统能力，不隐藏 Baseline 的历史。
相同冻结模型配置、temperature=0、max_tokens=1500、timeout≤60 秒、max_retries=0；每组每例最多一次模型调用，共最多 32 次。请求顺序按 Case 交替两组先后。
Expected Facts / Behavior 只供评分，绝不送入任一模型。原始请求、原始回复、错误和产品交付状态分别保存。
