"""Streamlit product entry point; business decisions remain in existing services."""
import logging
import os
import uuid
import streamlit as st
from core.errors import BusinessError
from core.planner import user_visible_reason
from storage.database import DEFAULT_DATABASE_PATH
from ui.adapter import (open_product, run_once, operation_key, profile_changes, level_label, requirement_rows,
                        LEVEL_LABELS, STAGE_LABELS, STATUS_LABELS, TRIGGER_LABELS, evidence_text)


def perform(key, operation, loading, success):
    try:
        with st.spinner(loading):
            result = run_once(st.session_state, key, operation)
    except BusinessError as error:
        st.error(str(error))
        return None
    except Exception:
        logging.exception("UI action failed")
        st.error("操作未完成，请稍后重试；已保存的数据仍保留。")
        return None
    st.session_state["notice"] = success
    return result


def render_evidence(evidence):
    if not evidence:
        st.caption("暂时没有可验证证据，可重新上传更完整的简历并确认。")
    for item in evidence:
        st.write(evidence_text(item["content"]))
        if item.get("evidence_type") == "user_confirmed_resume_evidence":
            st.caption("用户确认的简历证据，不是 LLM 自动认证。")
        source = {"resume": "简历", "task": "任务反馈", "test": "演示记录"}.get(item.get("source"), "其他来源")
        st.caption(f"来源：{source} · 时间：{item.get('created_at') or '未记录'}")


def dashboard(ui):
    st.title("今天，先做最值得的一步")
    st.caption("结合多个目标岗位、当前能力和执行反馈，持续调整准备计划。")
    vm = ui.dashboard()
    top = vm["priority"]["top_priority"]
    a, b, c = st.columns(3)
    a.metric("正在准备的岗位", vm["active_jd_count"])
    b.metric("能力档案", "已确认" if vm["profile_confirmed"] else "待建立")
    c.metric("当前重点", top["capability"] if top else "待分析")
    if vm["empty_message"]:
        st.info(vm["empty_message"])
    for warning in vm["priority"].get("warnings", []):
        st.warning(warning)
    if vm["needs_retry"]:
        st.warning("最近一次任务规划未完成，已保存的档案和反馈仍保留，可稍后重新规划。")
    if top:
        with st.container(border=True):
            st.subheader(f"优先准备：{top['capability']}")
            st.write(vm["explanation"])
            a, b, c, d = st.columns(4)
            a.metric("准备优先分", f"{top['score']:.3f}")
            b.metric("岗位覆盖", f"{top['coverage']:.0%}")
            c.metric("平均重要程度", f"{top['importance']:.0%}")
            d.metric("差距程度", f"{top['gap_severity']:.0%}")
            st.write("下一步：" + STAGE_LABELS.get(top["next_gap_type"], "待确认"))
            if top["evidence_gap"]:
                st.info("当前证据不足：先补充或核实能力证据，这不代表你不会这项能力。")
            st.caption("优先分是准备顺序的启发式参考，不是能力考试分数或经济收益预测。")
        with st.expander("查看全部能力差距与准备顺序"):
            st.dataframe([{"能力": r["capability"], "优先分": round(r["score"], 3),
                "当前等级": level_label(r["current_level"]), "岗位要求": "、".join(map(str, r["required_levels"])),
                "差距程度": f"{r['gap_severity']:.0%}"} for r in vm["priority"]["ranked_priorities"]], hide_index=True)
    task = vm["task"]
    st.subheader("今日任务")
    if task:
        with st.container(border=True):
            st.write(task["task_text"])
            st.caption("预计用时：" + task["estimated_time"])
            st.write("安排理由：" + user_visible_reason(task["reason"]))
            st.write("验收标准")
            for criterion in task["acceptance_criteria_json"]:
                st.write("• " + criterion)
        with st.form(f"feedback_{task['id']}"):
            status = st.radio("完成情况", ["completed", "partial", "not_completed"],
                              format_func=lambda x: STATUS_LABELS[x], horizontal=True)
            feedback = st.text_area("执行反馈", help="已完成可不填；部分完成或未完成请说明已做部分、卡点或原因。")
            submitted = st.form_submit_button("提交反馈", type="primary")
        if submitted:
            result = perform(f"feedback:{task['id']}", lambda: ui.feedback(task["id"], status, feedback),
                             "正在保存反馈并规划下一步…", "反馈已保存，已重新检查能力、优先级和下一任务。")
            if result:
                if result["replanning"].get("needs_retry"):
                    st.session_state["notice"] = "反馈已保存，但新任务生成失败，可稍后重新规划。"
                if result.get("progression"):
                    st.session_state["notice"] += " " + result["progression"]["reason"]
                st.rerun()
    else:
        st.info("尚无可执行的当前任务。完成档案和岗位设置后，可生成当前任务。")
    if st.button("重新规划" if task or vm["needs_retry"] else "生成当前任务", disabled=not bool(top), key="plan"):
        result = perform(f"plan:{vm['revision']}", lambda: ui.planning.recompute("retry" if vm["needs_retry"] else "manual"),
                         "正在检查当前任务并生成下一步…", "规划已更新。")
        if result:
            if result.get("needs_retry"):
                st.session_state["notice"] = "任务生成未完成，可稍后重新规划；已有数据保留。"
            elif result.get("planning_status") == "no_time_budget":
                st.session_state["notice"] = "当前时间预算不足 5 分钟，请在画像草稿中确认可用时间后重新规划。"
            elif result.get("planning_status") == "retained":
                st.session_state["notice"] = "当前任务仍然有效，已保留，无需重复创建。"
            st.rerun()
    if vm["replanning_reason"]:
        with st.expander("最近一次规划为什么这样安排"):
            st.write(user_visible_reason(vm["replanning_reason"]))


