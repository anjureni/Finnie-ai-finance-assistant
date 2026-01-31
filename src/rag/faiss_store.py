# src/rag/faiss_store.py
from __future__ import annotations
from pathlib import Path
import json
from typing import List, Tuple
import numpy as np
import faiss

from src.rag.types import Chunk

def _to_np(vectors: list[list[float]]) -> np.ndarray:
    arr = np.array(vectors, dtype="float32")
    return arr

def build_faiss_index(vectors: list[list[float]]) -> faiss.Index:
    mat = _to_np(vectors)
    dim = mat.shape[1]
    index = faiss.IndexFlatIP(dim)   # cosine-like if normalized
    faiss.normalize_L2(mat)
    index.add(mat)
    return index

def save_index(index: faiss.Index, chunks: List[Chunk], out_dir: str):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(out / "faiss.index"))

    meta = []
    for c in chunks:
        meta.append({
            "id": c.id,
            "text": c.text,
            "source": c.source,
            "title": c.title,
            "meta": c.meta,
        })
    (out / "chunks.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

def load_index(out_dir: str) -> Tuple[faiss.Index, List[Chunk]]:
    out = Path(out_dir)
    index = faiss.read_index(str(out / "faiss.index"))
    meta = json.loads((out / "chunks.json").read_text(encoding="utf-8"))

    chunks = []
    for m in meta:
        chunks.append(Chunk(
            id=m["id"],
            text=m["text"],
            source=m["source"],
            title=m.get("title"),
            meta=m.get("meta"),
        ))
    return index, chunks

def search(index: faiss.Index, chunks: List[Chunk], query_vec: list[float], top_k: int = 5):
    q = np.array([query_vec], dtype="float32")
    faiss.normalize_L2(q)
    scores, idxs = index.search(q, top_k)
    results = []
    for score, i in zip(scores[0], idxs[0]):
        if i == -1:
            continue
        results.append((float(score), chunks[int(i)]))
    return results
