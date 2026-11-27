"""Persistent hybrid vector + TF-IDF index builder for Supreme Court judgment PDFs."""

from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from scipy.sparse import save_npz
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer

from app.config import get_settings
from app.config.settings import BASE_DIR
from app.utils.pdf_parser import PassageChunk, chunk_judgment_document, parse_judgment_pdf


INDEX_FILES = (
    "embeddings.npy",
    "tfidf_vectorizer.pkl",
    "tfidf_matrix.npz",
    "chunks.json",
    "index_manifest.json",
)


def resolve_retrieval_paths() -> tuple[Path, Path]:
    """Resolve retrieval dataset and persistent index directories relative to backend/."""
    settings = get_settings()
    data_dir = Path(settings.RETRIEVAL_DATA_DIR)
    if not data_dir.is_absolute():
        data_dir = (BASE_DIR / data_dir).resolve()

    index_dir = Path(settings.RETRIEVAL_INDEX_DIR)
    if not index_dir.is_absolute():
        index_dir = (BASE_DIR / index_dir).resolve()

    return data_dir, index_dir


def is_index_ready(index_dir: Path | None = None) -> bool:
    """Return True if all persistent retrieval index files exist."""
    if index_dir is None:
        _, index_dir = resolve_retrieval_paths()
    return all((index_dir / name).is_file() for name in INDEX_FILES)


def build_retrieval_index(force_rebuild: bool = False) -> dict[str, Any]:
    """Extract PDFs, chunk passages, compute embeddings & TF-IDF, and persist to disk."""
    settings = get_settings()
    data_dir, index_dir = resolve_retrieval_paths()

    if not data_dir.exists() or not data_dir.is_dir():
        raise FileNotFoundError(f"Retrieval dataset directory not found: {data_dir}")

    index_dir.mkdir(parents=True, exist_ok=True)
    if not force_rebuild and is_index_ready(index_dir):
        with open(index_dir / "index_manifest.json", "r", encoding="utf-8") as fh:
            return json.load(fh)

    pdf_files = sorted(data_dir.rglob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in {data_dir}")

    chunks: list[PassageChunk] = []
    categories: set[str] = set()
    next_chunk_id = 0

    for pdf_path in pdf_files:
        doc = parse_judgment_pdf(pdf_path, dataset_root=data_dir)
        categories.add(doc.category)
        doc_chunks = chunk_judgment_document(doc, start_chunk_id=next_chunk_id)
        chunks.extend(doc_chunks)
        next_chunk_id += len(doc_chunks)

    if not chunks:
        raise RuntimeError("No text passages were extracted from the retrieval dataset.")

    # Normalize whitespace only for representation; original verbatim text & offsets stay intact.
    corpus_texts = [
        f"{chunk.title}. {chunk.category}. {' '.join(chunk.excerpt.split())}"
        for chunk in chunks
    ]

    model_name = settings.EMBEDDING_MODEL_NAME or "sentence-transformers/all-MiniLM-L6-v2"
    encoder = SentenceTransformer(model_name, device="cpu")
    embeddings = encoder.encode(
        corpus_texts,
        batch_size=64,
        show_progress_bar=False,
        normalize_embeddings=True,
        convert_to_numpy=True,
    ).astype(np.float32)

    tfidf_vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        max_features=30000,
        sublinear_tf=True,
    )
    tfidf_matrix = tfidf_vectorizer.fit_transform(corpus_texts)

    np.save(index_dir / "embeddings.npy", embeddings)
    joblib.dump(tfidf_vectorizer, index_dir / "tfidf_vectorizer.pkl")
    save_npz(index_dir / "tfidf_matrix.npz", tfidf_matrix)

    with open(index_dir / "chunks.json", "w", encoding="utf-8") as fh:
        json.dump([asdict(c) for c in chunks], fh, ensure_ascii=False)

    manifest = {
        "embedding_model": model_name,
        "embedding_dim": int(embeddings.shape[1]),
        "document_count": len(pdf_files),
        "chunk_count": len(chunks),
        "categories": sorted(categories),
        "tfidf_vocabulary_size": len(tfidf_vectorizer.vocabulary_),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    with open(index_dir / "index_manifest.json", "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)

    return manifest


if __name__ == "__main__":
    summary = build_retrieval_index(force_rebuild=True)
    print(json.dumps(summary, indent=2))
