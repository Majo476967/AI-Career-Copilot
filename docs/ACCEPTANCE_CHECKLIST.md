# V1.0 Acceptance Checklist

更新记录日期：2026-09-14。人工主链已完成，结论 **PASS WITH OBSERVATION**。依据用户本次确认的 [Smoke S01～S20 与 Bad Case Retest](SMOKE_TEST_RESULT.md)。External Human Evaluation=NOT CONDUCTED，Owner已接受为非阻塞限制；最终技术验证见Release Checklist。

| AC | 状态 | 验收证据与边界 |
|---|---|---|
| AC-01 Resume | PASS | 人工 S02～S05：Demo Resume 解析、Draft 隔离、人工编辑与 Confirm；BC-PROFILE-001～003 复测通过。PDF/DOCX 的解析覆盖另有 test_parsers.py；本轮不声称额外完成未报告的 PDF 人工场景。 |
| AC-02 Multi-JD | PASS | 人工 S06～S07：3 Active JD 与共同能力聚合；BC-JD-001 PASS。超过 3 个岗位的支持另有 test_jd_service.py。 |
| AC-03 Replace JD | PASS | 人工 S18～S19：Archive 3→2，Replace 新 JD 生效/旧归档，Priority 重算并切换；S20 重启保留状态。 |
| AC-04 Priority | PASS | 人工 S08～S09、S16～S19：等级校准、Gap 归零、升级/岗位变更后的排序变化；确定性与公式由 test_priority_engine.py / test_gap_engine.py 验证。权重仍是 heuristic。 |
| AC-05 Task | PASS | 人工 S10～S14：任务可执行反馈、不重复同任务；后续任务出现明确动作、产出及验收标准；五字段/预算有 test_task_planner.py。Actionability 波动仍保留，人工质量评分未完成。 |
| AC-06 Feedback | PASS | 人工 S10、S12～S15：partial/completed 及记录持久化；not_completed 与原因必填由现有 test_task_service.py 验证，不冒称本轮人工另测。 |
| AC-07 Replanning | PASS | 人工 S11、S13～S19：partial 后重规划、第一次 completed 不升级、第二个不同 completed 使 User Research 0→1、Gap 归零并切换 Top Priority；BC-TASK-001 PASS。自报进展不等同客观认证。 |
| AC-08 Persistence | PASS | 人工 S12、S20：Feedback/Task/Snapshot 持久化；完全重启后 Profile/JD/Capability/Priority/Current Task 保留。 |
| AC-09 Context | PASS | 延续 test_memory_service.py 与 C15/C16 原始请求证据：相关历史≤5、字符预算、摘要水位。不是本轮人工新增的 Context 检查；Summary 语义质量不据此判定满分。 |
| AC-10 Evaluation | PARTIAL — ACCEPTED LIMITATION | 16 案例、同模型对照、冻结 Rubric、原始 Run 与自动指标已保留；AI-assisted Blind Review=COMPLETE；Independent AI Blind Review #2=COMPLETE；Inter-Judge Agreement Analysis=COMPLETE（14/16，87.5%），见 evaluation/JUDGE_AGREEMENT.md。External Human A/B Evaluation=NOT CONDUCTED；Owner已接受为V1.0非阻塞限制，留作Future Work，不标记人工PASS。 |

## 工程验证记录

最近一次业务修复的全量离线结果：348 项通过（含恢复后保存/确认完整链路）。本次Final Review完整离线测试348项全部通过（34.426s，Failed=0、Errors=0、Skipped=0），与此前348项数量一致；Python 3.10.11、pip check通过，不调用真实API。之前的 API Run、测试结果与失败历史不覆盖。

## Observations 与发布边界

- Task Actionability 仍有波动，部分任务偏学习/记录；后续已有明确动作、产出与验收标准。
- Resume Analyzer 仍会漏显式能力；Completeness Check + Human Recovery 是保护措施，不代表解析完全可靠。
- Capability Progression 基于用户自报 completed Evidence，非客观考试认证。
- Evaluation样本仍较小；外部人工A/B评测未执行，已作为Owner接受的限制。

六项指定 Bad Case 人工 Retest 均 PASS；历史实验其他案例不自动关闭。详见 [Release Checklist](RELEASE_CHECKLIST.md)。

## AI-assisted Blind Review

状态：COMPLETE。已原样保存用户提供的盲评分数，保存校验后解盲并统计；不是独立人工评分。AC10为PARTIAL — ACCEPTED LIMITATION；External Human Evaluation未执行且不再阻塞本版本。

## Independent AI Blind Review #2 / Inter-Judge Agreement

两项均COMPLETE；同一16例匿名输出、冻结Rubric，两位AI Judge偏好一致14/16，分歧和违规口径差异均保留。未修改评分或验收标准，不将AI评审替代Human Evaluation。AC10保持PARTIAL — ACCEPTED LIMITATION；外部人工评测留作Future Work。

## V1.0 Owner Evaluation Release Decision — 2026-09-14

Evaluation：COMPLETE WITH LIMITATIONS。AC10：PARTIAL — ACCEPTED LIMITATION。External Human A/B Evaluation：NOT CONDUCTED（不是PASS），作为Future Work，不再阻塞本次V1.0 Release；不追加AI Judge或外部人工A/B评测。

Owner接受理由：真实用户Manual Smoke和Bad Case Retest已完成，Automatic Evaluation及两轮独立Blind AI Review已完成；Judge #1偏好Copilot 12 / Baseline 3 / Tie 1，Judge #2为13 / 3 / 0，Preferred Agreement=14/16=87.5%。对于当前个人项目V1.0，继续增加评审的边际收益较低。此为Owner接受限制，不是把AI评审当成人工评审。

自动指标State checks、Duplicate Rate、Coverage两方打平；AI评审中的稳定差异主要来自Task Actionability。Long History未体现Copilot稳定优势，不能宣称所有场景都胜出或统计显著。Copilot Constraint Violation Cases为Judge #1的4例、Judge #2的1例（Baseline分别11、10），口径分歧保留。Priority是准备优先级heuristic，非数学最优或最优ROI；能力升级基于用户自报Evidence，非客观考试认证。

Final Release以RELEASE_CHECKLIST.md的最终技术验证为准；接受Evaluation限制不豁免测试、依赖、安全与文档检查。历史评分和Run保持原样，旧的人工评审PENDING记录仅代表当时状态。
