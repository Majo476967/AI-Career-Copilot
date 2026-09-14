"""Paired frozen-fact evaluation; no production database or automatic scoring LLM."""
import argparse
import hashlib
import json
import tempfile
import uuid
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

from evaluation.baseline import run_baseline, shared_facts
from core.capabilities import normalize_capability
from core.planner import TaskPlanner
from core.schemas import Capability, Evidence, Event, TargetJD, Task, UserProfile
from services.planning_service import PlanningService
from storage.database import connect_database
from storage.repository import Repository, normalize_task

ROOT = Path(__file__).resolve().parent


def save(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)


def seed(repo, case):
    repo.initialize()
    repo.upsert_profile(UserProfile(**case["user_profile"]))
    for cap in case["capabilities"]:
        row = repo.upsert_capability(Capability(cap["capability_name"], cap["level"]))
        for evidence in cap["evidence"]:
            repo.add_evidence(Evidence(row["id"], "confirmed_profile", evidence, "evaluation_fixture", case["case_id"]))
    for jd in case["active_jds"] + case["archived_jds"]:
        key = repo.add_jd(TargetJD(jd["company"], jd["job_title"], jd["jd_text"], {"capabilities": jd["capabilities"]}))
        if jd["status"] == "archived":
            repo.archive_jd(key)
    for item in case["history"]:
        key = repo.create_task(Task(item["capability"], item["task"], status=item["status"]))
        # Preserve fixture dates, not import wall-clock dates, in the isolated test database.
        repo.connection.execute("UPDATE tasks SET created_at=?, completed_at=? WHERE id=?",
                                (item["created_at"], item["created_at"] if item["status"] == "completed" else None, key))
        event = "TASK_" + item["status"].upper()
        repo.append_event(Event(event, "task", str(key), {"capability": item["capability"],
                          "task_text": item["task"], "feedback": item["feedback"],
                          "fixture_created_at": item["created_at"]}))


def metrics(case, raw, api_error=None):
    if api_error:
        return {"api_error": True, "structured": None}
    try:
        data = json.loads(raw)
        if not isinstance(data, dict) or not all(isinstance(data.get(k), str) and data[k].strip()
                for k in ("capability", "task", "reason", "estimated_time")):
            raise ValueError()
        if not isinstance(data.get("acceptance_criteria"), list) or not data["acceptance_criteria"]:
            raise ValueError()
    except (ValueError, TypeError):
        return {"api_error": False, "structured": False}
    cap = normalize_capability(data["capability"])
    requirements = [r for jd in case["active_jds"] for r in jd["capabilities"]
                    if normalize_capability(r["name"]) == cap]
    covered = sum(any(normalize_capability(r["name"]) == cap for r in jd["capabilities"])
                  for jd in case["active_jds"])
    level = next((c["level"] for c in case["capabilities"] if normalize_capability(c["capability_name"]) == cap), 0)
    completed = [h for h in case["history"] if h["status"] == "completed"]
    duplicate = any(normalize_task(h["task"]) == normalize_task(data["task"]) for h in completed)
    checks = {"active_capability": bool(requirements),
              "positive_gap": any(r["required_level"] > level for r in requirements)}
    if completed:
        checks["avoids_completed_duplicate"] = not duplicate
    anchors = case["expected_facts"].get("feedback_anchors", [])
    output_text = json.dumps(data, ensure_ascii=False).casefold()
    return {"api_error": False, "structured": True, "state_checks": checks,
            "completed_duplicate": duplicate,
            "active_jd_coverage": covered / len(case["active_jds"]) if case["active_jds"] else None,
            "feedback_anchor_proxy": any(a.casefold() in output_text for a in anchors) if anchors else None}


def summarize(records):
    output = {}
    for arm in ("baseline", "copilot"):
        selected = [r for r in records if r["arm"] == arm]
        valid = [r["metrics"] for r in selected if r["metrics"].get("structured")]
        checks = [v for m in valid for v in m["state_checks"].values()]
        def mean(values):
            values = [v for v in values if v is not None]
            return sum(values) / len(values) if values else None
        output[arm] = {"n": len(selected), "api_errors": sum(bool(r.get("api_error")) for r in selected),
                       "parseable_n": len(valid), "delivered_n": sum(r["delivered"] for r in selected),
                       "state_check_accuracy": mean(checks), "state_check_n": len(checks),
                       "completed_duplicate_rate": mean([m["completed_duplicate"] for m in valid]),
                       "mean_active_jd_coverage": mean([m["active_jd_coverage"] for m in valid]),
                       "feedback_anchor_proxy": mean([m["feedback_anchor_proxy"] for m in valid]),
                       "human_scores": None}
    return output


