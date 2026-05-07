import hashlib
import json
import os
import re

from services.openai_service import (
    cosine_similarity,
    generate_text,
    get_embedding,
    is_openai_configured,
)


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
VECTOR_DB_DIR = os.path.join(BASE_DIR, "data", "vector_db")
EMBEDDING_CACHE_PATH = os.path.join(VECTOR_DB_DIR, "cv_chunk_embeddings.json")


def chunk_text(text, chunk_size=700, overlap=100):
    text = text or ""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap if overlap > 0 else end
        if start >= len(text) or start <= 0:
            break
    return [chunk.strip() for chunk in chunks if chunk.strip()]


def build_cv_chunks(cv_records):
    chunks = []
    for _, record in cv_records.iterrows():
        for idx, chunk in enumerate(chunk_text(record.get("extracted_text", ""))):
            chunks.append(
                {
                    "candidate_id": record.get("candidate_id", ""),
                    "candidate_name": record.get("candidate_name", ""),
                    "file_name": record.get("file_name", ""),
                    "chunk_id": idx,
                    "text": chunk,
                }
            )
    return chunks


def _keyword_overlap(question, text):
    q_words = set(re.findall(r"\b[a-zA-Z]{3,}\b", (question or "").lower()))
    t_words = set(re.findall(r"\b[a-zA-Z]{3,}\b", (text or "").lower()))
    if not q_words:
        return 0.0
    return len(q_words.intersection(t_words)) / len(q_words)


def retrieve_relevant_chunks(question, chunks, top_k=3):
    if not chunks:
        return []

    question_embedding = get_embedding(question) if is_openai_configured() else None
    cache = _load_embedding_cache() if question_embedding is not None else {}
    cache_changed = False
    scored = []
    for chunk in chunks:
        if question_embedding is not None:
            cache_key = _chunk_cache_key(chunk)
            chunk_embedding = cache.get(cache_key)
            if chunk_embedding is None:
                chunk_embedding = get_embedding(chunk["text"])
                if chunk_embedding is not None:
                    cache[cache_key] = chunk_embedding
                    cache_changed = True
            score = cosine_similarity(question_embedding, chunk_embedding)
        else:
            score = _keyword_overlap(question, chunk["text"])
        scored.append({**chunk, "score": score})

    if cache_changed:
        _save_embedding_cache(cache)

    scored.sort(key=lambda item: item["score"], reverse=True)
    selected = []
    used_files = set()
    for item in scored:
        if item["file_name"] in used_files:
            continue
        selected.append(item)
        used_files.add(item["file_name"])
        if len(selected) == top_k:
            return selected

    for item in scored:
        if item not in selected:
            selected.append(item)
        if len(selected) == top_k:
            break
    return selected


def get_cv_index_status(chunks):
    if not is_openai_configured():
        return {"total_chunks": len(chunks), "cached_chunks": 0, "missing_chunks": 0}

    cache = _load_embedding_cache()
    total_chunks = len(chunks)
    cached_chunks = sum(1 for chunk in chunks if _chunk_cache_key(chunk) in cache)
    return {
        "total_chunks": total_chunks,
        "cached_chunks": cached_chunks,
        "missing_chunks": total_chunks - cached_chunks,
    }


def answer_question_with_rag(question, retrieved_chunks):
    if not retrieved_chunks:
        return "The uploaded CVs do not contain enough information to answer this question."

    context = "\n\n".join(
        f"Source: {chunk['file_name']}\n{chunk['text']}" for chunk in retrieved_chunks
    )

    if not is_openai_configured():
        sources = ", ".join(sorted({chunk["file_name"] for chunk in retrieved_chunks}))
        return (
            "Demo keyword-search answer: relevant CV snippets were found in "
            f"{sources}. Please review the snippets below. Final hiring decisions require human review."
        )

    prompt = f"""
You are an AI recruitment assistant. Answer the question using only the provided CV context.
If the answer is not available in the context, say that the uploaded CVs do not contain enough information.
Do not invent facts. Include a short note that final hiring decisions require human review.

Question:
{question}

CV context:
{context}
"""
    return generate_text(prompt)


def _chunk_cache_key(chunk):
    text_hash = hashlib.md5(chunk["text"].encode("utf-8")).hexdigest()
    return f"{chunk['file_name']}::{chunk['chunk_id']}::{text_hash}"


def _load_embedding_cache():
    if not os.path.exists(EMBEDDING_CACHE_PATH):
        return {}
    try:
        with open(EMBEDDING_CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_embedding_cache(cache):
    os.makedirs(VECTOR_DB_DIR, exist_ok=True)
    with open(EMBEDDING_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f)
