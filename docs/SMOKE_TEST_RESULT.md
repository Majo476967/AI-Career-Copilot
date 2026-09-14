# V1.0 Human Smoke Test Result

## 当前结论：已完成 — PASS WITH OBSERVATION

更新记录日期：2026-09-14。依据：项目用户在本次对话中明确确认的真实人工 Smoke 结果。主链、持久化及下列六项 Bad Case 人工复测均通过；本轮文档更新未重新运行应用或调用 API。

具体执行时间、模型配置未补充，不推测填写。此结论不替代外部人工A/B评测；该评测未执行且已获Owner接受为非阻塞限制。最终发布见Release Checklist。

## 已通过的人工主链

| 编号 | 场景 | 用户确认的实际结果 | 判定 |
|---|---|---|---|
| S01 | 启动 | Streamlit 正常启动。 | PASS |
| S02 | Resume 输入 | Demo Resume 上传与解析完成。 | PASS |
| S03 | Draft 隔离 | Profile Draft 与正式 Profile 分离。 | PASS |
| S04 | 人工编辑 | 用户人工编辑 Profile 成功。 | PASS |
| S05 | Profile Confirm | Profile Confirm 成功。 | PASS |
| S06 | 多岗位添加 | 成功添加 3 个 Active JD。 | PASS |
| S07 | 能力聚合 | Multi-JD Capability Aggregation 通过。 | PASS |
| S08 | 岗位等级 | JD Required Level Calibration 通过。 | PASS |
| S09 | Priority | Priority 计算通过。 | PASS |
| S10 | Partial Feedback | Partial Feedback 提交成功。 | PASS |
| S11 | 反馈重规划 | Feedback-driven Replanning 生效。 | PASS |
| S12 | 持久化记录 | Feedback / Task / Planning Snapshot 持久化。 | PASS |
| S13 | 首次完成 | 第一次 completed 不提前升级。 | PASS |
| S14 | 任务重复 | 未重复生成相同任务。 | PASS |
| S15 | 阶段进展 | 第二个不同 completed Task 后，User Research Level 0 → 1。 | PASS |
| S16 | 升级后 Gap | Capability Level Change 后，User Research Gap 归零。 | PASS |
| S17 | 优先级切换 | Top Priority 从 User Research 切换到 Programming。 | PASS |
| S18 | Archive JD | Active JD 从 3 → 2，Priority 重算。 | PASS |
| S19 | Replace JD | 新 JD 生效、旧 JD 归档，Priority 从 Programming 切回 User Research。 | PASS |
| S20 | 完全重启 | Streamlit 完全重启后，Profile、JD、Capability、Priority、Current Task 均保留。 | PASS |

## 最新 Bad Case Retest

| Bad Case | 最新人工 Retest | 证据 / 说明 |
|---|---|---|
| BC-JD-001 | PASS | Capability Normalization 与 Multi-JD 聚合通过 |
| BC-JD-002 | PASS | JD Required Level Calibration 及岗位等级语义通过 |
| BC-PROFILE-001 | PASS | 空能力 Profile 的确认保护通过 |
| BC-PROFILE-002 | PASS | Completeness Check 能识别原文 Python 对应 Programming 的漏项；不代表模型已不再漏提取 |
| BC-PROFILE-003 | PASS | 用户选择 Level、确认 Resume Evidence、人工加入 Programming，Draft 重新校验并成功 Confirm |
| BC-TASK-001 | PASS | 无真实 Feedback 时不再错误引用“最新反馈”，用户确认复测通过 |

Recovery 中间曾出现“包含不可修改的 Draft 字段”。随后定位为 UI generic update payload 携带 protected metadata；只读诊断显示 Add 已持久化，失败发生在后续普通保存/确认。修正 payload 后，本次人工确认成功。中间失败记录继续保留。

## Remaining Observations

1. Task Actionability 仍有模型波动：部分任务偏“学习/记录”，后续任务已能出现明确动作、产出和验收标准。
2. Resume Analyzer 仍可能漏提取显式 Capability；Completeness Check + Human Recovery 降低风险，不代表 LLM 解析完全可靠。
3. Capability Progression 基于用户自报 completed Evidence，不是客观考试认证。
4. Evaluation样本仍较小，External Human A/B Evaluation未执行；Owner已接受为非阻塞限制与Future Work。

## V1.0 Owner Evaluation Release Decision — 2026-09-14

Evaluation：COMPLETE WITH LIMITATIONS。AC10：PARTIAL — ACCEPTED LIMITATION。External Human A/B Evaluation：NOT CONDUCTED（不是PASS），作为Future Work，不再阻塞本次V1.0 Release；不追加AI Judge或外部人工A/B评测。

