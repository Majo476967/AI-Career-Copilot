# V1.0 Bad Cases

## 最新人工复测结果（2026-09-14 记录）

依据用户本次人工 Smoke 完成报告，以下六项 Retest 更新为 PASS。主链总体为 PASS WITH OBSERVATION；这不是人工 Evaluation Rubric 评分，也不自动关闭历史实验中其他未复测案例。

| Bad Case | 最新人工 Retest | 证据 / 说明 |
|---|---|---|
| BC-JD-001 | PASS | Capability Normalization 与 Multi-JD 聚合通过 |
| BC-JD-002 | PASS | JD Required Level Calibration 及岗位等级语义通过 |
| BC-PROFILE-001 | PASS | 空能力 Profile 的确认保护通过 |
| BC-PROFILE-002 | PASS | Completeness Check 能识别原文 Python 对应 Programming 的漏项；不代表模型已不再漏提取 |
| BC-PROFILE-003 | PASS | 用户选择 Level、确认 Resume Evidence、人工加入 Programming，Draft 重新校验并成功 Confirm |
| BC-TASK-001 | PASS | 无真实 Feedback 时不再错误引用“最新反馈”，用户确认复测通过 |

BC-PROFILE-003 保留完整中间失败：Recovery UI 出现后曾报“包含不可修改的 Draft 字段”；根因是 generic update payload 复制了 protected validation metadata。只读证据确认 Programming 及 Evidence 已在 Draft 中，后续保存/确认被拦截；修复 payload 后人工 Confirm 成功，Retest=PASS。

## Remaining Observations

1. Task Actionability 仍有模型波动：部分任务偏“学习/记录”，后续任务已能出现明确动作、产出和验收标准。
2. Resume Analyzer 仍可能漏提取显式 Capability；Completeness Check + Human Recovery 降低风险，不代表 LLM 解析完全可靠。
3. Capability Progression 基于用户自报 completed Evidence，不是客观考试认证。
4. Evaluation样本仍较小，External Human A/B Evaluation未执行；Owner已接受为非阻塞限制与Future Work。

## 历史问题、修复与实验记录

以下原始 FAIL / pending / Retest=pending 表示对应历史时点，不覆盖顶部六项最新人工 PASS。其他 Evaluation Bad Case 的原始结果不修改；所有历史 Run 保留。

来源为真实 Run 1 / Run 2 原文及评测工具离线测试；以下为代码与输出审查，**不是人工 Rubric 分数**。首轮不删除，不为提升成绩修改产品 Prompt。

Run 1：`results/20260913T033148Z-a79c2e86/`，16 例。Run 2：`results/20260913T033607Z-db115c43/`，仅复测 C10 / C12 / C14 / C15。

| ID / Case / Scenario | 分类 | Expected | Actual | Root Cause / 假设 | Fix | Retest |
|---|---|---|---|---|---|---|
| E01 / C09 等 / fixture | Evaluation Data | partial 无 completed_at | 初次离线 seed 违反 SQLite CHECK | 夹具为所有终态设置完成日期 | 仅 completed 写完成日期，未改产品 | 全 16 例离线接入通过 |
| E02 / C10,C12,C14,C15 / history | Evaluation Data | 历史文本与能力一致 | Agent/Evaluation/ProductDesign 误填 JOIN 练习，两组跟随错误输入 | 公共夹具模板未按能力区分 | 修正四例任务文本；Run 1 manifest 保留旧案例 | Run 2 C10/C12 已不混入 JOIN，C14/C15 见原文；不能归因为产品变强 |
| E03 / alias level / metric | Evaluation Data | UserResearch 与 User Research 同一能力 | 原指标查当前 Level 时未规范化别名 | 指标实现遗漏；本批正向 Gap 判定未改变 | 规范化 Current Level 查询，补反例测试 | 离线测试通过；不覆盖 Run 1 指标 |
| B01 / C02 / unknown evidence | Evidence / Task Planning | 下一未达等级的证据任务、预算内 | Baseline 要求直接提升到 2 级并假设 10 天；Copilot 仍引用未定义的“评估等级2”权威标准 | Prompt 约束不能证明语义正确；模型误把内部等级当外部标准 | 标记 limitation，未调业务 Prompt | 待人工；未复测此例 |
| B02 / C06 / multi-JD | Task Planning | 明确题目、产出及可核验条件 | Copilot“完成至少2个 Evaluation 实际练习”没有给出案例内容 | 字段/长度校验无法保证具体性 | limitation；人工 Actionability 必须评估 | 未复测 |
| B03 / C14 / target change | Replanning | 不捏造最新反馈 | Run 1 Copilot 声称“根据最新反馈，用户需要完成中级实践任务”，对应上下文无此反馈 | 将自身任务推断写为用户事实 | 记录限制；未改产品，仅关联 E02 数据修复 | Run 2 此句未出现，但不能证明普遍解决 |
| B04 / C09,C15 / history | Memory Retrieval / Duplicate | 根据已完成部分推进，明确具体练习 | C09 仍称“第2组 JOIN”，C15“第22组窗口函数”无具体题目，两轮重复出现 | 词语命中不等于理解，normalized 去重不能判语义 | limitation | C15 Run 2 仍存在；C09 未复测 |
| B05 / C13 / target change | Structured Output / Task Planning | 1 小时预算、N min | Baseline 返回 8 hours；其他部分案例 estimated_time 返回叙述句 | Direct Prompt 无产品验证门；JSON 可解析不等于任务合规 | 原文保留；报告区分可解析与产品校验 | 未复测 |

