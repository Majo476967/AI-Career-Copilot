"""JD pasted text or local/uploaded file -> plain text only; no URL fetching."""
from core.errors import ParseError
from parsers.common import extract_file, validate_text

MAX_JD_BYTES = 5 * 1024 * 1024


def parse_jd_text(text):
    if isinstance(text, str) and text.strip().lower().startswith(("https://", "http://")):
        raise ParseError("url_not_supported", "不支持 URL 抓取，请直接粘贴 JD 正文。")
    return validate_text(text)


def parse_jd_file(source, *, filename=None):
    return extract_file(source, filename=filename, allowed_formats={".txt", ".pdf", ".docx"},
                        max_bytes=MAX_JD_BYTES)
