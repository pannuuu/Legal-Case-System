"""Hybrid semantic + lexical retrieval service over the persistent judgment index."""

from dataclasses import dataclass
from functools import lru_cache
import json
from typing import Any

import joblib
import numpy as np
from scipy.sparse import csr_matrix, load_npz
from sentence_transformers import SentenceTransformer

from app.api.schemas.retrieval_schemas import (
    JudgmentResult,
    RetrievalSearchRequest,
    RetrievalSearchResponse,
    RetrievalStatusResponse,
)
from app.services.retrieval_indexer import (
    INDEX_FILES,
    is_index_ready,
    resolve_retrieval_paths,
)


class RetrievalIndexError(RuntimeError):
    """Raised when the persistent retrieval index is missing or invalid."""


@dataclass(frozen=True)
class RetrievalIndexBundle:
    """In-memory loaded persistent vector and TF-IDF index."""

    embeddings: np.ndarray
    tfidf_vectorizer: Any
    tfidf_matrix: csr_matrix
    chunks: list[dict[str, Any]]
    manifest: dict[str, Any]


@lru_cache(maxsize=1)
def get_query_encoder(model_name: str) -> SentenceTransformer:
    """Load and cache the SentenceTransformer encoder once per process (offline-first)."""
    try:
        return SentenceTransformer(model_name, device="cpu", local_files_only=True)
    except Exception:
        return SentenceTransformer(model_name, device="cpu")


@lru_cache(maxsize=1)
def get_retrieval_index() -> RetrievalIndexBundle:
    """Load and cache the persistent retrieval index artifacts once per process."""
    _, index_dir = resolve_retrieval_paths()
    if not is_index_ready(index_dir):
        missing = [name for name in INDEX_FILES if not (index_dir / name).is_file()]
        raise RetrievalIndexError(
            f"Persistent retrieval index is incomplete in {index_dir}. Missing: {', '.join(missing)}. "
            "Run `python -m app.services.retrieval_indexer` to build it."
        )

    try:
        embeddings = np.load(index_dir / "embeddings.npy")
        tfidf_vectorizer = joblib.load(index_dir / "tfidf_vectorizer.pkl")
        tfidf_matrix = load_npz(index_dir / "tfidf_matrix.npz").tocsr()
        with open(index_dir / "chunks.json", "r", encoding="utf-8") as fh:
            chunks = json.load(fh)
        with open(index_dir / "index_manifest.json", "r", encoding="utf-8") as fh:
            manifest = json.load(fh)
    except Exception as exc:
        raise RetrievalIndexError(f"Failed to load retrieval index: {exc}") from exc

    if len(chunks) != embeddings.shape[0] or len(chunks) != tfidf_matrix.shape[0]:
        raise RetrievalIndexError(
            "Retrieval index dimension mismatch between chunks, embeddings, and TF-IDF matrix."
        )

    return RetrievalIndexBundle(
        embeddings=embeddings,
        tfidf_vectorizer=tfidf_vectorizer,
        tfidf_matrix=tfidf_matrix,
        chunks=chunks,
        manifest=manifest,
    )


def get_retrieval_status() -> RetrievalStatusResponse:
    """Return index readiness and corpus statistics."""
    _, index_dir = resolve_retrieval_paths()
    if not is_index_ready(index_dir):
        return RetrievalStatusResponse(
            ready=False,
            embedding_model="",
            document_count=0,
            chunk_count=0,
            categories=[],
        )

    bundle = get_retrieval_index()
    manifest = bundle.manifest
    return RetrievalStatusResponse(
        ready=True,
        embedding_model=str(manifest.get("embedding_model", "")),
        document_count=int(manifest.get("document_count", 0)),
        chunk_count=int(manifest.get("chunk_count", len(bundle.chunks))),
        categories=list(manifest.get("categories", [])),
    )


def search_similar_judgments(request: RetrievalSearchRequest) -> RetrievalSearchResponse:
    """Perform hybrid semantic + TF-IDF search with per-judgment deduplication."""
    bundle = get_retrieval_index()
    query = " ".join(request.query_text.split()).strip()
    if not query:
        raise ValueError("query_text must not be empty.")

    model_name = str(bundle.manifest["embedding_model"])
    encoder = get_query_encoder(model_name)

    query_embedding = encoder.encode(
        [query],
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    ).astype(np.float32)[0]

    semantic_scores = bundle.embeddings @ query_embedding
    query_tfidf = bundle.tfidf_vectorizer.transform([query])
    lexical_scores = (bundle.tfidf_matrix @ query_tfidf.T).toarray().ravel()

    # Clamp semantic cosine to [0, 1] and combine with lexical TF-IDF cosine.
    semantic_clamped = np.clip(semantic_scores, 0.0, 1.0)
    lexical_clamped = np.clip(lexical_scores, 0.0, 1.0)
    hybrid_scores = (0.80 * semantic_clamped) + (0.20 * lexical_clamped)

    category_filter = request.category.strip().lower() if request.category else None
    ranked_indices = np.argsort(hybrid_scores)[::-1]

    selected_results: list[JudgmentResult] = []
    seen_docs: set[str] = set()

    for idx in ranked_indices:
        chunk = bundle.chunks[int(idx)]
        doc_id = chunk["doc_id"]
        if doc_id in seen_docs:
            continue
        if category_filter and chunk["category"].strip().lower() != category_filter:
            continue

        seen_docs.add(doc_id)
        sem_val = float(semantic_clamped[int(idx)])
        lex_val = float(lexical_clamped[int(idx)])
        hyb_val = float(hybrid_scores[int(idx)])

        selected_results.append(
            JudgmentResult(
                id=f"{doc_id}::{chunk['chunk_id']}",
                court=chunk["court"],
                title=chunk["title"],
                citation=chunk["citation"],
                date=chunk["date"],
                category=chunk["category"],
                similarity_score=round(min(100.0, max(0.0, hyb_val * 100.0)), 1),
                semantic_score=round(sem_val, 4),
                lexical_score=round(lex_val, 4),
                excerpt=chunk["excerpt"],
                offset_start=int(chunk["offset_start"]),
                offset_end=int(chunk["offset_end"]),
                context=chunk["context"],
            )
        )
        if len(selected_results) >= request.top_k:
            break

    return RetrievalSearchResponse(
        success=True,
        total_indexed_documents=int(bundle.manifest.get("document_count", 0)),
        total_indexed_chunks=len(bundle.chunks),
        retrieved_count=len(selected_results),
        embedding_model=model_name,
        judgments=selected_results,
    )
