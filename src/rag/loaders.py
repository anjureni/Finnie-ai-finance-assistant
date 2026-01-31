# src/rag/loaders.py
from pathlib import Path
from typing import List
from pypdf import PdfReader

from src.rag.types import Chunk
from typing import Union



def load_documents(folder: Union[str, Path]) -> List[dict]:
    base = Path(folder)


def load_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")

def load_pdf_file(path: Path) -> str:
    reader = PdfReader(str(path))
    pages = []
    for p in reader.pages:
        try:
            pages.append(p.extract_text() or "")
        except Exception:
            pages.append("")
    return "\n".join(pages)

def load_documents(folder: str) -> List[dict]:
    """
    Returns list of {"source": ..., "text": ..., "title": ...}
    """
    base = Path(folder)
    docs = []
    for p in base.rglob("*"):
        if p.is_dir():
            continue
        ext = p.suffix.lower()
        if ext in [".txt", ".md"]:
            text = load_text_file(p)
        elif ext in [".pdf"]:
            text = load_pdf_file(p)
        else:
            continue

        docs.append({
            "source": p.name,
            "title": p.stem,
            "text": text,
        })
    return docs
