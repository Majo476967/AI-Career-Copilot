"""Preparation priority heuristic, not economic ROI. Pure deterministic Python."""
from fractions import Fraction
from core.errors import BusinessError
from core.gap_engine import calculate_gap, validate_level
from core.requirement_aggregation import aggregate_requirements, capability_name

FEASIBILITY = {"evidence_knowledge_verification": 1.0, "practice": 0.9,
               "experience": 0.6, "depth": 0.4}
WEIGHTS = {"coverage": 0.35, "importance": 0.25, "gap_severity": 0.30, "feasibility": 0.10}
TIE_BREAK = ["score desc", "gap_severity desc", "coverage desc", "importance desc", "capability asc"]
STATUS_REASON = {"ok": "按多岗位覆盖下的准备优先级排序。",
    "no_active_jd": "暂无 Active JD，请先添加目标岗位。",
    "no_valid_capabilities": "Active JD 尚无有效能力条目，请补充或重新分析。",
    "no_positive_gap": "暂无明确正向 Gap，不强行推荐能力。",
    "no_confirmed_profile": "尚无 Confirmed Profile，请先确认用户画像。"}


def empty_result(status, reason=None):
    return {"status": status, "requirements": [], "gaps": [], "ranked_priorities": [],
            "top_priority": None, "reason": reason or STATUS_REASON.get(status, "输入数据不合法。")}


def user_levels(capabilities):
    if not isinstance(capabilities, list):
        raise BusinessError("invalid_input", "用户能力输入必须为数组。")
    levels = {}
    for item in capabilities:
        if not isinstance(item, dict):
            raise BusinessError("invalid_input", "用户能力必须是对象。")
        name = capability_name(item.get("capability_name"))
        level = validate_level(item.get("level"))
        if name in levels and levels[name] != level:
            raise BusinessError("invalid_input", "归一化后的用户能力等级存在冲突，请先确认。")
        levels[name] = level
    return levels


def calculate_priorities(jds, capabilities):
    """Return a structured result, including invalid_input; never change the arguments."""
    try:
        levels = user_levels(capabilities)
        aggregation = aggregate_requirements(jds)
        result = empty_result(aggregation["status"])
        result.update(aggregation)
        if aggregation["status"] != "ok":
            return result
        ranked = []
        for requirement in aggregation["requirements"]:
            name = requirement["capability_name"]
            gap = calculate_gap(levels.get(name, 0), requirement["required_levels"])
            result["gaps"].append({"capability": name, **gap})
            # Filter BEFORE scoring: zero gap cannot win on coverage/importance.
            if gap["gap_severity"] <= 0:
                continue
            count = requirement["active_jd_count"]
            coverage = Fraction(count, requirement["total_active_jd_count"])
            importance = sum(Fraction(str(v)) for v in requirement["importance_values"]) / count
            severity = Fraction(sum(gap["raw_gaps"]), 4 * count)
            feasibility = Fraction(str(FEASIBILITY[gap["next_gap_type"]]))
            components = {"coverage": coverage, "importance": importance,
                          "gap_severity": severity, "feasibility": feasibility}
            score = sum(Fraction(str(WEIGHTS[key])) * value for key, value in components.items())
            description = ("当前缺少可验证证据，需补充或核实 Evidence。" if gap["evidence_gap"]
                           else f"当前确认等级为 {gap['current_level']}，按等级差计算 Skill Gap。")
            row = {"capability": name, "score": float(score), "coverage": float(coverage),
                "importance": float(importance), "feasibility": float(feasibility), **gap,
                "reason": {"active_jd_count": count,
                    "total_active_jd_count": requirement["total_active_jd_count"],
                    "jd_ids": list(requirement["jd_ids"]),
                    "importance_values": list(requirement["importance_values"]),
                    "current_level": gap["current_level"], "required_levels": list(gap["required_levels"]),
                    "raw_gaps": list(gap["raw_gaps"]), "gap_kind": "Evidence Gap" if gap["evidence_gap"] else "Skill Gap",
                    "state_explanation": description, "evidence_by_jd": requirement["evidence_by_jd"],
                    "feasibility_basis": {"next_gap_type": gap["next_gap_type"],
                        "heuristic": "V1.0 假设，尚未经过实验验证"},
                    "weighted_components": {k: float(Fraction(str(WEIGHTS[k])) * v) for k, v in components.items()},
                    "tie_break": list(TIE_BREAK)},
                "_sort": (-score, -severity, -coverage, -importance, name)}
            ranked.append(row)
        ranked.sort(key=lambda row: row["_sort"])
        for rank, row in enumerate(ranked, 1):
            del row["_sort"]
            row["reason"]["rank"] = rank
            row["reason"]["selection"] = ("正向 Gap 候选中按 Score 及固定同分规则排名第一。" if rank == 1
                                           else "按 Score 及固定同分规则排序。")
        result.update(status="ok" if ranked else "no_positive_gap", ranked_priorities=ranked,
                      top_priority=ranked[0] if ranked else None)
        result["reason"] = STATUS_REASON[result["status"]]
        return result
    except BusinessError as error:
        return empty_result("invalid_input", str(error))
