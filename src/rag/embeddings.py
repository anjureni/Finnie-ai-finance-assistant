# src/rag/embeddings.py
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

EMBED_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

def embed_texts(texts: list[str]) -> list[list[float]]:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    resp = client.embeddings.create(
        model=EMBED_MODEL,
        input=texts
    )
    return [d.embedding for d in resp.data]