## 分类覆盖与未观测范围

| 类别 | 当前记录状态 |
|---|---|
| Resume Parsing | 本轮状态快照实验未覆盖真实解析；等人工 Smoke，不宣称无错误 |
| JD Understanding | 本轮使用确认后的 JD；真实解析待人工 |
| Capability Mapping | E03 是评测指标别名问题，不算模型理解错误 |
| Evidence | B01；自报完成不等于客观掌握 |
| Priority | 公式离线验证；本轮未观察零 Gap 被选中，不代表权重最优 |
| Memory Retrieval | B04；未实验验证 Rolling Summary 语义质量 |
| Task Planning | B01/B02/B05 |
| Duplicate Task | B04 为语义审阅线索；确定性完全重复率为 0 |
| Replanning | B03/B04 |
| Structured Output | B05 时间语义不合规；本轮均为可解析 JSON，无 API Error |

不做新特性或算法调参。所有核心产品文件保持不变；待 Owner 审查局限是否阻止发布。

## 最终夹具回归发现

E04 / C15 / Evaluation Data：新增测试发现历史能力的实际名字是 `Product Design`，第一次修复仅匹配 `ProductDesign`，故 Run 2 C15 的无关 JOIN 历史仍然存在。已补正匹配，测试禁止非 SQL 夹具含 JOIN 历史。Run 3 `results/20260913T034058Z-891cdbd3/` 仅复测 C15；保留全部原文和指标，不修改前两轮。总请求数 42。数据修复的遗漏不能归为产品或模型错误。

## 人工 Smoke 阻塞问题（用户报告，2026-09-13 记录）

- **BC-JD-001 / Capability Mapping / FAIL**：三个 Active JD 成功加入，但 Python、SQL、数据分析的同义能力未合并，Coverage 几乎均为 1/3。期望按 canonical capability 聚合为 2/3 或 3/3。根因待代码核查；原始失败保留，修复后的人工复测待执行。
- **BC-JD-002 / JD Understanding / FAIL**：“必须能够用 SQL 查询和分析业务数据”被解析为 required_level=0，UI 显示“当前证据不足”。期望岗位实践要求为 2，且岗位等级不使用 User State 的证据文案。根因待代码核查；修复后的人工复测待执行。

执行日期、模型配置未由用户提供；不推断。此次为真实用户 Smoke 报告，不是先前虚构 Evaluation Run。

### BC-JD-001 / BC-JD-002 修复与离线复测

根因：旧 normalize_capability 仅支持完整 alias；JD 校验复用了 User Level 的 0～4 解释，未校准 Evidence 中的动作强度；Target Jobs 复用了 level_label。

修复：强匹配加 alias、保留 raw_names、所有汇总统一 canonical；JD 专用确定性 Evidence 校准；旧 JSON 读取投影应用相同规则；未知 0 阻止 Priority 计算并提示补充；岗位等级使用独立文案。用户 Evidence 的“仅关键词不能升级”校验继续使用精确 alias，避免强归一化误伤真实经历文本。

