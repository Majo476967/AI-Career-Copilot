"""Bounded local file -> text extraction. No LLM and no retained upload files."""
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from docx import Document
from pypdf import PdfReader

from core.errors import ParseError

MIN_TEXT_CHARACTERS = 10
MAX_EXTRACTED_CHARACTERS = 200_000
MAX_DOCX_UNCOMPRESSED_BYTES = 50 * 1024 * 1024


def validate_text(text):
    if not isinstance(text, str):
        raise ParseError("invalid_text", "输入必须为文本。")
    text = text.replace("\x00", "").strip()
    if sum(character.isalnum() for character in text) < MIN_TEXT_CHARACTERS:
        raise ParseError("insufficient_text", "有效文本过少，请提供更完整的文本或可编辑 PDF/DOCX；不支持 OCR。")
    if len(text) > MAX_EXTRACTED_CHARACTERS:
        raise ParseError("text_too_long", "提取文本过长，请缩小文件内容后重试。")
    return text


def extract_file(source, *, filename=None, allowed_formats, max_bytes):
    """Accept a path or uploaded bytes (bytes require filename); never save bytes to disk."""
    path = None
    if isinstance(source, (str, Path)):
        path = Path(source)
        filename = path.name
    elif not isinstance(source, bytes):
        raise ParseError("invalid_file", "请提供文件路径或文件字节内容及文件名。")
    suffix = Path(filename or "").suffix.lower()
    if suffix not in allowed_formats:
        raise ParseError("unsupported_format", "不支持该文件格式，请使用 " + "/".join(sorted(allowed_formats)) + "。")
    try:
        if path is not None:
            if not path.is_file():
                raise ParseError("file_missing", "文件不存在或不是普通文件。")
            if path.stat().st_size > max_bytes:
                raise ParseError("file_too_large", f"文件超过 {max_bytes // (1024 * 1024)} MB 限制。")
            with path.open("rb") as stream:
                data = stream.read(max_bytes + 1)
        else:
            data = source
        if not data:
            raise ParseError("empty_file", "文件为空，请重新选择文件。")
        if len(data) > max_bytes:
            raise ParseError("file_too_large", f"文件超过 {max_bytes // (1024 * 1024)} MB 限制。")
        if suffix == ".txt":
            try:
                text = data.decode("utf-8-sig")
            except UnicodeDecodeError:
                try:
                    text = data.decode("gb18030")
                except UnicodeDecodeError:
                    raise ParseError("text_encoding", "TXT 编码无法识别，请另存为 UTF-8。") from None
        elif suffix == ".pdf":
            if b"%PDF-" not in data[:1024]:
                raise ParseError("file_unreadable", "文件不是有效 PDF，请重新选择文件。")
            reader = PdfReader(BytesIO(data))
            if reader.is_encrypted:
                raise ParseError("encrypted_pdf", "PDF 已加密，请上传未加密的文本 PDF。")
            pieces, total = [], 0
            for page in reader.pages:
                piece = page.extract_text() or ""
                total += len(piece)
                if total > MAX_EXTRACTED_CHARACTERS:
                    raise ParseError("text_too_long", "PDF 文本过长，请缩小内容后重试。")
                pieces.append(piece)
            text = "\n".join(pieces)
        else:
            # DOCX is a ZIP; bound decompression before handing it to python-docx.
            with ZipFile(BytesIO(data)) as archive:
                if sum(item.file_size for item in archive.infolist()) > MAX_DOCX_UNCOMPRESSED_BYTES:
                    raise ParseError("expanded_file_too_large", "DOCX 解压内容过大，请简化文档。")
            document = Document(BytesIO(data))
            pieces = []
            for block in document.iter_inner_content():
                if hasattr(block, "text"):
                    pieces.append(block.text)
                else:
                    for row in block.rows:
                        pieces.append("\t".join(cell.text for cell in row.cells))
            text = "\n".join(pieces)
        return validate_text(text)
    except ParseError:
        raise
    except Exception:
        raise ParseError("file_unreadable", "文件无法解析，可能已损坏或无权读取；请上传有效的文本文件。") from None
