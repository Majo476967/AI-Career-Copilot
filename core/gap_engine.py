"""Deterministic level/evidence gaps. No model calls or state mutation."""
from core.errors import BusinessError

NEXT_GAP_TYPE = {
    0: "evidence_knowledge_verification", 1: "practice", 2: "experience", 3: "depth",
}


def validate_level(value):
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 4:
        raise BusinessError("invalid_input", "能力等级必须是 0～4 的整数。")
    return int(value)


def calculate_gap(current_level, required_levels):
    current = validate_level(current_level)
    if not isinstance(required_levels, list) or not required_levels:
        raise BusinessError("invalid_input", "required_levels 必须是非空等级数组。")
    required = [validate_level(value) for value in required_levels]
    raw = [max(value - current, 0) for value in required]
    positive = any(raw)
    return {"current_level": current, "required_levels": required, "raw_gaps": raw,
            "gap_severity": sum(raw) / (4 * len(raw)), "evidence_gap": current == 0,
            "next_gap_type": NEXT_GAP_TYPE[current] if positive else None}