def profile_page(ui):
    st.title("我的能力档案")
    vm = ui.profile()
    current = vm["current"]
    st.subheader("正式档案")
    if current is None:
        st.info("先上传简历建立你的求职能力档案。未确认的 AI 草稿不会更新正式档案。")
    else:
        st.success("已确认的能力档案")
        data = current["profile_json"]
        for field, label in [("education", "教育"), ("internships", "实习"), ("projects", "项目"), ("skills", "技能")]:
            st.write(label + "：" + "；".join(data.get(field, [])))
        st.caption(f"专业：{current['major'] or '未填写'} · 求职方向：{current['target_direction'] or '未填写'}")
        st.caption(f"每天可投入：{current['available_hours_per_day']} 小时" if current["available_hours_per_day"] is not None else "每日时间未填写，单任务暂按默认预算安排。")
        for capability in vm["capabilities"]:
            with st.expander(f"{capability['capability_name']} · {capability['level_label']}"):
                render_evidence(capability["evidence"])
        with st.expander("当前简历文本"):
            st.text(current["resume_text"])
    st.subheader("上传 / 更新简历")
    st.caption("支持可编辑 PDF、DOCX，最大 10 MB；扫描 PDF 暂不支持文字识别。重新上传仍需人工确认。")
    nonce = st.session_state.get("resume_nonce", 0)
    upload = st.file_uploader("选择简历", type=["pdf", "docx"], max_upload_size=10, key=f"resume_{nonce}")
    if st.button("解析为画像草稿", disabled=upload is None):
        key = operation_key(f"resume:{nonce}", upload.getvalue())
        result = perform(key, lambda: ui.profiles.create_profile_draft(upload.getvalue(), filename=upload.name),
                         "正在解析简历并生成画像草稿…", "AI 已生成用户画像草稿，请核对后确认。")
        if result:
            st.session_state["draft_selected"] = result["id"]
            st.session_state["resume_nonce"] = nonce + 1
            st.rerun()
    drafts = vm["drafts"]
    if not drafts:
        return
    ids = [d["id"] for d in drafts]
    desired = st.session_state.get("draft_selected")
    draft_id = st.selectbox("待确认草稿", ids, index=ids.index(desired) if desired in ids else 0,
                           format_func=lambda value: f"草稿 #{value}")
    draft = next(d for d in drafts if d["id"] == draft_id)
    data = draft["draft_json"]
    data = ui.profiles.review_profile_draft(draft_id)
    if data["missing_capabilities"]:
        st.subheader("检测到可能遗漏的能力")
        for missing in data["missing_capabilities"]:
            name = missing["canonical_name"]
            st.write(name)
            st.caption("AI 没有把这项能力加入画像。请确认是否需要补充。")
            for snippet in missing["evidence_snippets"]:
                st.write("检测依据：" + snippet)
            with st.form(f"recover_{draft_id}_{name}"):
                chosen_level = st.selectbox("选择能力等级", list(range(5)), index=None,
                    format_func=level_label, placeholder="请自行选择等级", key=f"recover_level_{draft_id}_{name}")
                chosen_evidence = st.selectbox("确认简历证据", missing["evidence_snippets"], key=f"recover_evidence_{draft_id}_{name}")
                st.caption("添加后记录为用户确认的简历证据，不是 LLM 自动认证。3/4 级仍须有项目或实习等经历依据。")
                add = st.form_submit_button("添加到草稿")
                ignore = st.form_submit_button("不纳入")
            if add or ignore:
                action = "add" if add else "ignore"
                result = perform(operation_key(f"recover:{draft_id}:{draft['updated_at']}:{name}", (action, chosen_level, chosen_evidence)),
                    lambda: ui.profiles.resolve_missing_capability(draft_id, name, action, level=chosen_level, evidence_snippet=chosen_evidence),
                    "正在重新校验草稿…", "草稿已更新，正式用户状态未改变。")
                if result:
                    st.rerun()
    st.warning("AI 已生成用户画像草稿，请确认。以下内容尚未进入正式档案。")
    with st.form(f"draft_{draft_id}"):
        fields = {}
        a, b = st.columns(2)
        for field, label in [("education", "教育（每行一条）"), ("internships", "实习（每行一条）"),
                             ("projects", "项目（每行一条）"), ("skills", "技能（每行一条）")]:
            fields[field] = (a if field in {"education", "internships"} else b).text_area(label, "\n".join(data[field]))
        fields["major"] = st.text_input("专业", data.get("major", ""))
        fields["target_direction"] = st.text_input("求职方向", data.get("target_direction", ""))
        hours = data.get("available_hours_per_day")
        fields["available_hours_per_day"] = st.number_input("每天可投入的小时数", 0.0, 24.0,
            value=float(hours) if hours is not None else None, step=0.5, placeholder="留空使用默认任务预算")
        rows = [{"保留": True, "能力": c["name"], "等级": level_label(c["level"])} for c in data["capabilities"]]
        if rows:
            rows = st.data_editor(rows, hide_index=True, num_rows="fixed", key=f"cap_editor_{draft_id}",
                column_config={"等级": st.column_config.SelectboxColumn(options=[level_label(i) for i in range(5)], required=True)})
        st.caption("可修改能力名称、等级或取消保留；证据只读。高等级须有相应来源支持。")
        save = st.form_submit_button("保存草稿修改")
        confirm = st.form_submit_button("确认并更新正式档案", type="primary", disabled=data["validation_status"] != "valid")
    with st.expander("核对草稿证据及原文"):
        st.text(draft["resume_text"])
        for capability in data["capabilities"]:
            st.write(f"{capability['name']} · {level_label(capability['level'])}")
            render_evidence(capability["evidence"])
    if save or confirm:
        def update():
            changes = profile_changes(draft, fields, rows)
            updated = ui.profiles.update_profile_draft(draft_id, changes)
            return ui.profiles.confirm_profile(draft_id) if confirm else updated
        key = f"confirm:{draft_id}" if confirm else operation_key(f"edit:{draft_id}:{draft['updated_at']}", (fields, rows))
        result = perform(key, update, "正在保存画像并检查准备计划…" if confirm else "正在保存草稿…",
                         "正式能力档案已更新，可到首页查看准备计划。" if confirm else "草稿修改已保存，尚未确认。")
        if result:
            st.rerun()
    if st.button("放弃这个草稿", key=f"discard_{draft_id}"):
        if perform(f"discard:{draft_id}", lambda: ui.profiles.discard_profile_draft(draft_id), "正在放弃草稿…", "草稿已放弃，正式档案保留。"):
            st.rerun()


