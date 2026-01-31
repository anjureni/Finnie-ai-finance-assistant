# src/agents/finance_qa.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List
import os

from dotenv import load_dotenv
from openai import OpenAI

from src.rag.retriever import Retriever
from src.rag.prompting import build_rag_context, hits_to_sources

load_dotenv()


@dataclass
class AgentResult:
    answer: str
    sources: List[str]


class FinanceQAAgent:
    def __init__(self, index_dir: str = "data/index", top_k: int = 3):
        self.retriever = Retriever(index_dir=index_dir)
        self.top_k = top_k

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set")

        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv("CHAT_MODEL", "gpt-4o-mini")

    def run(self, state: dict) -> AgentResult:
        question = state.get("user_query") or state.get("query", "")
        if not question:
            return AgentResult(answer="Please ask a question.", sources=[])

        hits = self.retriever.retrieve(question, top_k=self.top_k)
        context = build_rag_context(hits)
        sources = hits_to_sources(hits)

        system = (
            "You are a finance education assistant. "
            "Provide general educational information only. "
            "Do not give personalized financial advice."
        )

        user_prompt = f"""
Answer the QUESTION using:
1) The CONTEXT (knowledge base) as the primary source.
2) If the context is incomplete, you MAY add helpful general finance explanation from your own knowledge.

CITATIONS RULE:
- Add citations like [1], [2] ONLY for statements supported by the CONTEXT.
- Do NOT invent citations.
- If you add general knowledge, do not cite it.

OUTPUT FORMAT:
- Start with a short answer (2–4 sentences).
- Then give 3–6 bullet points with simple explanation.
- End with a one-line disclaimer.

CONTEXT (KB):
{context}

QUESTION:
{question}
""".strip()

        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )

        answer = resp.choices[0].message.content or ""
        return AgentResult(answer=answer, sources=sources)


# Alias if registry expects this name
FinanceQAgent = FinanceQAAgent
