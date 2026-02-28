"""Document embedding pipeline for the RAG knowledge base."""
import os
from app.config import settings

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def embed_knowledge_base(kb_dir: str = None, index_path: str = None) -> FAISS:
    """Load all PDFs from the knowledge base directory and build a FAISS index."""
    kb_dir = kb_dir or settings.KNOWLEDGE_BASE_DIR
    index_path = index_path or settings.FAISS_INDEX_PATH

    pdf_files = [f for f in os.listdir(kb_dir) if f.endswith(".pdf")]
    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in {kb_dir}")

    all_docs = []
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

    for pdf_file in pdf_files:
        path = os.path.join(kb_dir, pdf_file)
        print(f"Loading: {pdf_file}")
        loader = PyPDFLoader(path)
        docs = loader.load()
        chunks = splitter.split_documents(docs)
        # Tag each chunk with its source file
        for chunk in chunks:
            chunk.metadata["source"] = pdf_file
        all_docs.extend(chunks)

    print(f"Total chunks: {len(all_docs)}")
    embeddings = get_embeddings()
    vectorstore = FAISS.from_documents(all_docs, embeddings)
    vectorstore.save_local(index_path)
    print(f"FAISS index saved to: {index_path}")
    return vectorstore


def load_vectorstore(index_path: str = None) -> FAISS:
    """Load an existing FAISS index from disk."""
    index_path = index_path or settings.FAISS_INDEX_PATH
    if not os.path.exists(index_path):
        raise FileNotFoundError(
            f"FAISS index not found at '{index_path}'. "
            "Run embed_knowledge_base() first or upload documents via the admin panel."
        )
    embeddings = get_embeddings()
    return FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)


if __name__ == "__main__":
    embed_knowledge_base()