def requirement_table(data):
    st.dataframe(requirement_rows(data), hide_index=True)


def jobs_page(ui):
    st.title("目标岗位")
    active = ui.jobs.list_active_jds()
    labels = {j["id"]: f"{j['company'] or '未填写公司'} · {j['job_title'] or '未填写岗位'}" for j in active}
    st.caption("添加多个目标岗位，发现共同要求。支持粘贴文本或 TXT / PDF / DOCX 文件，最大 5 MB。")
    with st.form("jd_input"):
        replace_id = st.selectbox("新增或替换", [None] + list(labels), format_func=lambda v: "新增目标岗位" if v is None else "替换：" + labels[v])
        mode = st.radio("输入方式", ["粘贴正文", "上传文件"], horizontal=True)
        text = st.text_area("岗位正文", height=160)
        upload = st.file_uploader("岗位文件", type=["txt", "pdf", "docx"], max_upload_size=5)
        analyze = st.form_submit_button("分析并预览", type="primary")
    if analyze:
        if mode == "上传文件" and upload is None:
            st.error("请先选择岗位文件。")
        else:
            value = upload.getvalue() if mode == "上传文件" else text
            preview = perform(operation_key("jd_preview:" + str(replace_id), value),
                lambda: ui.jobs.preview_jd(file=value, filename=upload.name) if mode == "上传文件" else ui.jobs.preview_jd(text),
                "正在分析 JD…", "岗位分析已完成，请核对公司和岗位名称后添加。")
            if preview:
                st.session_state["jd_preview"] = {"prepared": preview, "replace_id": replace_id,
                    "replace_label": labels.get(replace_id), "token": uuid.uuid4().hex}
                st.rerun()
    staged = st.session_state.get("jd_preview")
    if staged:
        data = staged["prepared"]["analysis"]
        st.subheader("待确认岗位预览")
        st.caption("尚未加入当前目标。" if staged["replace_id"] is None else "确认后将替换：" + staged["replace_label"])
        requirement_table(data)
        with st.form("confirm_jd:" + staged["token"]):
            company = st.text_input("公司", data["company"])
            title = st.text_input("岗位名称", data["job_title"])
            confirm = st.form_submit_button("确认加入目标" if staged["replace_id"] is None else "确认替换岗位", type="primary")
        if confirm:
            def commit():
                options = {"prepared": staged["prepared"], "company": company, "job_title": title}
                return ui.jobs.add_jd(**options) if staged["replace_id"] is None else ui.jobs.replace_jd(staged["replace_id"], **options)
            result = perform("jd_commit:" + staged["token"], commit, "正在保存岗位并检查准备计划…",
                "岗位已加入当前目标。" if staged["replace_id"] is None else "旧 JD 已归档，新 JD 已加入当前目标。")
            if result:
                del st.session_state["jd_preview"]
                st.rerun()
        if st.button("放弃岗位预览"):
            del st.session_state["jd_preview"]
            st.rerun()
    st.subheader("正在准备的岗位")
    if not active:
        st.info("添加至少一个目标岗位后，系统才能分析准备优先级。")
    for job in active:
        with st.container(border=True):
            st.subheader(labels[job["id"]])
            st.caption(f"{len(job['jd_analysis_json'].get('capabilities', []))} 项能力要求 · 添加于 {job['created_at']}")
            with st.expander("查看岗位分析"):
                requirement_table(job["jd_analysis_json"])
                st.text(job["jd_text"])
            st.caption("归档后该岗位将退出当前准备计算，但历史记录会保留。替换岗位可使用上方入口。")
            if st.button("归档岗位", key=f"archive_{job['id']}"):
                if perform(f"archive:{job['id']}", lambda: ui.jobs.archive_jd(job["id"]), "正在归档并检查计划…", "岗位已归档，历史记录保留。"):
                    st.rerun()
    with st.expander("多个岗位的共同能力要求", expanded=bool(active)):
        summary = ui.job_summary()
        if summary:
            st.dataframe(summary, hide_index=True)
        else:
            st.caption("添加目标岗位后展示共同要求。")
    with st.expander("已归档岗位"):
        archived = ui.jobs.list_archived_jds()
        if not archived:
            st.caption("暂无归档岗位。")
        for job in archived:
            st.write(f"{job['company']} · {job['job_title']}")
            st.caption("归档时间：" + (job["archived_at"] or "未记录"))


