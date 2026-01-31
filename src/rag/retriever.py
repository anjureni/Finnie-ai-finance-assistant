# src/rag/retriever.py
from __future__ import annotations

from typing import Any, Dict, List
import os

import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

from src.rag.faiss_store import load_index
from src.rag.types import Chunk

load_dotenv()

# Load FAISS index + chunks once
_INDEX, _CHUNKS = load_index("data/index")


def _chunk_text(ch: Chunk) -> str:
    return getattr(ch, "text", None) or getattr(ch, "content", None) or str(ch)


def _chunk_source(ch: Chunk) -> str:
    return getattr(ch, "source", None) or getattr(ch, "filename", None) or "knowledge_base"


class Retriever:
    """
    Returns structured hits for citations:
      [{"id": 1, "source": "...", "text": "...", "score": ...}, ...]
    """

    def __init__(
        self,
        index_dir: str = "data/index",  # kept for compatibility
        model: str = "text-embedding-3-small",
        **kwargs,
    ):
        self.index_dir = index_dir
        self.model = model

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        self.client = OpenAI(api_key=api_key)

    def retrieve(self, query: str, top_k: int = 3, **kwargs) -> List[Dict[str, Any]]:
        emb = self.client.embeddings.create(model=self.model, input=[query]).data[0].embedding
        qvec = np.array([emb], dtype="float32")

        D, I = _INDEX.search(qvec, top_k)

        hits: List[Dict[str, Any]] = []
        for rank, idx in enumerate(I[0], start=1):
            ch = _CHUNKS[int(idx)]
            hits.append(
                {
                    "id": rank,
                    "source": _chunk_source(ch),
                    "text": _chunk_text(ch),
                    "score": float(D[0][rank - 1]) if len(D) else None,
                }
            )
        return hits
