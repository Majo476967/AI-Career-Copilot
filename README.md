# AI Career Copilot V1.0

面向同时准备多个目标岗位、每天准备时间有限的求职者。系统将已确认能力与 Active JD 要求结合，持续回答“现在优先补哪个 Gap，下一项具体做什么”。价值在于可追溯的状态和反馈闭环；不声称底层模型比 ChatGPT 更聪明。

## 产品流程

Resume → Profile Draft → 用户确认 → 多 JD → Gap / Priority → 一个任务 → Feedback → Memory / Replanning。

- PDF / DOCX 简历先解析为待确认草稿，避免模型误读直接污染正式档案。
- 多岗位预览、加入、归档与替换，只有 Active JD 参与准备计算。
- Python 计算 preparation priority：先过滤零 Gap，再结合 Coverage、Importance、Gap Severity 与 Feasibility。
- 豆包设计预算内、有产出和验收标准的下一阶段任务。
- completed / partial / not_completed 反馈持久化；有效任务保留，失效任务 superseded 后重新生成。
- SQLite State、来源 Evidence、append-only Events 和规划快照支持追溯及重启恢复。
- 有界 Memory 与增量 Summary；保守阶段进展基于多次自报完成，不当作客观认证。

## 本地运行

Python 3.10，Windows PowerShell，在仓库目录：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
# 仅在没有 .env 时复制，再填写自己的 ARK_API_KEY
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
streamlit run app.py
```

保留豆包 Ark / OpenAI-compatible SDK。模型、地址、超时、重试由 llm.py 统一读取环境变量。不要提交 .env。

四页：首页、我的档案、目标岗位、进度与历史。默认数据库 runtime/career_copilot.sqlite3；演示可设置 `$env:CAREER_COPILOT_DB = "runtime/smoke.sqlite3"`。刷新页面不自动调用模型。

## Demo

使用 demo/resume.example.docx 和 demo/jd-1.txt～jd-3.txt，均为虚构输入。按 [人工 Demo 清单](docs/MANUAL_SMOKE_TEST.md) 完成解析、确认、岗位、任务、反馈及重启。人工Smoke已完成；首页Priority、Profile Confirmation、反馈前后任务的脱敏截图仍可作为后续展示材料补充，当前未伪造截图。

## 架构与 Memory

[架构图](docs/ARCHITECTURE.md)描述 Deterministic Workflow + Agentic Planning。Python 管理数据、排名与事务，LLM 负责分析和任务设计。Current State 可更新，Events 只追加；Memory 按能力检索最多 5 条相关历史，Summary 与反馈受字符预算限制。V0 的 main.py / agent.py 保留为历史参考；V1.0 入口为 app.py。

## Evaluation

[Rubric](evaluation/RUBRIC.md) 在首轮前冻结；[16 个案例](evaluation/cases.json)覆盖单/多 JD、三种反馈、目标变化和长历史。Direct LLM 与 Copilot 使用相同模型、事实及可用历史，保存每次原始输入输出；自动指标不替代人工质量评分。

```powershell
python -B -m evaluation.evaluator          # 不调用模型
python -B -m unittest discover -s tests -v
python -m pip check
git diff --check
```

每轮结果写入 evaluation/results/ 独立目录，不覆盖历史。[实验结果](evaluation/RESULTS.md)、[Bad Cases](evaluation/BAD_CASES.md)、[验收状态](docs/ACCEPTANCE_CHECKLIST.md)、[人工 Smoke 状态](docs/SMOKE_TEST_RESULT.md)。本版本Evaluation已结束，结论COMPLETE WITH LIMITATIONS；External human A/B evaluation not conducted，作为Owner接受的已知限制与Future Work。

## V1.0 Owner Evaluation Release Decision — 2026-09-14

Evaluation：COMPLETE WITH LIMITATIONS。AC10：PARTIAL — ACCEPTED LIMITATION。External Human A/B Evaluation：NOT CONDUCTED（不是PASS），作为Future Work，不再阻塞本次V1.0 Release；不追加AI Judge或外部人工A/B评测。

Owner接受理由：真实用户Manual Smoke和Bad Case Retest已完成，Automatic Evaluation及两轮独立Blind AI Review已完成；Judge #1偏好Copilot 12 / Baseline 3 / Tie 1，Judge #2为13 / 3 / 0，Preferred Agreement=14/16=87.5%。对于当前个人项目V1.0，继续增加评审的边际收益较低。此为Owner接受限制，不是把AI评审当成人工评审。

自动指标State checks、Duplicate Rate、Coverage两方打平；AI评审中的稳定差异主要来自Task Actionability。Long History未体现Copilot稳定优势，不能宣称所有场景都胜出或统计显著。Copilot Constraint Violation Cases为Judge #1的4例、Judge #2的1例（Baseline分别11、10），口径分歧保留。Priority是准备优先级heuristic，非数学最优或最优ROI；能力升级基于用户自报Evidence，非客观考试认证。

Final Release以RELEASE_CHECKLIST.md的最终技术验证为准；接受Evaluation限制不豁免测试、依赖、安全与文档检查。历史评分和Run保持原样，旧的人工评审PENDING记录仅代表当时状态。

## 局限与范围

V1.0 单用户本地产品；不含登录、云部署、爬虫、职位搜索、OCR、向量库、自定义 LangGraph 编排。等级与 Priority 权重是 heuristic；Level 0 表示未知证据。不能验证真实技能或经济 ROI，不能彻底消除语义重复；API 输出和摘要可能失败。16 个虚构状态案例是下一步决策实验，不是求职结果或长期学习效果证明。

[冻结规格](docs/PROJECT_SPEC.md)是唯一 Source of Truth；[产品决策](docs/PRODUCT_DECISIONS.md)说明取舍。[发布清单](docs/RELEASE_CHECKLIST.md)记录最终技术验收；commit / tag / push另行授权。
