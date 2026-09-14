# V1.0 Product Decisions

1. **为何是多 JD 准备优先级？** 用户面对多个目标且时间有限；先选择覆盖多个岗位的正向能力 Gap，再安排一个任务，降低选择负担。Priority 是 heuristic，不是经济意义 ROI。
2. **为何用 Python 排名？** 固定公式可复现、可解释、可单测。Active JD 等权，零 Gap 先过滤，LLM 不临时改变权重。
3. **为何保留 LLM Planner？** 具体练习需要结合自然语言反馈和下一阶段设计，固定模板很难覆盖这些差异；Python 负责校验，模型负责任务内容。
4. **为何需要人工确认？** Resume Analyzer 会误读经历；Draft 与 Current State 隔离，用户确认后再写正式档案和证据。Level 0 是证据未知。
5. **为何是 SQLite？** V1.0 单用户本地演示需要跨重启持久化和原子事务；标准库已足够，不引入 ORM、云数据库或账号系统。
6. **为何 State 与 Events 分开？** State 用于当前决策，追加历史用于解释与追溯；不通过事件重放构建整套 Event Sourcing。
7. **为何有限 Memory 而非全历史入模？** 全历史成本和干扰不断增长；按能力检索、增量 Summary 与配置预算限制上下文，原始历史仍保留。语义重复与摘要质量仍需人工审查。
8. **为何保留有效 pending Task？** 新事件要求重算 Priority，但用户正在做的任务仍可能有效；只替换失效任务并标记 superseded，避免无意义反复规划。

补充：两次有效、不同任务的自报完成支持保守 0→1 / 1→2；这不是客观认证，不自动 2→3 / 3→4。Direct LLM 对照使用相同模型、事实和可用历史，避免把不同输入造成的差异误称为产品收益。

## V1.0 Owner Evaluation Release Decision — 2026-09-14

Evaluation：COMPLETE WITH LIMITATIONS。AC10：PARTIAL — ACCEPTED LIMITATION。External Human A/B Evaluation：NOT CONDUCTED（不是PASS），作为Future Work，不再阻塞本次V1.0 Release；不追加AI Judge或外部人工A/B评测。

Owner接受理由：真实用户Manual Smoke和Bad Case Retest已完成，Automatic Evaluation及两轮独立Blind AI Review已完成；Judge #1偏好Copilot 12 / Baseline 3 / Tie 1，Judge #2为13 / 3 / 0，Preferred Agreement=14/16=87.5%。对于当前个人项目V1.0，继续增加评审的边际收益较低。此为Owner接受限制，不是把AI评审当成人工评审。

自动指标State checks、Duplicate Rate、Coverage两方打平；AI评审中的稳定差异主要来自Task Actionability。Long History未体现Copilot稳定优势，不能宣称所有场景都胜出或统计显著。Copilot Constraint Violation Cases为Judge #1的4例、Judge #2的1例（Baseline分别11、10），口径分歧保留。Priority是准备优先级heuristic，非数学最优或最优ROI；能力升级基于用户自报Evidence，非客观考试认证。

Final Release以RELEASE_CHECKLIST.md的最终技术验证为准；接受Evaluation限制不豁免测试、依赖、安全与文档检查。历史评分和Run保持原样，旧的人工评审PENDING记录仅代表当时状态。