离线复测：tests/test_jd_calibration.py 新增 19 项；原 275 项保持通过，总计 294 项通过，未调用真实 API。覆盖 3/3、2/3 Coverage、Archived 排除、两条 SQL Level 2 表达、项目 Level 3、未知深度、原名保留、旧记录不变及两种 UI 文案。

人工复测：**待执行**。保留上方 FAIL，不把离线通过写为人工成功。规则无法覆盖全部自然语言；未命中规则的既有正整数等级仍是 Analyzer 推断，需原文核对。Spec 已同步此边界。

## BC-PROFILE-001 — Resume Evidence 存在但能力列表为空

来源：用户人工 Smoke 报告；2026-09-13 只读核查。检查进程未继承 CAREER_COPILOT_DB；runtime 中仅一个 smoke 数据库 `smoke_20260913_124526_bbb76d9729e041cba385028527dc9b51.sqlite3`，其最新快照与用户报告一致。以 mode=ro / query_only 访问，未初始化或修改数据库。

Expected：明确的技能/项目被提取为可核对的 Capability Evidence，用户确认后原子保存，规划使用实际确认的等级。

Actual：user_profile.resume_text 有 SQL 查询 Demo 与基础描述；profile_json.capabilities=[]；已确认 Draft #1 的 capabilities=[]；user_capabilities 共 0 条；Resume 来源 capability_evidence 共 0 条，SQL/Programming/Data Analysis 均无记录。PROFILE_CONFIRMED payload.confirmed_profile.capabilities=[]；最新 snapshot.capability_state_json=[]。缺失 SQL 后默认 Current Level 0，产生 Required 2 / Gap 0.5 / Score 0.85。

Root Cause：Profile validation 只检查已有条目的格式与来源，允许明确有技能的简历对应空 capabilities；Confirm 将该空列表原样提交，规划按缺失能力使用 0。未发现名称错配或事务部分写入证据。数据库没有原始模型回复或草稿编辑历史，不能证明初始 Analyzer 就返回空列表，也不能排除确认前移除能力；可确定的故障边界是“空能力 Draft 被允许确认”。

Fix：加强 Resume Analyzer 的逐项技能/项目能力覆盖指令；validate_profile 检测原文中的已知强匹配能力，若 capabilities 全空则返回 incomplete_profile，在分析、编辑和确认边界拒绝该结果。不自动补能力等级、不按 Demo 名称分支、不修改 Priority。User Capability 继续共用 canonical vocabulary，新增 raw_names 保留；Evidence 原文及 Confirm 原子事务不变。

Retest：新增 tests/test_profile_evidence_chain.py 10 项离线测试；总 311 项通过，原 301 项保留通过。覆盖知识/实践 Evidence、别名、Draft/Confirm/Planning、空模型输出、旧空 Draft、清空操作与事务回滚。全部 Fake LLM / 临时 SQLite，无真实 API。

Status：代码修复、离线通过；人工重解析/确认复测待执行，原数据库失败数据保留。此保护针对已识别的全空能力遗漏，不声称覆盖所有单项漏提取；合法等级仍由分析与用户核对，不由关键词赋值。

## BC-PROFILE-002 — 非空 Profile 仍漏提取显式能力

记录日期：2026-09-14。来源：用户人工 Smoke 报告及对 runtime 唯一 smoke 数据库的只读核查；未改动数据。

- Expected：原文“了解 SQL 基础、Python 基础及数据分析概念”中显式能力应由 Analyzer 覆盖，缺项时判 incomplete_profile，不把遗漏变成 Level 0。
- Actual：最新已确认 Draft #4 及 user_capabilities 只有 SQL=2 / Data Analysis=1，没有 Programming。原始 Analyzer 回复没有留存，无法单独还原模型输出与草稿修改；确认后的漏项可直接验证。
- Root Cause：BC-PROFILE-001 的 coverage 检查仅在 capabilities 全空时执行；非空列表漏掉 Programming 会通过。旧片段归一化还可能把同一句多个能力当成一个名字，不能用它代替逐关键词覆盖检查。Confirm 持久化的是已漏项 Draft，没有发现名称错配或部分写入故障。
- Fix：core/capabilities.py 提供高置信显式词检索，逐词使用既有 canonical normalization；validation 比较显式集合与已抽取集合，报告 missing canonical capabilities 并拒绝不完整输入。在分析、编辑、确认边界复用；不补写 Capability、不猜 Level、不修改既有确认记录。修正离线 phase2 夹具原本缺少的 Python 能力，与其虚构原文对齐。
- Retest = pending（人工）。新增测试覆盖同句多能力、只缺 Python、canonical alias、模糊文本、词边界、输入不变及确认拒绝；全量离线 326 项通过，原 311 项全部保留通过。

