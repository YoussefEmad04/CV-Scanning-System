import os

import numpy as np
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


def is_openai_configured():
    return bool(os.getenv("OPENAI_API_KEY"))


def get_openai_client():
    if not is_openai_configured():
        return None
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_text(prompt, system_message=None):
    if not is_openai_configured():
        return "OpenAI API key is missing. Demo fallback response is being used."

    client = get_openai_client()
    model = os.getenv("OPENAI_MODEL", "gpt-4.1")

    try:
        instructions = system_message or "You are a helpful AI assistant."
        response = client.responses.create(
            model=model,
            instructions=instructions,
            input=prompt,
        )
        return response.output_text
    except Exception as exc:
        return f"OpenAI request failed: {exc}"


def get_embedding(text):
    if not is_openai_configured() or not text:
        return None

    client = get_openai_client()
    model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

    try:
        response = client.embeddings.create(model=model, input=text[:12000])
        return response.data[0].embedding
    except Exception:
        return None


def cosine_similarity(vec1, vec2):
    if vec1 is None or vec2 is None:
        return 0.0

    a = np.array(vec1, dtype=float)
    b = np.array(vec2, dtype=float)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)