def progress_page(ui):
    st.title("进度与历史")
    history = ui.history()
    st.subheader("任务记录")
    st.caption("展示最近 50 项任务；更早的原始记录仍保留在本地数据库。")
    if not history["tasks"]:
        st.info("还没有任务记录。完成档案和岗位设置后，到首页生成当前任务。")
    for task in history["tasks"]:
        with st.expander(f"{STATUS_LABELS[task['status']]} · {task['capability']} · {task['task_text'][:50]}"):
            st.write(task["task_text"])
            st.write("反馈：" + (task["feedback"] or "未填写"))
            st.caption("创建时间：" + (task["created_at"] or "历史时间未知"))
    st.subheader("能力进展")
    for capability in history["capabilities"]:
        with st.expander(f"{capability['capability_name']} · {capability['level_label']}"):
            render_evidence(capability["evidence"][-3:])
    with st.expander("长期学习摘要"):
        summaries = [c for c in history["capabilities"] if c["summary"]]
        if not summaries:
            st.caption("相关记录积累到阈值后才生成摘要，原始记录始终保留。")
        for capability in summaries:
            st.write(capability["capability_name"])
            st.write(capability["summary"]["summary"])
    st.subheader("规划变化")
    for snapshot in history["snapshots"]:
        result = snapshot["priority_result_json"]
        top = result.get("top_priority") if isinstance(result, dict) else None
        with st.expander(f"{TRIGGER_LABELS.get(snapshot['trigger'], '规划更新')} · {snapshot['created_at']}"):
            st.write("当时优先方向：" + (top["capability"] if top else "暂无明确差距"))
            selected = snapshot["selected_task_json"]
            st.write("当时选择的任务：" + (selected.get("task_text", "未生成任务") if selected else "未生成任务"))
            st.write(user_visible_reason(snapshot["reason"]))


def main():
    st.set_page_config(page_title="AI Career Copilot", page_icon="🧭", layout="wide")
    st.sidebar.title("AI Career Copilot")
    st.sidebar.caption("把求职准备落实到下一步")
    page = st.sidebar.radio("页面", ["首页", "我的档案", "目标岗位", "进度与历史"], key="page")
    st.sidebar.caption("单用户本地使用 · 数据保存在 SQLite")
    if "notice" in st.session_state:
        st.info(st.session_state.pop("notice"))
    try:
        with open_product(os.environ.get("CAREER_COPILOT_DB", str(DEFAULT_DATABASE_PATH))) as ui:
            {"首页": dashboard, "我的档案": profile_page, "目标岗位": jobs_page, "进度与历史": progress_page}[page](ui)
    except BusinessError as error:
        st.error(str(error))
    except Exception:
        logging.exception("Page rendering failed")
        st.error("页面暂时无法加载，请重试；已保存的数据仍保留。")


if __name__ == "__main__":
    main()
