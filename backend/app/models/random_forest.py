"""Loader and validator for the Experiment 3 Random Forest model artifacts."""

from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

import joblib

from app.config import get_settings
from app.config.settings import BASE_DIR


REQUIRED_ARTIFACTS = (
    "experiment_3_random_forest_model.pkl",
    "experiment_3_tfidf_vectorizer.pkl",
    "experiment_3_metadata_encoder.pkl",
    "experiment_3_config.pkl",
    "label_mapping.pkl",
    "model_metadata.json",
)


class ModelArtifactError(RuntimeError):
    """Raised when required Experiment 3 model artifacts are missing or invalid."""


@dataclass(frozen=True)
class RandomForestArtifactBundle:
    """Immutable container holding the loaded Experiment 3 artifacts."""

    model: Any
    tfidf_vectorizer: Any
    metadata_encoder: Any
    config: dict[str, Any]
    label_mapping: dict[int, str]
    metadata: dict[str, Any]
    expected_total_features: int
    expected_tfidf_features: int
    expected_metadata_features: int
    expected_article_features: int
    allowed_categories: tuple[str, ...]
    allowed_case_types: tuple[str, ...]


def resolve_model_directory() -> Path:
    """Resolve the Experiment 3 model directory relative to the backend root."""
    settings = get_settings()
    configured = Path(settings.RANDOM_FOREST_MODEL_DIR)
    if configured.is_absolute():
        return configured
    return (BASE_DIR / configured).resolve()


def _validate_artifacts(
    model: Any,
    tfidf_vectorizer: Any,
    metadata_encoder: Any,
    config: dict[str, Any],
    label_mapping: dict[Any, str],
) -> tuple[int, int, int, int, tuple[str, ...], tuple[str, ...], dict[int, str]]:
    """Validate artifact types, dimensions, and label mapping consistency."""
    if not hasattr(model, "predict") or not hasattr(model, "predict_proba"):
        raise ModelArtifactError("Loaded Random Forest model does not support predict/predict_proba.")
    if not hasattr(tfidf_vectorizer, "transform") or not hasattr(tfidf_vectorizer, "vocabulary_"):
        raise ModelArtifactError("Loaded TF-IDF vectorizer is invalid or unfitted.")
    if not hasattr(metadata_encoder, "transform") or not hasattr(metadata_encoder, "categories_"):
        raise ModelArtifactError("Loaded metadata encoder is invalid or unfitted.")

    expected_tfidf = int(config.get("tfidf_features", 50000))
    expected_meta = int(config.get("metadata_features", 14))
    expected_article = int(config.get("article_feature_count", 1))
    expected_total = int(config.get("total_features", expected_tfidf + expected_meta + expected_article))

    actual_tfidf = len(tfidf_vectorizer.vocabulary_)
    if actual_tfidf != expected_tfidf:
        raise ModelArtifactError(
            f"TF-IDF vocabulary size mismatch: expected {expected_tfidf}, found {actual_tfidf}."
        )

    categories = metadata_encoder.categories_
    if len(categories) != 2:
        raise ModelArtifactError(
            f"Metadata encoder must expect 2 categorical fields, found {len(categories)}."
        )
    actual_meta = sum(len(cat) for cat in categories)
    if actual_meta != expected_meta:
        raise ModelArtifactError(
            f"Metadata feature count mismatch: expected {expected_meta}, found {actual_meta}."
        )

    if expected_tfidf + expected_meta + expected_article != expected_total:
        raise ModelArtifactError(
            "Experiment 3 config feature counts do not sum to total_features: "
            f"{expected_tfidf} + {expected_meta} + {expected_article} != {expected_total}."
        )

    model_features = getattr(model, "n_features_in_", None)
    if model_features != expected_total:
        raise ModelArtifactError(
            f"Random Forest n_features_in_ ({model_features}) does not match "
            f"configured total_features ({expected_total})."
        )

    normalized_mapping: dict[int, str] = {}
    for key, value in label_mapping.items():
        normalized_mapping[int(key)] = str(value)

    model_classes = [int(cls) for cls in getattr(model, "classes_", [])]
    for cls in model_classes:
        if cls not in normalized_mapping:
            raise ModelArtifactError(
                f"Model class {cls} is missing from label_mapping.pkl ({normalized_mapping})."
            )

    allowed_categories = tuple(str(c) for c in categories[0])
    allowed_case_types = tuple(str(c) for c in categories[1])

    return (
        expected_total,
        expected_tfidf,
        expected_meta,
        expected_article,
        allowed_categories,
        allowed_case_types,
        normalized_mapping,
    )


@lru_cache(maxsize=1)
def get_random_forest_artifacts() -> RandomForestArtifactBundle:
    """Load and cache all Experiment 3 Random Forest artifacts once per process."""
    model_dir = resolve_model_directory()
    if not model_dir.exists() or not model_dir.is_dir():
        raise ModelArtifactError(f"Model directory does not exist: {model_dir}")

    missing = [name for name in REQUIRED_ARTIFACTS if not (model_dir / name).is_file()]
    if missing:
        raise ModelArtifactError(
            f"Missing required Experiment 3 artifact(s) in {model_dir}: {', '.join(missing)}"
        )

    try:
        model = joblib.load(model_dir / "experiment_3_random_forest_model.pkl")
        tfidf_vectorizer = joblib.load(model_dir / "experiment_3_tfidf_vectorizer.pkl")
        metadata_encoder = joblib.load(model_dir / "experiment_3_metadata_encoder.pkl")
        config = joblib.load(model_dir / "experiment_3_config.pkl")
        label_mapping = joblib.load(model_dir / "label_mapping.pkl")
        with open(model_dir / "model_metadata.json", "r", encoding="utf-8") as fh:
            metadata = json.load(fh)
    except Exception as exc:
        raise ModelArtifactError(f"Failed to load Experiment 3 artifacts: {exc}") from exc

    (
        expected_total,
        expected_tfidf,
        expected_meta,
        expected_article,
        allowed_categories,
        allowed_case_types,
        normalized_mapping,
    ) = _validate_artifacts(
        model=model,
        tfidf_vectorizer=tfidf_vectorizer,
        metadata_encoder=metadata_encoder,
        config=config,
        label_mapping=label_mapping,
    )

    return RandomForestArtifactBundle(
        model=model,
        tfidf_vectorizer=tfidf_vectorizer,
        metadata_encoder=metadata_encoder,
        config=config,
        label_mapping=normalized_mapping,
        metadata=metadata,
        expected_total_features=expected_total,
        expected_tfidf_features=expected_tfidf,
        expected_metadata_features=expected_meta,
        expected_article_features=expected_article,
        allowed_categories=allowed_categories,
        allowed_case_types=allowed_case_types,
    )
