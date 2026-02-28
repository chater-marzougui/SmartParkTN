"""RAG retriever — builds context for LLM questions."""
from typing import List, Tuple
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

from app.ai.embedder import load_vectorstore


_vectorstore: FAISS | None = None


def get_vectorstore() -> FAISS:
    global _vectorstore
    if _vectorstore is None:
        try:
            _vectorstore = load_vectorstore()
        except FileNotFoundError:
            return None
    return _vectorstore


def reload_vectorstore():
    """Force-reload from disk (called after re-embedding)."""
    global _vectorstore
    _vectorstore = load_vectorstore()
    return _vectorstore


def retrieve(query: str, k: int = 4) -> List[Tuple[Document, float]]:
    """Return top-k most relevant document chunks with scores."""
    vs = get_vectorstore()
    if vs is None:
        return []
    return vs.similarity_search_with_score(query, k=k)