Owner接受理由：真实用户Manual Smoke和Bad Case Retest已完成，Automatic Evaluation及两轮独立Blind AI Review已完成；Judge #1偏好Copilot 12 / Baseline 3 / Tie 1，Judge #2为13 / 3 / 0，Preferred Agreement=14/16=87.5%。对于当前个人项目V1.0，继续增加评审的边际收益较低。此为Owner接受限制，不是把AI评审当成人工评审。

自动指标State checks、Duplicate Rate、Coverage两方打平；AI评审中的稳定差异主要来自Task Actionability。Long History未体现Copilot稳定优势，不能宣称所有场景都胜出或统计显著。Copilot Constraint Violation Cases为Judge #1的4例、Judge #2的1例（Baseline分别11、10），口径分歧保留。Priority是准备优先级heuristic，非数学最优或最优ROI；能力升级基于用户自报Evidence，非客观考试认证。

Final Release以RELEASE_CHECKLIST.md的最终技术验证为准；接受Evaluation限制不豁免测试、依赖、安全与文档检查。历史评分和Run保持原样，旧的人工评审PENDING记录仅代表当时状态。

## 历史记录（非当前状态）

以下保留初始待执行清单、失败及修复过程。其中 FAIL / pending 是当时记录；上述主链与六项指定 Bad Case 的最新状态以本页顶部为准。未列入本次用户确认的其他场景，不推定通过。

状态：**待人工执行，不能认定 PASS**。编写日期：2026-09-13。实际执行日期、执行人、模型均待填写。离线 AppTest 与真实模型评测不能替代人工浏览器测试。

按 [MANUAL_SMOKE_TEST.md](MANUAL_SMOKE_TEST.md) 使用独立 runtime/smoke.sqlite3 和虚构 demo 文件。只记录脱敏结果。

| 场景 | 输入 | 预期 | 实际结果 | 判定 | 观察 |
|---|---|---|---|---|---|
| 启动四页 | streamlit run app.py | 空状态清晰、无异常 | 待执行 | PENDING | |
| DOCX 解析 | demo/resume.example.docx | 真实豆包生成 Draft | 待执行 | PENDING | |
| Profile 确认 | 修改并确认草稿 | 确认前无 Current State，确认后有 Evidence/Event | 待执行 | PENDING | |
| 三个岗位 | demo/jd-1～3.txt | 预览后确认，3 Active JD | 待执行 | PENDING | |
| 聚合与 Priority | 三岗位事实 | Coverage、正向 Gap、Top 可解释 | 待执行 | PENDING | |
| Task | 生成按钮 | 五字段、下一阶段、预算内 | 待执行 | PENDING | |
| partial | 真实观察到的卡点 | 原文保存、相关下一任务 | 待执行 | PENDING | |
| completed / progression | 两个不同有效阶段任务完成 | 单次不升，阈值后保守升一级并重算 | 待执行 | PENDING | |
| archive / replace | 虚构新 JD | 旧归档、重算、保留历史 | 待执行 | PENDING | |
| 重启 | 停止再启动 | Profile/JD/Task/History 恢复 | 待执行 | PENDING | |
| 失败恢复 | 请求失败后重试 | 已保存反馈不丢失、不重复提交 | 待执行 | PENDING | |

执行人填写实际日期、ARK_MODEL、每步结果和异常截图编号后再审核。禁止用生成的“成功描述”填充本表。

## 用户人工 Smoke 回报：阻塞失败

记录日期 2026-09-13；实际执行日期及模型配置未提供。以下结果来自用户报告，其余未回报步骤仍待执行。

| 场景 | 输入 | 预期 | 实际结果 | 判定 | 观察 |
|---|---|---|---|---|---|
| 三个 Active JD 聚合 | Python基础/Python技能、SQL实践能力/SQL技能/SQL查询和分析业务数据、数据分析理解/数据分析与指标拆解/解释指标变化 | 同义能力合并，Coverage 2/3 或 3/3 | 三个岗位已加入，但同义词分散，几乎均为 1/3 | FAIL | BC-JD-001 |
| JD Required Level | 必须能够用 SQL 查询和分析业务数据 | 2 · 实践使用 | 0 · 当前证据不足 | FAIL | BC-JD-002 |

当前人工验收为 **FAIL（阻塞）**。代码修复与离线回归不得覆盖此失败记录；人工复测后另追加结果。

### 修复后状态（离线，不替代人工）

BC-JD-001 / BC-JD-002 已完成代码修复；294 项离线测试通过，其中 19 项专门回归这两个问题。未调用真实 API，未改写用户 runtime DB 或历史记录。刷新后的 JD 展示和聚合使用校准投影；如旧要求仍无法明确深度，提示补充岗位原文后重新分析。

请人工复测原三个 JD 的 canonical Coverage 和 SQL 要求文案；当前保留 **FAIL / 待人工复测**，不得据离线结果认定已通过。

## BC-PROFILE-001：本次人工失败及只读核查

