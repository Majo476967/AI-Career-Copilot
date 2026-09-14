# Inter-Judge Agreement Analysis

记录日期：2026-09-14。Independent AI Blind Review #2：**COMPLETE**；Inter-Judge Agreement Analysis：**COMPLETE**。不是 Human Evaluation；AC10 **PARTIAL — ACCEPTED LIMITATION**，External Human Evaluation **NOT CONDUCTED**；最终发布见Release Checklist。

## 评审来源与实验完整性

用户提供两位独立 AI Judge 的盲评，声明使用同一匿名 A/B Packet、同一冻结 RUBRIC，且各自在评分完成前未读取身份映射。该独立性和盲评过程依据用户声明，并非本次额外验证的运行日志；未推断第二位Judge的模型身份。本次只解析、保存和统计，不重新评分或调用模型/API。

Judge #2 从附件《16个Case A/B方案盲评结果》程序化提取32份评分、Notes及全部逐维理由，保存在 INDEPENDENT_AI_BLIND_SCORES_02.csv；另存原文各方案片段、偏好理由及来源SHA-256。先保存并回读校验 A=7/B=9/Tie=0，再读取既有密钥核对映射。上一版 A=6/B=10 为已确认笔误，不作为数据来源。解析未采用附件末尾的另起任务建议。

评分CSV SHA-256：`aa6d3e38b313e8b3060e13f4a3c004ed43b2e597a04b48211a2c6b0caec5cd27`。Judge #1评分、Rubric、Cases、原始Runs、匿名包与映射均未修改。

现有Packet使用Run 1 `20260913T033148Z-a79c2e86` 的其余12例、Run 2 `20260913T033607Z-db115c43` 的C10/C12/C14、Run 3 `20260913T034058Z-891cdbd3` 的C15。两Judge评分同一组16例输出，不是32个独立Case，不是新的模型Run，不代表当前修复版本的重新评测。

## 总体指标

| Judge | 方案 | W / L / T | Actionability | Reasonableness | Replanning | Violation Cases |
|---|---|---|---:|---:|---:|---:|
| #1 | Career Copilot | 12 / 3 / 1 | 4.1875 | 4.5625 | 4.8 | 4 |
| #1 | Direct LLM Baseline | 3 / 12 / 1 | 2.625 | 4 | 4.5 | 11 |
| #2 | Career Copilot | 13 / 3 / 0 | 4.25 | 3.5625 | 3.9 | 1 |
| #2 | Direct LLM Baseline | 3 / 13 / 0 | 2.25 | 2.75 | 2.8 | 10 |

每个Judge每方Actionability / Reasonableness n=16；Replanning仅10个适用Case（C07～C16），C01～C06 N/A不计入分母。均分为Case等权算术平均；展示最多4位小数（Judge #1原报告的两位显示4.19/2.62等保持不改）。Violation为Case计数，不是违规条目数量。

## Preferred Agreement

完全一致14/16，Exact Preferred Agreement=87.5%。Tie作为独立类别，未强制转换为胜负。

- C09 partial：Judge #1偏好Direct LLM Baseline，Judge #2偏好Career Copilot。
- C16 long_history：Judge #1为Tie，Judge #2偏好Direct LLM Baseline。

| Case | Scenario | Judge #1 A/B | Judge #1 解盲 | Judge #2 A/B | Judge #2 解盲 | 一致 |
|---|---|---|---|---|---|---|
| C01 | single_jd | B | Career Copilot | B | Career Copilot | Yes |
| C02 | single_jd | A | Career Copilot | A | Career Copilot | Yes |
| C03 | single_jd | B | Career Copilot | B | Career Copilot | Yes |
| C04 | multi_jd | B | Career Copilot | B | Career Copilot | Yes |
| C05 | multi_jd | A | Career Copilot | A | Career Copilot | Yes |
| C06 | multi_jd | B | Career Copilot | B | Career Copilot | Yes |
| C07 | completed | B | Direct LLM Baseline | B | Direct LLM Baseline | Yes |
| C08 | completed | B | Career Copilot | B | Career Copilot | Yes |
| C09 | partial | B | Direct LLM Baseline | A | Career Copilot | No |
| C10 | partial | B | Career Copilot | B | Career Copilot | Yes |
| C11 | not_completed | A | Career Copilot | A | Career Copilot | Yes |
| C12 | not_completed | B | Career Copilot | B | Career Copilot | Yes |
| C13 | target_change | A | Career Copilot | A | Career Copilot | Yes |
| C14 | target_change | A | Career Copilot | A | Career Copilot | Yes |
| C15 | long_history | A | Direct LLM Baseline | A | Direct LLM Baseline | Yes |
| C16 | long_history | Tie | Tie | B | Direct LLM Baseline | No |

