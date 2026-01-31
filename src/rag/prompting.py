# src/rag/prompting.py
from __future__ import annotations
from typing import Any, Dict, List


def build_rag_context(hits: List[Dict[str, Any]]) -> str:
    """
    Build a context string with numbered sources for citation.
    """
    lines: List[str] = []
    for h in hits:
        i = h.get("id")
        src = h.get("source", "knowledge_base")
        txt = h.get("text", "")
        lines.append(f"[{i}] Source: {src}")
        lines.append(txt)
        lines.append("")  # spacing
    return "\n".join(lines).strip()


def hits_to_sources(hits: List[Dict[str, Any]]) -> List[str]:
    """
    Make a clean, unique sources list for the UI.
    Output examples:
      [1] diversification_basics.txt
      [2] etf_basics.txt
    """
    out: List[str] = []
    seen = set()
    for h in hits:
        i = h.get("id")
        src = h.get("source", "knowledge_base")
        label = f"[{i}] {src}"
        if label not in seen:
            seen.add(label)
            out.append(label)
    return out
