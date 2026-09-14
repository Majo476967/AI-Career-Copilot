"""Active-JD facts, deterministic order, one capability contribution per JD."""
from core.capabilities import normalize_capability, normalize_jd_requirement
from core.errors import BusinessError
from core.gap_engine import validate_level

IMPORTANCE_VALUES = {"must_have": 1.0, "important": 0.7, "bonus": 0.3}


def invalid(message):
    raise BusinessError("invalid_input", message)


def capability_name(value):
    try:
        return normalize_capability(value)
    except (ValueError, TypeError):
        invalid("Capability Name 必须是非空文本。")


def aggregate_requirements(jds):
    if not isinstance(jds, list):
        invalid("JD 输入必须为数组。")
    active, ids = [], set()
    for jd in jds:
        if not isinstance(jd, dict) or jd.get("status") not in ("active", "archived"):
            invalid("JD 必须有合法的 active / archived 状态。")
        if jd["status"] == "archived":
            continue
        jd_id = jd.get("id")
        if type(jd_id) is not int or jd_id < 1 or jd_id in ids:
            invalid("Active JD 必须具有唯一的正整数 ID。")
        ids.add(jd_id)
        active.append(jd)
    merged, empty_ids = {}, []
    for jd in sorted(active, key=lambda item: item["id"]):
        analysis = jd.get("jd_analysis_json")
        if not isinstance(analysis, dict) or not isinstance(analysis.get("capabilities"), list):
            invalid("JD 缺少结构化 capabilities 数组，请重新分析该岗位。")
        per_jd = {}
        for item in analysis["capabilities"]:
            if not isinstance(item, dict):
                invalid("JD Capability 必须是对象。")
            name = capability_name(item.get("name"))
            label = item.get("importance")
            if not isinstance(label, str) or label not in IMPORTANCE_VALUES:
                invalid("JD importance 必须为 must_have / important / bonus。")
            required = validate_level(item.get("required_level"))
            evidence = item.get("evidence")
            if not isinstance(evidence, str) or not evidence.strip():
                invalid("JD Requirement 缺少原文 Evidence。")
            projected = normalize_jd_requirement(item)
            required = projected["required_level"]
            row = per_jd.setdefault(name, {"importance": label, "level": required, "evidence": set(), "raw_names": set(), "unknown": False})
            row["importance"] = max((row["importance"], label), key=IMPORTANCE_VALUES.get)
            row["level"] = max(row["level"], required)
            row["evidence"].add(evidence)
            row["raw_names"].update(projected["raw_names"])
            row["unknown"] = row["unknown"] or required == 0
        if not per_jd:
            empty_ids.append(jd["id"])
        for name, item in per_jd.items():
            row = merged.setdefault(name, {"capability_name": name, "active_jd_count": 0,
                "total_active_jd_count": len(active), "jd_ids": [], "importance_values": [],
                "importance_labels": [], "required_levels": [], "evidence_by_jd": {}, "raw_names_by_jd": {}, "unknown_jd_ids": [], "requirement_level_unknown": False})
            row["jd_ids"].append(jd["id"])
            row["raw_names_by_jd"][str(jd["id"])] = sorted(item["raw_names"])
            if item["unknown"]:
                row["unknown_jd_ids"].append(jd["id"])
                row["requirement_level_unknown"] = True
            row["active_jd_count"] += 1
            row["importance_values"].append(IMPORTANCE_VALUES[item["importance"]])
            row["importance_labels"].append(item["importance"])
            row["required_levels"].append(item["level"])
            row["evidence_by_jd"][str(jd["id"])] = sorted(item["evidence"])
    status = "no_active_jd" if not active else ("ok" if merged else "no_valid_capabilities")
    return {"status": status, "total_active_jd_count": len(active), "empty_jd_ids": empty_ids,
            "requirements": [merged[name] for name in sorted(merged)]}