## Scenario-level Preferred Results

| Scenario | Case 数 | Judge | Copilot / Baseline / Tie |
|---|---:|---|---|
| single_jd | 3 | #1 | 3 / 0 / 0 |
| single_jd | 3 | #2 | 3 / 0 / 0 |
| multi_jd | 3 | #1 | 3 / 0 / 0 |
| multi_jd | 3 | #2 | 3 / 0 / 0 |
| completed | 2 | #1 | 1 / 1 / 0 |
| completed | 2 | #2 | 1 / 1 / 0 |
| partial | 2 | #1 | 1 / 1 / 0 |
| partial | 2 | #2 | 2 / 0 / 0 |
| not_completed | 2 | #1 | 2 / 0 / 0 |
| not_completed | 2 | #2 | 2 / 0 / 0 |
| target_change | 2 | #1 | 2 / 0 / 0 |
| target_change | 2 | #2 | 2 / 0 / 0 |
| long_history | 2 | #1 | 0 / 1 / 1 |
| long_history | 2 | #2 | 0 / 2 / 0 |

single_jd / multi_jd / not_completed / target_change两位Judge完全同方向；completed均为1:1。partial仅C09有分歧；long_history两位Judge均未显示Copilot优势。

## 评分尺度与方向

不跨Judge平均原始分数。Judge #2的绝对评分尺度与Judge #1明显不同，尤其Reasonableness和Replanning；只分别报告偏好方向、维度排序和分差方向。下表Δ=Copilot均分−Baseline均分：

| Judge | Δ Actionability | Δ Reasonableness | Δ Replanning |
|---|---:|---:|---:|
| #1 | 1.5625 | 0.5625 | 0.3 |
| #2 | 2 | 0.8125 | 1.1 |

两位Judge总体三维分差都为正，最大且稳定的差异来自Task Actionability；这不意味着全部场景都优于另一方。

| Scenario | Judge | 方案 | Actionability | Reasonableness | Replanning | Violations |
|---|---|---|---:|---:|---:|---:|
| single_jd | #1 | Career Copilot | 4.3333 | 4 | N/A | 2 |
| single_jd | #1 | Direct LLM Baseline | 1.3333 | 3.3333 | N/A | 3 |
| single_jd | #2 | Career Copilot | 4.6667 | 3.6667 | N/A | 0 |
| single_jd | #2 | Direct LLM Baseline | 1.3333 | 2.3333 | N/A | 3 |
| multi_jd | #1 | Career Copilot | 4 | 4.3333 | N/A | 1 |
| multi_jd | #1 | Direct LLM Baseline | 1.3333 | 3 | N/A | 3 |
| multi_jd | #2 | Career Copilot | 4.3333 | 3 | N/A | 0 |
| multi_jd | #2 | Direct LLM Baseline | 1.3333 | 2.3333 | N/A | 3 |
| completed | #1 | Career Copilot | 4.5 | 5 | 5 | 0 |
| completed | #1 | Direct LLM Baseline | 3.5 | 4.5 | 5 | 1 |
| completed | #2 | Career Copilot | 4 | 3.5 | 3.5 | 0 |
| completed | #2 | Direct LLM Baseline | 3 | 3 | 3 | 1 |
| partial | #1 | Career Copilot | 4.5 | 5 | 4.5 | 0 |
| partial | #1 | Direct LLM Baseline | 4 | 4.5 | 4 | 1 |
| partial | #2 | Career Copilot | 4.5 | 4 | 4.5 | 0 |
| partial | #2 | Direct LLM Baseline | 3 | 3 | 2.5 | 1 |
| not_completed | #1 | Career Copilot | 3.5 | 5 | 5 | 0 |
| not_completed | #1 | Direct LLM Baseline | 3.5 | 4 | 3.5 | 1 |
| not_completed | #2 | Career Copilot | 4.5 | 4 | 4.5 | 0 |
| not_completed | #2 | Direct LLM Baseline | 2 | 2.5 | 2 | 1 |
| target_change | #1 | Career Copilot | 4.5 | 4 | 4.5 | 1 |
| target_change | #1 | Direct LLM Baseline | 2 | 4.5 | 5 | 2 |
| target_change | #2 | Career Copilot | 4.5 | 4 | 4 | 0 |
| target_change | #2 | Direct LLM Baseline | 2 | 2.5 | 2.5 | 1 |
| long_history | #1 | Career Copilot | 4 | 5 | 5 | 0 |
| long_history | #1 | Direct LLM Baseline | 4 | 5 | 5 | 0 |
| long_history | #2 | Career Copilot | 3 | 3 | 3 | 1 |
| long_history | #2 | Direct LLM Baseline | 4 | 4 | 4 | 0 |

