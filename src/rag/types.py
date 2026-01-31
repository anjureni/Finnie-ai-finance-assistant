# src/rag/types.py
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class Chunk:
    id: str
    text: str
    source: str                 # filename or URL
    title: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
