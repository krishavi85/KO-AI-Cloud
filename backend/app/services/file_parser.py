from pathlib import Path
from pypdf import PdfReader
from docx import Document as DocxDocument


def parse_txt(path: str) -> str:
    return Path(path).read_text(encoding="utf-8", errors="ignore")


def parse_pdf(path: str) -> str:
    reader = PdfReader(path)
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n".join(pages)


def parse_docx(path: str) -> str:
    doc = DocxDocument(path)
    return "\n".join([p.text for p in doc.paragraphs])


def parse_file(path: str, content_type: str | None = None) -> str:
    suffix = Path(path).suffix.lower()
    if suffix == ".pdf":
        return parse_pdf(path)
    if suffix == ".docx":
        return parse_docx(path)
    if suffix in [".txt", ".md", ".csv", ".json", ".py", ".js", ".jsx", ".ts", ".tsx", ".html", ".css"]:
        return parse_txt(path)
    return parse_txt(path)


def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200) -> list[str]:
    clean = " ".join(text.split())
    chunks = []
    start = 0
    while start < len(clean):
        end = start + chunk_size
        chunk = clean[start:end]
        if chunk.strip():
            chunks.append(chunk)
        start = end - overlap
        if start < 0:
            start = 0
        if start >= len(clean):
            break
    return chunks