def run(cases, request, output_dir, model_metadata):
    directory = Path(output_dir) / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8])
    directory.mkdir(parents=True, exist_ok=False)
    rubric = (ROOT / "RUBRIC.md").read_bytes()
    save(directory / "manifest.json", {"model": model_metadata, "cases": cases,
         "rubric": rubric.decode("utf-8"), "rubric_sha256": hashlib.sha256(rubric).hexdigest(),
         "cases_sha256": hashlib.sha256(json.dumps(cases, ensure_ascii=False, sort_keys=True).encode()).hexdigest(),
         "experiment": "confirmed-fact next-decision snapshot; not end-to-end or human smoke"})
    records = []
    for index, case in enumerate(cases):
        for arm in (("baseline", "copilot") if index % 2 == 0 else ("copilot", "baseline")):
            record = {"case_id": case["case_id"], "scenario_type": case["scenario_type"], "arm": arm,
                      "facts": shared_facts(case), "raw_input": None, "raw_output": None,
                      "api_error": None, "delivered": False}
            def recorded(system, user):
                record["raw_input"] = {"system": system, "user": user}
                record["requested_at"] = datetime.now(timezone.utc).isoformat()
                try:
                    raw = request(system, user)
                    record["raw_output"] = raw
                    return raw
                except Exception as exc:
                    record["api_error"] = {"type": type(exc).__name__, "status_code": getattr(exc, "status_code", None)}
                    raise
            try:
                if arm == "baseline":
                    run_baseline(case, recorded)
                    record["delivered"] = bool(metrics(case, record["raw_output"]).get("structured"))
                else:
                    with tempfile.TemporaryDirectory(prefix="career-eval-") as temp:
                        connection = connect_database(Path(temp) / "case.sqlite3")
                        try:
                            repo = Repository(connection)
                            seed(repo, case)
                            result = PlanningService(repo, enable_tasks=True, planner=TaskPlanner(recorded)).recompute("evaluation")
                            record["product_result"] = result
                            record["delivered"] = bool(result.get("selected_task")) and not result.get("needs_retry")
                        finally:
                            connection.close()
            except Exception as exc:
                record["execution_error"] = type(exc).__name__
            record["metrics"] = metrics(case, record["raw_output"], record["api_error"])
            save(directory / f"{case['case_id']}-{arm}.json", record)
            records.append(record)
            print(case["case_id"], arm, "api_error" if record["api_error"] else "delivered" if record["delivered"] else "failed", flush=True)
    save(directory / "summary.json", summarize(records))
    save(directory / "human_scores.json", [{"case_id": r["case_id"], "arm": r["arm"],
         "actionability": None, "decision_reasonableness": None, "replanning_consistency": None,
         "reviewer": None, "notes": ""} for r in records])
    return directory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Explicitly authorize up to 32 model calls")
    parser.add_argument("--limit", type=int, default=16)
    parser.add_argument("--case-ids", nargs="+", help="Explicit subset for documented retest")
    args = parser.parse_args()
    if not 1 <= args.limit <= 16:
        parser.error("limit must be 1..16")
    cases = json.loads((ROOT / "cases.json").read_text(encoding="utf-8"))[:args.limit]
    if args.case_ids:
        available = {c["case_id"] for c in cases}
        if not set(args.case_ids) <= available:
            parser.error("unknown case ID or excluded by limit")
        cases = [c for c in cases if c["case_id"] in args.case_ids]
    if not args.live:
        print(f"Validated input selection: {len(cases)} cases. Add --live to call the configured model.")
        return
    import llm
    loaded = llm.load_llm_config()
    config = replace(loaded, max_retries=0, timeout=min(loaded.timeout, 60))
    model = llm.get_chat_model(config=config, temperature=0)
    def request(system, user):
        return model.invoke([("system", system), ("user", user)], max_tokens=1500).content
    directory = run(cases, request, ROOT / "results", {"model": config.model, "temperature": 0,
                    "max_tokens": 1500, "timeout": config.timeout, "max_retries": 0})
    print(directory)


if __name__ == "__main__":
    main()
