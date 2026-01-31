# src/rag/chunker.py
from typing import List
from src.rag.types import Chunk

def chunk_text(
    text: str,
    source: str,
    title: str,
    chunk_size: int = 900,
    overlap: int = 150
) -> List[Chunk]:
    """
    Simple character-based chunking.
    """
    text = (text or "").strip()
    if not text:
        return []

    chunks: List[Chunk] = []
    start = 0
    i = 0

    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunk_str = text[start:end].strip()
        if chunk_str:
            chunks.append(
                Chunk(
                    id=f"{source}::chunk{i}",
                    text=chunk_str,
                    source=source,
                    title=title,
                    meta={"start": start, "end": end},
                )
            )
        i += 1
        start = end - overlap if end - overlap > 0 else end

    return chunks
