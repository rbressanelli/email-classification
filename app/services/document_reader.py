from pathlib import Path
from pypdf import PdfReader


def read_txt_file(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8", errors="ignore")


def read_pdf_file(path: str | Path) -> str:
    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages).strip()


def read_document(path: str | Path, filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".txt":
        return read_txt_file(path)
    if suffix == ".pdf":
        return read_pdf_file(path)
    raise ValueError("Formato não suportado. Use .txt ou .pdf")