## BC-TASK-001 — 无反馈归因错误与内部枚举泄露

与先前 B03 / Replanning 归因问题关联；本次来源为真实人工 Smoke，不能用之前的 Evaluation 输出替代。

- Expected：latest_feedback 不存在时，reason 只能引用上下文中实际存在的事实；内部 gap_type 以中文显示。
- Actual：只读核查 Task Feedback Event 数量为 0，最新任务理由却以“根据最新反馈”开头，并含 evidence_knowledge_verification。
- Root Cause：MemoryService 无反馈时正确构造 latest_feedback=None；TaskService 持久化 Planner 的结果。Planner Prompt 曾无条件要求使用 latest_feedback，结构校验未检查反馈归因，UI 直接输出 reason，因此虚构归因与枚举均进入可见文字。
- Fix：只修改 Prompt 的反馈条件和枚举表述，不调 Task 内容设计；TaskPlanner 对 None/空 latest_feedback 的反馈归因返回 unsupported_feedback_attribution，不保存该任务，不自动增加模型调用。非空真实反馈允许引用，但仍不能虚构其内容。统一 reason 中文映射：evidence_knowledge_verification→补充或核实基础能力证据，practice→实践应用，experience→真实场景经验，depth→深度能力。生成验证和 UI 历史展示使用同一映射，数据库内部 enum 与原始历史不改。
- Retest = pending（人工）。离线测试验证四种归因拒绝、有反馈允许、仅 State 理由通过、失败不落任务、枚举映射及任务文本不变。两项 Bad Case 共新增 15 项，326 项全通过，无真实 API 调用。

边界：显式词检查只发现明显遗漏，不证明完整语义提取；理由归因校验使用明确模式，不声称穷尽所有自然语言幻觉。未更改 Priority Formula、任务内容设计或 Evaluation 历史 Run。已保存错误记录不重写，待人工核对完整 Profile 并重新规划后再验收。

## BC-PROFILE-003 — Incomplete Profile Detection Works, But User Cannot Repair The Draft

记录日期：2026-09-14；来源为用户人工 Smoke 报告。保留前述失败记录，不修改 Smoke 数据。

- Expected：检测到明显能力漏项后保留部分分析，用户可以在 Draft 中补充或明确不纳入；全部漏项处理后才能 Confirm。
- Actual：Resume 明确有 Python 基础，连续两次模型输出仍漏 Programming；completeness 正确报错，但产品只能重新分析，没有人工恢复入口。
- Root Cause：Analyzer/validation 在 completeness 失败时直接抛异常，ProfileService 因而没有创建可恢复 Draft；UI 只有已有能力的固定行编辑，缺少处理 missing capabilities 的操作。
- Fix：只放宽 completeness 的 Draft 保存路径，格式/来源/等级校验仍严格。在现有 profile_drafts.draft_json 保存 validation_status、missing_capabilities 和 ignored_missing_capabilities，不新增表或修改当前数据库。missing 保存 canonical_name、matched_resume_terms、原文 evidence_snippets，不带推测等级。
- Recovery：UI“检测到可能遗漏的能力”显示依据；添加须用户选择 Level（默认未选择）并确认候选证据；不纳入是当前 Draft 的显式 override。ProfileService.resolve_missing_capability 在事务内重新检测并保存 Draft，每次操作后重算 completeness，不调用 LLM、不写 Current State。无关或重复处理明确拒绝。
- Evidence：用户添加后才保存 source=resume、evidence_type=user_confirmed_resume_evidence 与原文 content；标明用户确认而非 LLM 认证。高等级仍受项目/实习等原有证据规则约束。
- Confirm：始终从原文与 Capability 重新验证，忽略伪造的 validation_status/missing 列表；未处理漏项不能写正式状态。模型不能提供 ignore override；通用编辑接口也不能直接修改 ignored 列表。
- Retest：pending（人工）。新增 16 项离线 Service/AppTest 测试，验证 incomplete 保存、添加、用户选级、ignore 隔离、服务端防绕过、证据持久化及按钮解锁。原“空分析不创建草稿”测试按本轮新要求改为“保存 incomplete 但禁止确认”，保留其 Current State 不受污染的检查。

