"""Chat handler — combines DB context + RAG retrieval + LLM."""
from typing import Optional
import httpx

from app.config import settings
from app.ai.retriever import retrieve


SYSTEM_PROMPT = """You are TunisPark AI Assistant, a helpful parking management assistant.
Answer questions about parking rules, billing, access decisions, and regulations.
Always cite your sources when quoting rules or regulations.
Respond in the same language as the question (French, Arabic, or English).
Be concise, factual, and professional. Never make up information."""


def build_context(
    question: str,
    vehicle_context: str = "",
    decision_context: str = "",
) -> str:
    """Build a rich context string from DB data + retrieved docs."""
    chunks = retrieve(question, k=4)
    doc_context = "\n\n".join(
        [f"[Source: {doc.metadata.get('source', 'Unknown')}]\n{doc.page_content}" for doc, _ in chunks]
    )
    sources = list({doc.metadata.get("source", "Unknown") for doc, _ in chunks})

    context_parts = []
    if vehicle_context:
        context_parts.append(f"Vehicle Information:\n{vehicle_context}")
    if decision_context:
        context_parts.append(f"Decision Log:\n{decision_context}")
    if doc_context:
        context_parts.append(f"Relevant Regulations:\n{doc_context}")

    return "\n\n---\n\n".join(context_parts), sources


async def answer_question(
    question: str,
    vehicle_context: str = "",
    decision_context: str = "",
) -> dict:
    """Send question + context to Ollama LLM and return answer + sources."""
    context, sources = build_context(question, vehicle_context, decision_context)

    prompt = f"{SYSTEM_PROMPT}\n\n{context}\n\nQuestion: {question}\nAnswer:"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": settings.LLM_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.3, "num_predict": 500},
                },
            )
            resp.raise_for_status()
            data = resp.json()
            answer = data.get("response", "Unable to generate a response.")
    except Exception as e:
        answer = f"LLM unavailable ({type(e).__name__}). Please ensure Ollama is running with: ollama run {settings.LLM_MODEL}"

    return {
        "answer": answer.strip(),
        "sources": sources,
        "confidence": 0.85 if sources else 0.5,
    }