用户反馈：已确认简历含 SQL 查询 Demo / SQL 基础，首页却为 SQL Level 0、Required 2、Gap 50%、Score 0.850。判定 **FAIL（阻塞）**。

2026-09-13 按 runtime 唯一最新 smoke 文件只读识别：`smoke_20260913_124526_bbb76d9729e041cba385028527dc9b51.sqlite3`。实际执行模型配置未提供。Draft #1、Profile JSON、确认 Event 的 capabilities 均为空，能力表和 Resume Evidence 均零条；最新快照 State=[]。不存在已保存的 SQL Level 0 行，而是规划对缺失 SQL 的默认值。

根因是有明确技能时仍允许确认空能力列表；缺少原始模型回复/编辑轨迹，初始漏提取与确认前清空无法区分。未发现写入事务部分失败或 SQL 别名错配证据。

已加强 Prompt 与空能力校验、保留 User raw_names；新增 10 项离线测试，总 311 项通过。未改动 Smoke 数据、Evaluation 历史 Run 或等级。原 FAIL 保留；人工需重新解析并检查草稿 SQL/Evidence，再确认并复测。尚未执行真实模型复测，不宣称已恢复现有库。

## 2026-09-14：BC-PROFILE-002 / BC-TASK-001

本次实际执行日期和模型配置未由用户提供。用户回报与只读核查来自唯一 Smoke 文件 `smoke_20260913_124526_bbb76d9729e041cba385028527dc9b51.sqlite3`。

| Bad Case | Expected | Actual | Root Cause | Fix | Retest |
|---|---|---|---|---|---|
| BC-PROFILE-002 | 显式 Python 基础进入 Programming，漏项须拒绝 | Confirmed Draft #4 和正式能力表仅 SQL=2、Data Analysis=1，Programming 缺失 | 旧校验仅拒绝全空 capabilities，未检查非空列表的缺项 | 显式关键词 canonical 集合差检查；不猜等级或静默补写 | pending |
| BC-TASK-001 | 无反馈时不引用反馈；reason 使用中文阶段名称 | 反馈事件 0 条，任务写“根据最新反馈”并泄露内部 enum | Prompt 无条件反馈要求、缺少归因校验、UI 直接展示 reason | 条件 Prompt、无反馈归因拒绝、统一中文映射 | pending |

人工状态仍为 **FAIL / 待复测**，不覆盖失败历史。两项共新增 15 项离线测试，全量 326 项通过（保留原 311 项）；Fake LLM 与临时 SQLite，无真实 API。仅 reason 的事实归因及文案被修复，未调任务内容设计或 Priority Formula；当前 Smoke 数据未修改。

## BC-PROFILE-003：漏项已检测，但缺少人工恢复入口

记录日期：2026-09-14。用户报告连续两次分析均遗漏 Programming，completeness 报错后只能重试模型。实际模型配置与执行日期未额外提供。

- Expected：保留分析结果为 incomplete Draft，用户手动添加/不纳入，再校验并确认。
- Actual：检测有效，但无可修复草稿和恢复入口，人工验收 **FAIL（Release-blocking UX）**。
- Root Cause：原链路只有 reject path，没有 recovery path。
- Fix：现有 Draft JSON 暂存缺项详情；UI 提供候选原文、未预选的 Level 及添加/不纳入按钮；每次操作重验；Confirm 服务独立重验。用户证据明确标识，不自动猜等级，不改变当前 Smoke 数据。
- Retest：pending（人工）。新增 16 项离线回归，包括 Streamlit AppTest 的添加和忽略操作。离线通过不替代人工 Smoke；所有既有失败记录保留。

BC-PROFILE-003 最终离线验证：342 项全部通过（原 326 项回归 + 新增 16 项），git diff --check 通过。人工 Retest 仍为 pending。

### BC-PROFILE-003 再次复测：保存/确认触发 immutable-field error

用户观察：Recovery UI appeared, but persistence failed because protected Draft metadata was sent through the generic Draft update path；界面已显示 Programming=1，但报“包含不可修改的 Draft 字段”。人工状态仍为 FAIL，Retest=pending。

只读事实：最新 Draft #5 内 Programming=1 及用户确认 Resume Evidence 已持久化，validation_status=valid、missing_capabilities=[]、status=draft。失败在后续普通保存/确认，并非专用 Add 的数据库写入。

触发字段为 validation_status、missing_capabilities、ignored_missing_capabilities：普通表单复制整个 draft_json 带入内部字段。已将 payload 限定为八个可编辑 Profile 字段，保持普通更新保护不变；恢复 API、服务端重新校验、重复操作保护不变。

新增六项离线测试覆盖真实读库及恢复后完整 UI 保存/确认路径。当前 Smoke 数据、原失败记录均未更改，无真实 API 调用；等待人工复测，不把离线结果写成 Smoke PASS。
