"""BC-PROFILE-003 retest: recovery persistence through generic save/confirm."""
import sqlite3
import unittest
from core.errors import BusinessError
from tests import test_profile_recovery as recovery_fixtures
from ui.adapter import profile_changes, level_label


def changes_for(item):
    data = item["draft_json"]
    fields = {name: "\n".join(data[name]) for name in ("education", "internships", "projects", "skills")}
    fields.update({name: data.get(name) for name in ("major", "target_direction", "available_hours_per_day")})
    rows = [{"保留": True, "能力": c["name"], "等级": level_label(c["level"])} for c in data["capabilities"]]
    return profile_changes(item, fields, rows)


class RecoveryPayloadTests(unittest.TestCase):
    setUp = recovery_fixtures.ProfileRecoveryTests.setUp
    create = recovery_fixtures.ProfileRecoveryTests.create
    add = recovery_fixtures.ProfileRecoveryTests.add

    def test_generic_payload_contains_only_editable_fields(self):
        item = self.add(self.create())
        item["draft_json"].update(id=9, status="confirmed", analyzer_provenance={"test": True})
        changes = changes_for(item)
        self.assertEqual(set(changes), {"education", "internships", "projects", "skills", "capabilities", "major", "target_direction", "available_hours_per_day"})
        self.assertEqual(changes["capabilities"], item["draft_json"]["capabilities"])

    def test_add_then_generic_save_and_confirm_persists_evidence(self):
        item = self.add(self.create())
        saved = self.service.update_profile_draft(item["id"], changes_for(item))
        self.assertEqual(saved["draft_json"]["validation_status"], "valid")
        self.assertEqual(saved["draft_json"]["missing_capabilities"], [])
        self.service.confirm_profile(item["id"])
        cap = self.repo.get_capability("Programming")
        self.assertEqual(cap["level"], 1)
        self.assertEqual(self.repo.get_evidence(cap["id"])[0]["evidence_type"], "user_confirmed_resume_evidence")
        self.request.assert_called_once()

    def test_ignore_survives_generic_save_and_confirmation(self):
        item = self.create()
        resolved = self.service.resolve_missing_capability(item["id"], "Programming", "ignore")
        saved = self.service.update_profile_draft(item["id"], changes_for(resolved))
        self.assertEqual(saved["draft_json"]["ignored_missing_capabilities"], ["Programming"])
        self.assertEqual(saved["draft_json"]["missing_capabilities"], [])
        self.service.confirm_profile(item["id"])
        self.assertIsNone(self.repo.get_capability("Programming"))

    def test_generic_service_still_rejects_all_internal_fields(self):
        item = self.create()
        for field in ["validation_status", "missing_capabilities", "ignored_missing_capabilities", "id", "status", "resume_version", "analyzer_provenance"]:
            with self.subTest(field=field), self.assertRaises(BusinessError) as caught:
                self.service.update_profile_draft(item["id"], {field: None})
            self.assertEqual(caught.exception.code, "invalid_draft_update")
        self.assertEqual(self.service.get_profile_draft(item["id"]), item)

    def test_duplicate_add_does_not_duplicate_persisted_evidence(self):
        item = self.create(); self.add(item)
        with self.assertRaises(BusinessError): self.add(item)
        # A second connection proves this is persisted state rather than session state.
        import json
        with sqlite3.connect(self.path_for_read()) as connection:
            data = json.loads(connection.execute("SELECT draft_json FROM profile_drafts WHERE id=?", (item["id"],)).fetchone()[0])
        caps = [c for c in data["capabilities"] if c["name"] == "Programming"]
        self.assertEqual(len(caps), 1)
        self.assertEqual(len(caps[0]["evidence"]), 1)

    def path_for_read(self):
        from pathlib import Path
        return str(Path(self.temp.name) / "recovery.sqlite3")


class RecoveryConfirmationUITests(unittest.TestCase):
    setUp = recovery_fixtures.ProfileRecoveryTests.setUp
    create = recovery_fixtures.ProfileRecoveryTests.create
    app = recovery_fixtures.ProfileRecoveryUITests.app

    def test_add_reload_save_then_confirm_from_ui(self):
        item = self.create(); app = self.app()
        next(s for s in app.selectbox if s.label == "选择能力等级").set_value(1)
        next(b for b in app.button if b.label == "添加到草稿").click().run()
        self.assertFalse(app.error)
        app = self.app()  # New AppTest session rereads SQLite.
        data = self.repo.get_profile_draft(item["id"])["draft_json"]
        self.assertIn("Programming", [c["name"] for c in data["capabilities"]])
        next(b for b in app.button if b.label == "保存草稿修改").click().run()
        self.assertFalse(app.exception)
        self.assertFalse(app.error)
        next(b for b in app.button if b.label == "确认并更新正式档案").click().run()
        self.assertFalse(app.exception)
        self.assertFalse(app.error)
        self.assertEqual(self.repo.get_profile_draft(item["id"])["status"], "confirmed")
        self.assertEqual(self.repo.get_capability("Programming")["level"], 1)
        self.request.assert_called_once()
