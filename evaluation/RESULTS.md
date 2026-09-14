# V1.0 Evaluation Results

## V1.0 Owner Evaluation Release Decision — 2026-09-14

Evaluation：COMPLETE WITH LIMITATIONS。AC10：PARTIAL — ACCEPTED LIMITATION。External Human A/B Evaluation：NOT CONDUCTED（不是PASS），作为Future Work，不再阻塞本次V1.0 Release；不追加AI Judge或外部人工A/B评测。

Owner接受理由：真实用户Manual Smoke和Bad Case Retest已完成，Automatic Evaluation及两轮独立Blind AI Review已完成；Judge #1偏好Copilot 12 / Baseline 3 / Tie 1，Judge #2为13 / 3 / 0，Preferred Agreement=14/16=87.5%。对于当前个人项目V1.0，继续增加评审的边际收益较低。此为Owner接受限制，不是把AI评审当成人工评审。

自动指标State checks、Duplicate Rate、Coverage两方打平；AI评审中的稳定差异主要来自Task Actionability。Long History未体现Copilot稳定优势，不能宣称所有场景都胜出或统计显著。Copilot Constraint Violation Cases为Judge #1的4例、Judge #2的1例（Baseline分别11、10），口径分歧保留。Priority是准备优先级heuristic，非数学最优或最优ROI；能力升级基于用户自报Evidence，非客观考试认证。

Final Release以RELEASE_CHECKLIST.md的最终技术验证为准；接受Evaluation限制不豁免测试、依赖、安全与文档检查。历史评分和Run保持原样，旧的人工评审PENDING记录仅代表当时状态。


日期：2026-09-13。**确定性指标两组打平；人工质量评分未完成，不能宣称 Copilot 全面优于 Direct LLM。**

## 数据、模型与实验

16 个虚构案例，8 类场景。首轮 16 例 × 2 组 = 32 次真实请求；发现四例历史模板错误后，仅复测四例 × 2 组 = 8 次。回归测试发现 C15 的 Product Design 别名使文本修正遗漏，补正后 Run 3 仅复测 C15（2 次）。总计 42 次，无 API Error，无自动重试。

两组相同 `doubao-1-5-lite-32k-250115`、temperature=0、max_tokens=1500、timeout=60s、max_retries=0。同一冻结 Case 的事实与完整历史均可用。Copilot 使用现有 PlanningService + 临时 SQLite + Memory 检索；Baseline 无持久结构状态或 Priority Engine，直接读取全部事实。Expected 字段不进 Prompt。

这是确认事实后的下一决策实验，不是全链路解析、真实用户纵向学习或求职成功率实验。夹具直接载入 State，不用历史 completed 自动推断当前等级；当前等级以已确认事实为准。导入事件的 created_at 是评测导入时间，原历史日期另存 fixture_created_at，历史顺序不变；此差异限制严格时间相关推断。

## 保留的运行记录

- [Run 1 原始 manifest / 冻结案例及 Rubric](results/20260913T033148Z-a79c2e86/manifest.json)：16 例全部保留，包括四例数据问题。
- [Run 1 指标](results/20260913T033148Z-a79c2e86/summary.json)、[人工评分模板](results/20260913T033148Z-a79c2e86/human_scores.json)。
- [Run 2 manifest](results/20260913T033607Z-db115c43/manifest.json)：仅修正 C10/C12/C14/C15 历史文本，模型与 Rubric 未改。
- [Run 2 指标](results/20260913T033607Z-db115c43/summary.json)、[人工评分模板](results/20260913T033607Z-db115c43/human_scores.json)。

每个目录内 `Cxx-baseline.json` / `Cxx-copilot.json` 保存实际 system/user、模型原文、错误、指标及产品结果。Run 2 是数据修复复测，不是完整独立第二轮；不把三轮 21 次案例执行宣称为 21 个独立案例。当前 cases.json 为修正版；原版见 Run 1 manifest。Run 2 的 C15 仍含错误无关历史，不能当作完全修正；最终修正版见 [Run 3 manifest](results/20260913T034058Z-891cdbd3/manifest.json)，[指标](results/20260913T034058Z-891cdbd3/summary.json)，[人工评分模板](results/20260913T034058Z-891cdbd3/human_scores.json)。Run 3 两组均 1/1 可解析交付、3/3 State 检查通过、0/1 重复、100% Coverage、1/1 Feedback 关键词命中；人工分数仍为空。

## 自动指标

| 指标 | Run 1 Baseline | Run 1 Copilot | Run 2 Baseline | Run 2 Copilot |
|---|---:|---:|---:|---:|
| 案例数 | 16 | 16 | 4 | 4 |
| API 错误 | 0 | 0 | 0 | 0 |
| JSON 可解析任务 | 16/16 | 16/16 | 4/4 | 4/4 |
| State 确定性检查通过 | 38/38 | 38/38 | 10/10 | 10/10 |
| 完全重复 completed 任务 | 0/16 | 0/16 | 0/4 | 0/4 |
| 平均 Active JD Coverage | 90.42% | 90.42% | 91.67% | 91.67% |
| Feedback 关键词线索命中 | 6/6 | 6/6 | 3/3 | 3/3 |
| 人工 Actionability / Decision / Replanning | 待评 | 待评 | 待评 | 待评 |

State 子集不是完整理解准确率；Coverage 不是最优决策或 ROI。重复率在有可解析任务的全部案例上统计，其中 Run 1 只有 6 例有 completed 历史，相关子集同样为 0/6。Run 2 有 completed 历史 2 例，为 0/2。关键词命中不证明合理 Replanning。Baseline 的“可解析”只代表能提取字段；不代表通过 Copilot 的严格方向、时长与内容校验。Copilot 本轮均成功交付任务。

## AI-assisted Blind A/B Review

