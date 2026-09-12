"""Multi-JD CRUD and factual capability aggregation, never priority or planning."""
import unicodedata
from core.errors import BusinessError
from core.schemas import Event, EventType, TargetJD
from parsers.jd_parser import parse_jd_file, parse_jd_text
from services.common import storage_errors
from tools.jd_analyzer import analyze_jd_text


def input_key(text):
    return " ".join(unicodedata.normalize("NFKC", text).split()).casefold()


class JDService:
    def __init__(self, repository):
        self.repo = repository

    @staticmethod
    def _input(text, file, filename):
        if (text is None) == (file is None):
            raise BusinessError("jd_input", "请提供 JD 正文或文件，且只选择一种输入。")
        return parse_jd_file(file, filename=filename) if file is not None else parse_jd_text(text)

    def _check_duplicate(self, text):
        for existing in self.repo.list_jds():
            if input_key(existing["jd_text"]) == input_key(text):
                raise BusinessError("duplicate_jd", "相同 JD 已存在（可能已归档），请查看已有岗位记录。")

    @staticmethod
    def _analyze(text, company, job_title):
        data = analyze_jd_text(text)
        for field, value in (("company", company), ("job_title", job_title)):
            if value is not None:
                if not isinstance(value, str):
                    raise BusinessError("invalid_jd_label", "公司和岗位名称必须是文本。")
                data[field] = value.strip()
        return data

    @storage_errors
    def add_jd(self, text=None, *, file=None, filename=None, company=None, job_title=None):
        text = self._input(text, file, filename)
        self._check_duplicate(text)
        data = self._analyze(text, company, job_title)
        with self.repo.transaction():
            self._check_duplicate(text)
            jd_id = self.repo.add_jd(TargetJD(data["company"], data["job_title"], text, data))
            self.repo.append_event(Event(EventType.JD_ADDED, "jd", str(jd_id), {"planning_required": True}))
        return self.get_jd(jd_id)

    @storage_errors
    def get_jd(self, jd_id):
        jd = self.repo.get_jd(jd_id)
        if jd is None:
            raise BusinessError("jd_missing", "目标 JD 不存在。")
        return jd

    @storage_errors
    def list_active_jds(self):
        return self.repo.get_active_jds()

    @storage_errors
    def list_archived_jds(self):
        return self.repo.list_jds("archived")

    @storage_errors
    def archive_jd(self, jd_id):
        with self.repo.transaction():
            old = self.get_jd(jd_id)
            if old["status"] == "active":
                self.repo.archive_jd(jd_id)
                self.repo.append_event(Event(EventType.JD_ARCHIVED, "jd", str(jd_id), {"planning_required": True}))
            # Already archived: idempotent success, no duplicate event.
        return self.get_jd(jd_id)

    @storage_errors
    def replace_jd(self, old_jd_id, text=None, *, file=None, filename=None, company=None, job_title=None):
        old = self.get_jd(old_jd_id)
        if old["status"] != "active":
            raise BusinessError("jd_not_active", "只能替换 Active JD；该岗位已经归档。")
        text = self._input(text, file, filename)
        self._check_duplicate(text)
        data = self._analyze(text, company, job_title)
        with self.repo.transaction():
            if self.get_jd(old_jd_id)["status"] != "active":
                raise BusinessError("jd_not_active", "该岗位状态已改变，请重新读取。")
            self._check_duplicate(text)
            self.repo.archive_jd(old_jd_id)
            new_id = self.repo.add_jd(TargetJD(data["company"], data["job_title"], text, data))
            self.repo.append_event(Event(EventType.JD_REPLACED, "jd", str(new_id), {
                "old_jd_id": old_jd_id, "new_jd_id": new_id, "planning_required": True}))
        return self.get_jd(new_id)

    @storage_errors
    def get_active_jd_capability_summary(self):
        summary = {}
        for jd in self.repo.get_active_jds():
            seen = set()
            for item in jd["jd_analysis_json"].get("capabilities", []):
                name = item["name"]
                if name in seen:
                    continue
                seen.add(name)
                row = summary.setdefault(name, {"jd_ids": [], "count": 0, "importance": [], "required_levels": []})
                row["jd_ids"].append(jd["id"])
                row["count"] += 1
                row["importance"].append(item["importance"])
                row["required_levels"].append(item["required_level"])
        return summary