未调整 Priority Formula、JD、Task Planner、任务内容或全局词表；未静默补能力/等级，无额外 LLM 重试，Evaluation 历史 Run 未改。

BC-PROFILE-003 最终离线验证：342 项全部通过（原 326 项回归 + 新增 16 项），git diff --check 通过。人工 Retest 仍为 pending。

### BC-PROFILE-003 人工复测：受保护 metadata 进入普通更新路径

记录日期：2026-09-14。用户回报：Recovery UI appeared, but persistence failed because protected Draft metadata was sent through the generic Draft update path。

只读核查进一步区分失败位置：唯一 Smoke 库的最新 Draft #5 已是 validation_status=valid，missing_capabilities=[]，Programming=1 与 user_confirmed_resume_evidence 已真正写入；Draft 生命周期仍为 draft。故不是 Add 未落库，而是其后的普通保存/确认被拦截。检查未修改该库。

Root Cause：Recovery 按钮已使用专用 resolve_missing_capability，服务端原子更新并返回重新读取的 Draft；但 ui.adapter.profile_changes 复制完整 draft_json，额外携带 validation_status、missing_capabilities、ignored_missing_capabilities，随后 update_profile_draft 的可编辑字段白名单正确拒绝它们。此前 UI 回归只测到按钮解锁，没有继续覆盖普通保存与确认。

Fix：profile_changes 仅构造 education / internships / projects / skills / capabilities / major / target_direction / available_hours_per_day 八个字段；不传 validation metadata、生命周期或 provenance。普通 Service 白名单不变，恢复 API 不新增或放宽。Add/Ignore 的服务端缺项检测、选级/原文校验、重算、事务保存和 Confirm 再验证继续有效；重复操作被拒绝，不产生重复能力或 Evidence。

Retest = pending（人工）。新增六项离线回归覆盖 payload 白名单、Add→普通 Save→Confirm、Ignore→Save→Confirm、内部字段拒绝、独立连接验证重复 Add 无重复数据，以及 Streamlit 新会话读库后完整确认。旧失败记录和当前 Smoke 数据保留，未调用真实 API。

## V1.0 Owner Evaluation Release Decision — 2026-09-14

Evaluation：COMPLETE WITH LIMITATIONS。AC10：PARTIAL — ACCEPTED LIMITATION。External Human A/B Evaluation：NOT CONDUCTED（不是PASS），作为Future Work，不再阻塞本次V1.0 Release；不追加AI Judge或外部人工A/B评测。

Owner接受理由：真实用户Manual Smoke和Bad Case Retest已完成，Automatic Evaluation及两轮独立Blind AI Review已完成；Judge #1偏好Copilot 12 / Baseline 3 / Tie 1，Judge #2为13 / 3 / 0，Preferred Agreement=14/16=87.5%。对于当前个人项目V1.0，继续增加评审的边际收益较低。此为Owner接受限制，不是把AI评审当成人工评审。

自动指标State checks、Duplicate Rate、Coverage两方打平；AI评审中的稳定差异主要来自Task Actionability。Long History未体现Copilot稳定优势，不能宣称所有场景都胜出或统计显著。Copilot Constraint Violation Cases为Judge #1的4例、Judge #2的1例（Baseline分别11、10），口径分歧保留。Priority是准备优先级heuristic，非数学最优或最优ROI；能力升级基于用户自报Evidence，非客观考试认证。

Final Release以RELEASE_CHECKLIST.md的最终技术验证为准；接受Evaluation限制不豁免测试、依赖、安全与文档检查。历史评分和Run保持原样，旧的人工评审PENDING记录仅代表当时状态。