本轮不是新的模型 Run，没有重新采样或调用API，使用既有正式Run的匿名A/B输出及数据修正有效版本。评分由用户提供的 **AI-assisted blind review** 产生，按冻结 RUBRIC 评分；评分CSV先保存校验，之后才读取映射解盲，分数未改变。尚不是独立 Human Evaluation，External Human A/B Evaluation未执行，Owner已接受为非阻塞限制。

| 方案 | Wins | Losses | Ties | Actionability | Reasonableness | Replanning | Violation Case 数 |
|---|---:|---:|---:|---|---|---|---:|
| Career Copilot | 12 | 3 | 1 | 4.19 (n=16) | 4.56 (n=16) | 4.80 (n=10) | 4 |
| Direct LLM Baseline | 3 | 12 | 1 | 2.62 (n=16) | 4.00 (n=16) | 4.50 (n=10) | 11 |

Actionability / Reasonableness 每方16例；Replanning仅10个适用Case，N/A不计入分母。自动指标历史保持不变：State checks、Duplicate Rate、Coverage打平。不能将AI-assisted结果表述为独立人工验证，也不能据此宣称全面优势。

完整映射、分场景统计、Bad Pattern及限制见 [AI_ASSISTED_BLIND_RESULTS.md](AI_ASSISTED_BLIND_RESULTS.md)；原样评分及评语见 [AI_ASSISTED_BLIND_SCORES.csv](AI_ASSISTED_BLIND_SCORES.csv)。External Human Evaluation=NOT CONDUCTED；AC10=PARTIAL — ACCEPTED LIMITATION；最终发布见Release Checklist。

## Independent AI Blind Review #2

用户提供第二位独立AI Judge对同一匿名A/B Packet、相同冻结Rubric的完整盲评；据用户声明，两位Judge在各自完成评分前均未读取身份映射。本次先程序化保存Judge #2逐项原始评分并验证A=7/B=9/Tie=0，再读取既有密钥解盲。不是Human Evaluation，不是新模型Run，没有重新采样或调用API，没有修改任一Judge的评分。

| Judge | 方案 | W / L / T | Actionability | Reasonableness | Replanning | Violation Cases |
|---|---|---|---:|---:|---:|---:|
| #1 | Career Copilot | 12 / 3 / 1 | 4.1875 | 4.5625 | 4.8 | 4 |
| #1 | Direct LLM Baseline | 3 / 12 / 1 | 2.625 | 4 | 4.5 | 11 |
| #2 | Career Copilot | 13 / 3 / 0 | 4.25 | 3.5625 | 3.9 | 1 |
| #2 | Direct LLM Baseline | 3 / 13 / 0 | 2.25 | 2.75 | 2.8 | 10 |

Actionability/Reasonableness每方16例；Replanning每方10例，N/A不计入分母。Judge #2结果及全部理由见 [INDEPENDENT_AI_BLIND_SCORES_02.csv](INDEPENDENT_AI_BLIND_SCORES_02.csv)。不同Judge不合并平均原始分数。

## Inter-Judge Agreement

Preferred Output完全一致14/16=87.5%；C09为Baseline→Copilot的分歧，C16为Tie→Baseline的分歧，Tie不强行转换为胜负。两位Judge总体均偏好Career Copilot，最大稳定差异主要来自Task Actionability；completed均1:1，Long History未表现出稳定Copilot优势。

Violation判定一致26/32=81.25%，低于偏好一致率，但单位/分母不同；保留对无真实latest_feedback却引用反馈等问题的评审口径差异，不修改既有标记。完整分场景指标、分歧与限制见 [JUDGE_AGREEMENT.md](JUDGE_AGREEMENT.md)。

State checks、Duplicate Rate、Coverage打平的自动指标历史保持不变。16例小样本，不声称statistically significant；两位AI评审不等同独立Human Evaluation。AC10=PARTIAL — ACCEPTED LIMITATION；External Human Evaluation=NOT CONDUCTED，不再阻塞本版本。

## 观察与无优势场景

C01/C08 等 Copilot 输出给出具体操作，而 Baseline 部分输出仅为提升等级；C10 数据修复后 Copilot 聚焦剩余参数校验。它们是可审阅的输出差异，不能在未评分时折算成质量提升百分比。

正向 Gap、目标归档、完全重复、覆盖和反馈词语线索两组没有明显优势。C11 两组均响应十分钟限制。C16 两组都安排一条 GROUP BY 练习。Direct LLM 在这些给定事实案例中已能作出相同能力选择。

Copilot 也有问题：C06 缺少具体练习，C02 将内部等级说成外部标准，C14 Run 1 把推断称为反馈，C15 使用没有题目的编号练习。详见 [BAD_CASES.md](BAD_CASES.md)。因此自动指标过于粗粒度，人工评分是必要的发布前工作。

## 历史复现实验命令（V1.0不再追加运行）

```powershell
python -B -m evaluation.evaluator
python -B -m evaluation.evaluator --live --limit 16
python -B -m evaluation.evaluator --live --case-ids C10 C12 C14 C15
```

每轮新建时间戳 + 随机 ID 目录，绝不覆盖旧 Run。人工评审复制 human_scores.json 为独立评分附件，按冻结 RUBRIC.md 填分、评语、评审人及日期，保留原模板。未评分维持 null，不记作 0。人工 Smoke 另见 docs/SMOKE_TEST_RESULT.md。

## 局限

小样本虚构输入、各轮每组每例一次请求，未以重复采样评估随机波动；四例首轮数据污染不能算模型失败。修复数据只说明输入修正，不说明模型优化。无盲审人工分数、无真实用户效果、无 Summary 语义实验、无完整解析准确率。上述限制已被Owner接受；最终发布由技术验证决定，不据此声称人工评审完成。
