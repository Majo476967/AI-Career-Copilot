"""Persisted draft -> explicit human confirmation -> atomic Current State + event.

Methods raise BusinessError (including ParseError/AnalysisError) with readable text.
No UI or tasks; an optional injected router recomputes deterministic priority.
"""
import hashlib
import math
from core.errors import BusinessError
from core.schemas import Capability, CapabilityLevel, Event, EventType, Evidence, UserProfile
from parsers.resume_parser import parse_resume
from services.common import storage_errors
from storage.repository import encode
from tools.user_analyzer import analyze_resume
from tools.analysis_validation import validate_profile, quote_key


class ProfileService:
    def __init__(self, repository, *, event_router=None):
        self.repo = repository
        self.event_router = event_router

    @storage_errors
    def create_profile_draft(self, source, *, filename=None):
        resume_text = parse_resume(source, filename=filename)
        data = validate_profile(analyze_resume(resume_text), resume_text)
        current = self.repo.get_profile() or {}
        data.update({key: current.get(key, default) for key, default in
                     (("major", ""), ("target_direction", ""), ("available_hours_per_day", None))})
        version = "resume:" + hashlib.sha256(quote_key(resume_text).encode("utf-8")).hexdigest()
        draft_id = self.repo.create_profile_draft(resume_text, version, data)
        return self.get_profile_draft(draft_id)

    @storage_errors
    def get_profile_draft(self, draft_id):
        draft = self.repo.get_profile_draft(draft_id)
        if draft is None:
            raise BusinessError("draft_missing", "Profile Draft 不存在。")
        return draft

    def _editable(self, draft_id):
        draft = self.get_profile_draft(draft_id)
        if draft["status"] != "draft":
            raise BusinessError("draft_closed", "该 Draft 已确认或已丢弃，不能继续修改。")
        return draft

    @staticmethod
    def _validate_edited(data, resume_text):
        cleaned = validate_profile(data, resume_text, human_edited=True)
        for field in ("major", "target_direction"):
            if not isinstance(data.get(field, ""), str):
                raise BusinessError("invalid_profile", f"{field} 必须是文本。")
            cleaned[field] = data.get(field, "").strip()
        hours = data.get("available_hours_per_day")
        if hours is not None and (isinstance(hours, bool) or not isinstance(hours, (float, int))
                                  or not math.isfinite(hours) or not 0 <= hours <= 24):
            raise BusinessError("invalid_hours", "每日可用时间须为 0～24 小时。")
        cleaned["available_hours_per_day"] = hours
        return cleaned

    @storage_errors
    def update_profile_draft(self, draft_id, changes):
        if not isinstance(changes, dict) or set(changes) - {
            "education", "internships", "projects", "skills", "capabilities",
            "major", "target_direction", "available_hours_per_day"}:
            raise BusinessError("invalid_draft_update", "包含不可修改的 Draft 字段。")
        with self.repo.transaction():
            draft = self._editable(draft_id)
            data = self._validate_edited({**draft["draft_json"], **changes}, draft["resume_text"])
            self.repo.update_profile_draft(draft_id, data)
        return self.get_profile_draft(draft_id)

    @storage_errors
    def discard_profile_draft(self, draft_id):
        with self.repo.transaction():
            draft = self.get_profile_draft(draft_id)
            if draft["status"] == "confirmed":
                raise BusinessError("draft_confirmed", "已确认的 Draft 不能丢弃，请上传新简历创建 Draft。")
            if draft["status"] == "draft":
                self.repo.set_profile_draft_status(draft_id, "discarded")
        return self.get_profile_draft(draft_id)

    @storage_errors
    def confirm_profile(self, draft_id):
        """Call only for an explicit user confirmation. A second call is a no-op."""
        with self.repo.transaction():
            draft = self.get_profile_draft(draft_id)
            if draft["status"] == "discarded":
                raise BusinessError("draft_discarded", "该 Draft 已丢弃，无法确认。")
            if draft["status"] == "confirmed":
                return {"draft_id": draft_id, "profile_id": 1, "status": "confirmed"}
            data = self._validate_edited(draft["draft_json"], draft["resume_text"])
            profile = UserProfile(
                education=encode(data["education"]), major=data["major"],
                target_direction=data["target_direction"],
                available_hours_per_day=data["available_hours_per_day"],
                resume_text=draft["resume_text"],
                profile_json={**data, "resume_version": draft["resume_version"], "draft_id": draft_id})
            self.repo.upsert_profile(profile)
            for item in data["capabilities"]:
                capability = self.repo.upsert_capability(Capability(item["name"], CapabilityLevel(item["level"])))
                for evidence in item["evidence"]:
                    self.repo.add_evidence_if_new(Evidence(
                        capability["id"], evidence["evidence_type"], evidence["content"],
                        "resume", draft["resume_version"]))
            self.repo.append_event(Event(EventType.PROFILE_CONFIRMED, "profile", "1", {
                "draft_id": draft_id, "resume_version": draft["resume_version"],
                "confirmed_profile": data, "planning_required": True}))
            self.repo.set_profile_draft_status(draft_id, "confirmed")
            if self.event_router is not None:
                self.event_router.dispatch(EventType.PROFILE_CONFIRMED)
        return {"draft_id": draft_id, "profile_id": 1, "status": "confirmed"}
