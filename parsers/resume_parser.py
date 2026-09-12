"""Resume file -> plain text only."""
from parsers.common import extract_file

MAX_RESUME_BYTES = 10 * 1024 * 1024


def parse_resume(source, *, filename=None):
    return extract_file(source, filename=filename, allowed_formats={".pdf", ".docx"},
                        max_bytes=MAX_RESUME_BYTES)
