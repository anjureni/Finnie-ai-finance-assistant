# scripts/build_index.py
from __future__ import annotations
from dotenv import load_dotenv
load_dotenv()


import os
import inspect
from pathlib import Path
from typing import List, Any, Dict

from src.rag.faiss_store import build_faiss_index, save_index
from src.rag.types import Chunk

# ---- Config ----
KB_DIR = Path("data/knowledge_base")
OUT_DIR = "data/index"

# ---- Simple chunker ----
def chunk_text(text: str, chunk_size: int = 900, overlap: int = 150) -> List[str]:
    text = (text or "").strip()
    if not text:
        return []
    chunks: List[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(n, start + chunk_size)
        chunks.append(text[start:end])
        if end >= n:
            break
        start = max(0, end - overlap)
    return chunks

# ---- Embeddings (OpenAI) ----
def embed_texts_openai(texts: List[str], model: str = "text-embedding-3-small") -> List[List[float]]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Export it in terminal or put it in your .env."
        )

    # New OpenAI SDK style
    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    vectors: List[List[float]] = []
    batch_size = 64
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        resp = client.embeddings.create(model=model, input=batch)
        vectors.extend([item.embedding for item in resp.data])
    return vectors

# ---- Robust Chunk creator (auto-matches your Chunk fields) ----
def make_chunk(*, text: str, source: str, chunk_id: int) -> Chunk:
    """
    Creates a Chunk instance by only passing constructor args that exist in your Chunk definition.
    This avoids keyword mismatch errors.
    """
    # Figure out the constructor signature
    try:
        sig = inspect.signature(Chunk)  # works if Chunk is a dataclass or normal class
        params = set(sig.parameters.keys())
    except Exception:
        sig = inspect.signature(Chunk.__init__)
        params = set(sig.parameters.keys()) - {"self"}

    # Candidate fields we can provide
    candidates: Dict[str, Any] = {
        "text": text,
        "content": text,
        "chunk": text,
        "page_content": text,

        "source": source,
        "file": source,
        "filename": source,
        "doc": source,
        "doc_id": source,
        "document": source,

        "chunk_id": chunk_id,
        "id": chunk_id,
        "idx": chunk_id,
        "index": chunk_id,

        "metadata": {"source": source, "chunk_id": chunk_id},
        "meta": {"source": source, "chunk_id": chunk_id},
    }

    kwargs = {k: v for k, v in candidates.items() if k in params}

    # If Chunk has no matching params (unlikely), fall back to minimal construction
    if not kwargs:
        # Try common patterns:
        for keys in (("text",), ("content",), ()):
            try:
                return Chunk(*[text for _ in keys])  # type: ignore
            except Exception:
                pass
        raise RuntimeError("Could not construct Chunk() with available fields. Check src/rag/types.py")

    return Chunk(**kwargs)  # type: ignore

def main():
    print(f"KB folder = {KB_DIR.resolve()}")
    if not KB_DIR.exists():
        raise FileNotFoundError(f"KB folder not found: {KB_DIR}")

    files = sorted(KB_DIR.glob("*.txt"))
    print("Files found =", [f.name for f in files])

    texts: List[str] = []
    chunks: List[Chunk] = []

    for f in files:
        raw = f.read_text(encoding="utf-8", errors="ignore")
        pieces = chunk_text(raw)
        for j, piece in enumerate(pieces):
            texts.append(piece)
            chunks.append(make_chunk(text=piece, source=f.name, chunk_id=j))

    if not texts:
        raise RuntimeError("No text chunks found. KB files may be empty?")

    print(f"Chunks created = {len(texts)}")

    vectors = embed_texts_openai(texts)
    print(f"Vectors created = {len(vectors)} | dim = {len(vectors[0]) if vectors else 'n/a'}")

    index = build_faiss_index(vectors)
    save_index(index=index, chunks=chunks, out_dir=OUT_DIR)

    print(f"✅ Saved FAISS index + chunks to: {OUT_DIR}")

if __name__ == "__main__":
    main()
