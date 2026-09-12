# Phase 5 手工 Smoke Test

此清单由用户手动执行；不会作为自动测试运行。简历/JD 分析和任务生成会调用已配置的豆包模型。
演示文件全部虚构；不要将真实简历、密钥或 runtime 数据提交到 Git。

## 启动

在仓库目录使用 Python 3.10：

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env  # 仅在尚无 .env 时执行；保留已有配置
# 在本地 .env 配置 ARK_API_KEY；不要展示或提交密钥
$env:CAREER_COPILOT_DB = "runtime/smoke.sqlite3"
streamlit run app.py
```

默认数据库是 runtime/career_copilot.sqlite3。上述环境变量让演示使用独立文件，不影响原有用户状态。
关闭程序后如需恢复默认，执行 `Remove-Item Env:CAREER_COPILOT_DB`；不要删除真实数据库。

## 检查流程

1. 首页为空时应提示先建立档案；切换四个页面无报错。
2. 在“我的档案”上传 demo/resume.example.docx，点击“解析为画像草稿”。仅生成草稿，正式档案仍未确认。
3. 核对教育、项目、技能、等级和证据；修改求职方向、每日时间以及必要的草稿内容，再保存修改。刷新页面，草稿仍存在。
4. 点击“确认并更新正式档案”，正式档案出现；证据不足显示中文说明，不显示“能力弱”。
5. 在“目标岗位”分别上传 demo/jd-1.txt、jd-2.txt、jd-3.txt。每次先预览、修正公司/岗位名，再确认加入。
6. 检查三个 Active JD、共同能力要求以及首页准备优先级；预览未确认时不得进入 Active JD。
7. 查看或点击“生成当前任务”；核对任务、理由、用时和验收标准。再次规划若任务仍有效应保留。
8. 提交 partial，先留空：应阻止提交。再填写“JOIN 已完成，但 GROUP BY 还需要练习”，提交并检查新任务及规划原因。
9. “进度与历史”显示旧任务为部分完成，反馈原文仍存在；查看最近证据与规划记录。摘要未达阈值时显示正常空状态。
10. 归档一个岗位，应退出准备计算并出现在归档区。通过上方“替换”入口输入一份不同的虚构 JD，确认后旧岗位归档、新岗位加入。
11. 浏览器刷新、切换页面，不应重复分析或创建任务/事件。
12. 停止并重新运行 `streamlit run app.py`，确认正式档案、岗位、任务和历史仍存在。未确认画像草稿可恢复；岗位预览仅保留在当前会话，重启后可重新预览。
13. 可在手工测试时临时使用无效模型配置验证错误提示：反馈一旦已保存，后续任务生成失败应提示“反馈已保存，但新任务生成失败，可稍后重新规划”。恢复配置后点击重新规划，不重复提交已完成反馈。

## 离线验证

```powershell
python -B -m unittest discover -s tests -v
git diff --check
```

自动测试使用临时 SQLite 和 Fake/Mock LLM，不调用真实 API。Streamlit 展示测试使用内置 AppTest，无需完整浏览器自动化。
