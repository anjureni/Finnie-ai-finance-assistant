# src/core/llm.py
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def get_client() -> OpenAI:
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def chat_completion(messages: list[dict], temperature: float = 0.2) -> str:
    """
    Minimal LLM wrapper for chat completion.
    messages = [{"role":"system/user/assistant","content":"..."}]
    """
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    client = get_client()

    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return resp.choices[0].message.content
