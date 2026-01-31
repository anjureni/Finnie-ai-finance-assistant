# src/agents/base.py
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class AgentResult:
    answer: str
    sources: List[str]

class BaseAgent:
    name: str = "base"

    def run(self, state: Dict[str, Any]) -> AgentResult:
        raise NotImplementedError
