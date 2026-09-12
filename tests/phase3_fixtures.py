"""Small synthetic requirement records; no personal information or network access."""

def requirement(name="SQL", level=2, importance="must_have", evidence="Synthetic SQL requirement"):
    return {"name": name, "required_level": level, "importance": importance, "evidence": evidence}


def jd(jd_id=1, requirements=None, status="active"):
    return {"id": jd_id, "status": status,
            "jd_analysis_json": {"capabilities": [requirement()] if requirements is None else requirements}}


def capability(name="SQL", level=1):
    return {"capability_name": name, "level": level}
