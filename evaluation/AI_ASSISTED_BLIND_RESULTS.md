# AI-assisted Blind A/B Review Results

记录日期：2026-09-14。状态：**AI-assisted Blind Review COMPLETE**；**Human Evaluation Scoring PENDING**；**Human Sign-off PENDING**；**V1.0 Final Release PENDING**。

## 来源与保存顺序

评分来源是用户提供的 ChatGPT blind review，review_method=AI-assisted blind A/B scoring；用户本人尚未填写 HUMAN_SCORES_TEMPLATE.csv。本报告不是独立 Human Evaluation。

本次先从用户附件逐字录入16例评分与notes，保存并重新读取 AI_ASSISTED_BLIND_SCORES.csv，验证 A=6/B=9/Tie=1、32份评分和N/A规则后，才读取 human_scoring_key.json 解盲。未根据身份改变任何评分。盲评本身由用户报告已在不知道身份时按冻结 Rubric 完成；本次工作仅录入、解盲和统计，不另行评分。

冻结评分 CSV SHA-256：`1f83eee1b730b66005be8fcbbf9c3c429b192b3c5fa13d0146490a5291c428ac`。

使用既有匿名包有效版本：其余12例来自 `20260913T033148Z-a79c2e86`；C10/C12/C14 来自 `20260913T033607Z-db115c43`；C15 来自 `20260913T034058Z-891cdbd3`。每例两方来自同一Run。不是新模型Run，未重新采样、未调用API。原始回复中的Bad Case保留；不能把本轮评分当作后续修复版本的重新评测。

## 总体

| 方案 | Wins | Losses | Ties | Actionability | Reasonableness | Replanning | Violation Case 数 |
|---|---:|---:|---:|---|---|---|---:|
| Career Copilot | 12 | 3 | 1 | 4.19 (n=16) | 4.56 (n=16) | 4.80 (n=10) | 4 |
| Direct LLM Baseline | 3 | 12 | 1 | 2.62 (n=16) | 4.00 (n=16) | 4.50 (n=10) | 11 |

16 Case；Actionability / Reasonableness 每方 n=16；Replanning 每方 n=10，C01～C06 为 N/A，不计入分母。均值为Case等权算术平均，显示两位小数；不计算三维混合总分。Violation为至少一个违规的方案Case计数，不是违规条目总数。

## Scenario Type

| Scenario | Case 数 | 方案 | W / L / T | Actionability | Reasonableness | Replanning | Violations |
|---|---:|---|---|---|---|---|---:|
| single_jd | 3 | Career Copilot | 3 / 0 / 0 | 4.33 (n=3) | 4.00 (n=3) | N/A (n=0) | 2 |
| single_jd | 3 | Direct LLM Baseline | 0 / 3 / 0 | 1.33 (n=3) | 3.33 (n=3) | N/A (n=0) | 3 |
| multi_jd | 3 | Career Copilot | 3 / 0 / 0 | 4.00 (n=3) | 4.33 (n=3) | N/A (n=0) | 1 |
| multi_jd | 3 | Direct LLM Baseline | 0 / 3 / 0 | 1.33 (n=3) | 3.00 (n=3) | N/A (n=0) | 3 |
| completed | 2 | Career Copilot | 1 / 1 / 0 | 4.50 (n=2) | 5.00 (n=2) | 5.00 (n=2) | 0 |
| completed | 2 | Direct LLM Baseline | 1 / 1 / 0 | 3.50 (n=2) | 4.50 (n=2) | 5.00 (n=2) | 1 |
| partial | 2 | Career Copilot | 1 / 1 / 0 | 4.50 (n=2) | 5.00 (n=2) | 4.50 (n=2) | 0 |
| partial | 2 | Direct LLM Baseline | 1 / 1 / 0 | 4.00 (n=2) | 4.50 (n=2) | 4.00 (n=2) | 1 |
| not_completed | 2 | Career Copilot | 2 / 0 / 0 | 3.50 (n=2) | 5.00 (n=2) | 5.00 (n=2) | 0 |
| not_completed | 2 | Direct LLM Baseline | 0 / 2 / 0 | 3.50 (n=2) | 4.00 (n=2) | 3.50 (n=2) | 1 |
| target_change | 2 | Career Copilot | 2 / 0 / 0 | 4.50 (n=2) | 4.00 (n=2) | 4.50 (n=2) | 1 |
| target_change | 2 | Direct LLM Baseline | 0 / 2 / 0 | 2.00 (n=2) | 4.50 (n=2) | 5.00 (n=2) | 2 |
| long_history | 2 | Career Copilot | 0 / 1 / 1 | 4.00 (n=2) | 5.00 (n=2) | 5.00 (n=2) | 0 |
| long_history | 2 | Direct LLM Baseline | 1 / 0 / 1 | 4.00 (n=2) | 5.00 (n=2) | 5.00 (n=2) | 0 |