## Constraint Violation Agreement

Judge #1：Copilot 4 / Baseline 11；Judge #2：Copilot 1 / Baseline 10。

以同一Case同一方案的Yes/No为单位，一致26/32=81.25%，低于Preferred的87.5%；Copilot一致11/16=68.75%，Baseline一致15/16=93.75%。这两个agreement的单位和分母不同，不直接当成相同统计量。

Constraint Violation classification shows lower inter-rater agreement.

| Case | 方案 | Judge #1 | Judge #2 |
|---|---|---|---|
| C01 | Career Copilot | Yes | No |
| C03 | Career Copilot | Yes | No |
| C04 | Career Copilot | Yes | No |
| C13 | Career Copilot | Yes | No |
| C14 | Direct LLM Baseline | Yes | No |
| C16 | Career Copilot | No | Yes |

C01/C03/C04/C13的Copilot回复被Judge #1判为无真实反馈却引用最新反馈，Judge #2未判违规。C14 Baseline的泛化学习任务，Judge #1判违规、Judge #2认为质量低但无明确违规。C16 Copilot的60分钟单题任务，Judge #2判时间不合理、Judge #1未判违规。均为既有评审口径差异，未事后统一评分。

另保留原文中值得人工审阅的口径：Judge #2对C16两份同为60分钟单题的任务作出不同Violation判断，其对另一方案“基础薄弱”的说明是评审原文，不是本报告认可的用户事实。该差异留待人工复核，不修改评分。

## 结论与剩余Gate

两位AI Judge均偏好Copilot的总体输出，Task Actionability差异最稳定；completed无整体胜出，long_history无稳定Copilot优势。State checks、Duplicate Rate、Coverage打平的历史结论继续保留。不声称statistically significant；只有16个虚构案例，两位AI评审可能存在共同偏差，不构成独立Human Evaluation或真实求职收益证明。

External Human Evaluation未执行，Owner已接受为非阻塞限制，留作Future Work。Final Release依赖技术验证。未修改业务代码，不commit，不tag。

## V1.0 Owner Evaluation Release Decision — 2026-09-14

Evaluation：COMPLETE WITH LIMITATIONS。AC10：PARTIAL — ACCEPTED LIMITATION。External Human A/B Evaluation：NOT CONDUCTED（不是PASS），作为Future Work，不再阻塞本次V1.0 Release；不追加AI Judge或外部人工A/B评测。

Owner接受理由：真实用户Manual Smoke和Bad Case Retest已完成，Automatic Evaluation及两轮独立Blind AI Review已完成；Judge #1偏好Copilot 12 / Baseline 3 / Tie 1，Judge #2为13 / 3 / 0，Preferred Agreement=14/16=87.5%。对于当前个人项目V1.0，继续增加评审的边际收益较低。此为Owner接受限制，不是把AI评审当成人工评审。

自动指标State checks、Duplicate Rate、Coverage两方打平；AI评审中的稳定差异主要来自Task Actionability。Long History未体现Copilot稳定优势，不能宣称所有场景都胜出或统计显著。Copilot Constraint Violation Cases为Judge #1的4例、Judge #2的1例（Baseline分别11、10），口径分歧保留。Priority是准备优先级heuristic，非数学最优或最优ROI；能力升级基于用户自报Evidence，非客观考试认证。

Final Release以RELEASE_CHECKLIST.md的最终技术验证为准；接受Evaluation限制不豁免测试、依赖、安全与文档检查。历史评分和Run保持原样，旧的人工评审PENDING记录仅代表当时状态。
