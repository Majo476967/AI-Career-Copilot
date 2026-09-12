import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from core.errors import ParseError
from parsers.resume_parser import parse_resume, MAX_RESUME_BYTES
from parsers.jd_parser import parse_jd_file, parse_jd_text, MAX_JD_BYTES
from tests.phase2_fixtures import pdf_bytes, docx_bytes, RESUME


class ParserTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        # Any accidental model call in a parser is a test failure.
        blocker = patch("llm.request_analysis", side_effect=AssertionError("Parser must not call LLM"))
        blocker.start()
        self.addCleanup(blocker.stop)

    def file(self, name, data):
        path = Path(self.temp.name) / name
        path.write_bytes(data)
        return path

    def test_resume_pdf(self):
        self.assertIn("SQL practice", parse_resume(self.file("resume.pdf", pdf_bytes())))

    def test_resume_docx(self):
        self.assertIn("虚构学院", parse_resume(self.file("resume.docx", docx_bytes())))

    def test_docx_table_text(self):
        self.assertIn("虚构学院", parse_resume(docx_bytes(table=True), filename="resume.docx"))

    def test_resume_empty_file(self):
        with self.assertRaises(ParseError) as caught:
            parse_resume(self.file("empty.pdf", b""))
        self.assertEqual(caught.exception.code, "empty_file")

    def test_resume_unsupported(self):
        for name in ("image.png", "image.jpg", "resume.txt"):
            with self.subTest(name=name), self.assertRaises(ParseError):
                parse_resume(b"not supported", filename=name)

    def test_resume_oversized(self):
        with self.assertRaises(ParseError) as caught:
            parse_resume(b"x" * (MAX_RESUME_BYTES + 1), filename="resume.pdf")
        self.assertEqual(caught.exception.code, "file_too_large")

    def test_missing_file(self):
        with self.assertRaises(ParseError) as caught:
            parse_resume(Path(self.temp.name) / "missing.pdf")
        self.assertEqual(caught.exception.code, "file_missing")

    def test_pdf_no_text_layer(self):
        with self.assertRaises(ParseError) as caught:
            parse_resume(pdf_bytes(text=""), filename="scan.pdf")
        self.assertEqual(caught.exception.code, "insufficient_text")

    def test_docx_empty(self):
        with self.assertRaises(ParseError):
            parse_resume(docx_bytes(text=""), filename="empty.docx")

    def test_corrupt_files(self):
        for extension in ("pdf", "docx"):
            with self.subTest(extension=extension), self.assertRaises(ParseError) as caught:
                parse_resume(b"corrupt input", filename="broken." + extension)
            self.assertEqual(caught.exception.code, "file_unreadable")

    def test_encrypted_pdf(self):
        with self.assertRaises(ParseError) as caught:
            parse_resume(pdf_bytes(encrypted=True), filename="encrypted.pdf")
        self.assertEqual(caught.exception.code, "encrypted_pdf")

    def test_jd_raw_text(self):
        self.assertEqual(parse_jd_text("  " + RESUME + "  "), RESUME)

    def test_jd_txt_utf8_and_chinese_encoding(self):
        for encoding in ("utf-8-sig", "gb18030"):
            with self.subTest(encoding=encoding):
                self.assertEqual(parse_jd_file(self.file("jd.txt", RESUME.encode(encoding))), RESUME)

    def test_jd_pdf(self):
        self.assertIn("SQL practice", parse_jd_file(pdf_bytes(), filename="jd.pdf"))

    def test_jd_docx(self):
        self.assertEqual(parse_jd_file(docx_bytes(), filename="jd.docx"), RESUME)

    def test_empty_and_too_short_text(self):
        for text in ("", "  ", "abc", "!!!", None):
            with self.subTest(text=text), self.assertRaises(ParseError):
                parse_jd_text(text)

    def test_jd_oversized(self):
        with self.assertRaises(ParseError) as caught:
            parse_jd_file(b"x" * (MAX_JD_BYTES + 1), filename="jd.txt")
        self.assertEqual(caught.exception.code, "file_too_large")

    def test_jd_url_not_fetched(self):
        with self.assertRaises(ParseError) as caught:
            parse_jd_text("https://example.invalid/job")
        self.assertEqual(caught.exception.code, "url_not_supported")
