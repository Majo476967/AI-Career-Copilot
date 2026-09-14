"""Validate model output before any write. Exact excerpts prevent invented source claims.

Quote checks establish provenance, not semantic truth; human confirmation still matters.
"""
import json
import re
import unicodedata
from core.capabilities import normalize_capability, normalize_alias, normalize_jd_requirement, explicit_resume_capabilities, missing_resume_capabilities
from core.errors import AnalysisError

IMPORTANCE = {"bonus": 0, "important": 1, "must_have": 2}
EVIDENCE_TYPES = {"resume_text", "education", "internship", "project", "skill"}


def fail(message):
    raise AnalysisError("invalid_analysis", message)


def decode_json(content):
    if not isinstance(content, str):
        fail("模型未返回 JSON 文本。")
    text = content.strip()
    if text.startswith("```json") and text.endswith("```"):
        text = text[7:-3].strip()
    def reject_constant(value):
        raise ValueError(value)
    try:
        data = json.loads(text, parse_constant=reject_constant)
    except (ValueError, TypeError):
        raise AnalysisError("invalid_json", "模型返回的内容不是合法 JSON，请重试。") from None
    if not isinstance(data, dict):
        fail("模型输出必须是 JSON 对象。")
    return data


def text(value, name, *, empty=False):
    if not isinstance(value, str) or (not empty and not value.strip()):
        fail(f"{name} 必须是{'可为空的' if empty else '非空'}文本。")
    return value.strip()


def array(value, name):
    if not isinstance(value, list):
        fail(f"{name} 必须是数组。")
    return value


def level(value):
    if type(value) is not int or not 0 <= value <= 4:
        fail("能力等级必须是 0～4 的整数；Level 0 表示 unknown evidence。")
    return value


def quote_key(value):
    return "".join(unicodedata.normalize("NFKC", value).split())


def require_quote(value, source):
    if quote_key(value) not in quote_key(source):
        fail("分析包含原文中不存在的经历或证据，请核对原文后重试。")


def validate_profile(data, resume_text, *, human_edited=False, allow_incomplete=False):
    if not isinstance(data, dict):
        fail("Profile Draft 必须是对象。")
    result = {}
    for field in ("education", "internships", "projects", "skills"):
        result[field] = [text(v, field) for v in array(data.get(field), field)]
        if not human_edited:
            for value in result[field]:
                require_quote(value, resume_text)
    merged = {}
    for raw in array(data.get("capabilities"), "capabilities"):
        if not isinstance(raw, dict):
            fail("Capability 必须是对象。")
        name = normalize_capability(text(raw.get("name"), "name"))
        value = level(raw.get("level"))
        evidence = []
        for item in array(raw.get("evidence"), "evidence"):
            if not isinstance(item, dict) or item.get("source") != "resume":
                fail("简历 Evidence 的 source 必须为 resume。")
            kind = text(item.get("evidence_type"), "evidence_type")
            if kind not in EVIDENCE_TYPES and not (human_edited and kind == "user_confirmed_resume_evidence"):
                fail("无效的简历 evidence_type。")
            content = text(item.get("content"), "evidence.content")
            require_quote(content, resume_text)
            normalized = {"evidence_type": kind, "content": content, "source": "resume"}
            if normalized not in evidence:
                evidence.append(normalized)
        if value > 0 and not evidence:
            fail("缺少可验证 Evidence 时等级只能为 0，不能推高能力等级。")
        if value > 1 and all(normalize_alias(e["content"]) == name for e in evidence):
            fail("仅出现能力关键词不足以支持实践及以上等级。")
        if value >= 3 and not any(e["evidence_type"] in {"project", "internship"} or (human_edited and e["evidence_type"] == "user_confirmed_resume_evidence" and re.search(r"项目|实习|业务|project|internship", e["content"], re.I)) for e in evidence):
            fail("Experience / Depth 必须有明确的项目或实习证据。")
        if name not in merged:
            merged[name] = {"name": name, "raw_names": list(dict.fromkeys(raw.get("raw_names", [raw["name"]]))), "level": value, "evidence": evidence}
        else:
            merged[name]["raw_names"] = list(dict.fromkeys(merged[name]["raw_names"] + raw.get("raw_names", [raw["name"]])))
            merged[name]["level"] = max(merged[name]["level"], value)
            for item in evidence:
                if item not in merged[name]["evidence"]:
                    merged[name]["evidence"].append(item)
    ignored = []
    if human_edited:
        ignored = sorted({normalize_capability(text(name, "ignored capability"))
                          for name in array(data.get("ignored_missing_capabilities", []), "ignored_missing_capabilities")})
    missing = missing_resume_capabilities(resume_text, merged, ignored)
    if missing and not allow_incomplete:
        detail = "能力草稿为空；" if not merged else ""
        raise AnalysisError("incomplete_profile", detail + "简历存在明确能力，但草稿缺少 canonical capabilities：" +
            "、".join(item["canonical_name"] for item in missing) + "。请在草稿中补充或明确不纳入；系统不会猜测 Level。")
    result.update(validation_status="incomplete" if missing else "valid", missing_capabilities=missing,
                  ignored_missing_capabilities=ignored)
    result["capabilities"] = list(merged.values())
    return result


def validate_jd(data, jd_text):
    if not isinstance(data, dict):
        fail("JD Analysis 必须是对象。")
    result = {field: text(data.get(field), field, empty=True) for field in ("company", "job_title")}
    for value in result.values():
        if value and value.casefold() != "unknown":
            require_quote(value, jd_text)
    merged = {}
    for raw in array(data.get("capabilities"), "capabilities"):
        if not isinstance(raw, dict):
            fail("JD Capability 必须是对象。")
        name = normalize_capability(text(raw.get("name"), "name"))
        category = text(raw.get("category"), "category", empty=True)
        importance = text(raw.get("importance"), "importance")
        if importance not in IMPORTANCE:
            fail("importance 只能是 must_have、important 或 bonus。")
        required = raw.get("required_level")
        if type(required) is not int or not 0 <= required <= 4:
            fail("岗位要求等级必须是 0～4 整数；0 表示岗位未明确等级。")
        evidence = text(raw.get("evidence"), "evidence")
        # A merged capability can cite several separate source excerpts.
        for excerpt in evidence.splitlines():
            if excerpt.strip():
                require_quote(excerpt, jd_text)
        calibrated = normalize_jd_requirement({**raw, "evidence": evidence})
        required = calibrated["required_level"]
        if name not in merged:
            merged[name] = {"raw_names": calibrated["raw_names"], "name": name, "category": category, "importance": importance,
                            "required_level": required, "evidence": evidence}
        else:
            old = merged[name]
            old["raw_names"] = list(dict.fromkeys(old["raw_names"] + calibrated["raw_names"]))
            old["required_level"] = max(old["required_level"], required)
            old["importance"] = max((old["importance"], importance), key=IMPORTANCE.get)
            # Keep separate source excerpts verifiable on subsequent validation.
            if evidence not in old["evidence"].split("\n"):
                old["evidence"] += "\n" + evidence
    if not merged:
        fail("未识别到有效岗位能力要求，请提供完整 JD。")
    result["capabilities"] = list(merged.values())
    return result