## A/B 解盲映射

| Case | 方案 A | 方案 B | Preferred（解盲） |
|---|---|---|---|
| C01 | Direct LLM Baseline | Career Copilot | Career Copilot |
| C02 | Career Copilot | Direct LLM Baseline | Career Copilot |
| C03 | Direct LLM Baseline | Career Copilot | Career Copilot |
| C04 | Direct LLM Baseline | Career Copilot | Career Copilot |
| C05 | Career Copilot | Direct LLM Baseline | Career Copilot |
| C06 | Direct LLM Baseline | Career Copilot | Career Copilot |
| C07 | Career Copilot | Direct LLM Baseline | Direct LLM Baseline |
| C08 | Direct LLM Baseline | Career Copilot | Career Copilot |
| C09 | Career Copilot | Direct LLM Baseline | Direct LLM Baseline |
| C10 | Direct LLM Baseline | Career Copilot | Career Copilot |
| C11 | Career Copilot | Direct LLM Baseline | Career Copilot |
| C12 | Direct LLM Baseline | Career Copilot | Career Copilot |
| C13 | Career Copilot | Direct LLM Baseline | Career Copilot |
| C14 | Career Copilot | Direct LLM Baseline | Career Copilot |
| C15 | Direct LLM Baseline | Career Copilot | Direct LLM Baseline |
| C16 | Career Copilot | Direct LLM Baseline | Tie |

## Bad Pattern Summary

以下归类仅整理冻结 notes，不重新评分、不修正原评分中的判断；同一 Case 可属于多类，类别数量不可相加作为独立失败数。

| 模式 | notes 对应案例（解盲后） |
|---|---|
| 任务只是提升至 Level X、验收循环定义或未定义等级 | Direct LLM Baseline：C01/C02/C03/C04/C05/C06/C08；Career Copilot：C02 的外部文档与等级定义仍有疑问 |
| 无依据时间估计 / 时间预算不匹配 | Direct LLM Baseline：C02/C03/C05/C06，C08 的20分钟与目标不匹配，C13 的8小时违反预算；Career Copilot：C02 的3篇文档/30分钟偏紧 |
| 不存在反馈却引用最新反馈，或将历史误称反馈依据 | Career Copilot：C01/C03/C04/C13 |
| partial 未保留已完成部分 | Direct LLM Baseline：C10 要求重新做且含已完成工具定义；Career Copilot：C09 虽识别卡点但仍包装成新JOIN组 |
| not_completed 未真正拆小原任务 | Direct LLM Baseline：C11；Career Copilot 的 C11 虽缩小，具体练习仍未定义 |
| 任务、题目或验收仍泛化 | 两方均存在：Career Copilot C05/C06/C07/C11/C12/C15/C16；Direct LLM Baseline C08/C12/C14/C16 等，具体以逐例 notes 为准 |
| Multi-JD 事实错误 / 权衡不足 | Direct LLM Baseline C04 错称5个Active JD均要求SQL，C06 缺少权衡；Career Copilot C14 理由可更明确比较覆盖 |

完整32份 notes 保存在评分 CSV，不只展示有利案例。Violation Yes/No 严格沿用提供值，例如 C02 的担忧未被擅自改为 Yes。偏好、分数与违规标记是不同维度，不相互覆盖。

## 解释与限制

本轮显示任务可执行性差异较明显，但不代表一方在全部场景全面优越。保留自动指标历史：State checks、Duplicate Rate、Coverage 打平；AI-assisted偏好不能改写这些结果。小样本、单一AI评审、离散主观评分，无独立人工确认，不推导统计显著性或真实求职收益。

仍需用户最终 sign-off / 独立人工确认；之后由Owner审核验收、Observations并批准最终发布。AC10保持PARTIAL。本次未修改Rubric、Cases、原始Runs、盲审包、评分模板或业务代码；不commit、不tag。
