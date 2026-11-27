"""Prediction service executing Experiment 3 Random Forest preprocessing and inference."""

import logging
import re
from typing import Any, Optional

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, hstack

from app.api.schemas.prediction_schemas import (
    AppliedMetadata,
    ClassProbabilities,
    PredictionRequest,
    PredictionResponse,
)
from app.models.random_forest import RandomForestArtifactBundle, get_random_forest_artifacts
from app.services.gemini_service import GeminiServiceError, generate_firac_and_merit
from app.utils.text_preprocessing import (
    clean_case_text,
    detect_constitutional_article_reference,
    preprocess_text,
)

logger = logging.getLogger(__name__)


def _normalize_metadata(
    request: PredictionRequest,
    cleaned_text: str,
    bundle: RandomForestArtifactBundle,
) -> tuple[str, str, bool, str]:
    """Normalize metadata inputs to match training-time encoder schema."""
    raw_category = (request.metadata.case_category or "unknown").strip().lower()
    if not raw_category:
        raw_category = "unknown"
    if raw_category not in bundle.allowed_categories:
        case_category = "unknown"
    else:
        case_category = raw_category

    case_type = (request.metadata.case_type or "").strip().lower()

    if request.metadata.has_article_reference is not None:
        has_article = bool(request.metadata.has_article_reference)
        article_source = "explicit_metadata"
    else:
        has_article = detect_constitutional_article_reference(cleaned_text)
        article_source = "inferred_from_case_text"

    return case_category, case_type, has_article, article_source


def _build_feature_matrix(
    cleaned_text: str,
    case_category: str,
    case_type: str,
    has_article: bool,
    bundle: RandomForestArtifactBundle,
) -> tuple[csr_matrix, int]:
    """Assemble the 50,015-dimension feature matrix in exact training order."""
    # 1. TF-IDF features (1 x 50,000)
    tfidf_matrix = bundle.tfidf_vectorizer.transform([cleaned_text])
    if tfidf_matrix.shape != (1, bundle.expected_tfidf_features):
        raise ValueError(
            f"TF-IDF output shape mismatch: expected (1, {bundle.expected_tfidf_features}), "
            f"got {tfidf_matrix.shape}."
        )
    matched_tfidf_terms = int(tfidf_matrix.nnz)

    # 2. One-hot encoded metadata features (1 x 14)
    encoder_columns = list(
        getattr(bundle.metadata_encoder, "feature_names_in_", ["case_category", "case_type"])
    )
    meta_df = pd.DataFrame([[case_category, case_type]], columns=encoder_columns)
    meta_matrix = bundle.metadata_encoder.transform(meta_df)
    if meta_matrix.shape != (1, bundle.expected_metadata_features):
        raise ValueError(
            f"Metadata encoder output shape mismatch: expected (1, {bundle.expected_metadata_features}), "
            f"got {meta_matrix.shape}."
        )

    # 3. Constitutional article binary indicator (1 x 1)
    article_value = 1.0 if has_article else 0.0
    article_matrix = csr_matrix(np.array([[article_value]], dtype=np.float64))

    # Combine in exact training order: [TF-IDF (50000), Metadata (14), has_article_reference (1)]
    combined = hstack([tfidf_matrix, meta_matrix, article_matrix], format="csr")
    if combined.shape != (1, bundle.expected_total_features):
        raise ValueError(
            f"Combined feature matrix shape mismatch: expected (1, {bundle.expected_total_features}), "
            f"got {combined.shape}."
        )

    return combined, matched_tfidf_terms


_VERDICT_LEAKAGE_PATTERN = re.compile(
    r"\bappeal\s+(?:is\s+|hereby\s+)?(?:allowed|dismissed|disposed)\b"
    r"|\bset\s+aside\b"
    r"|\bdismissed\s+with\s+costs?\b",
    flags=re.IGNORECASE,
)


def _format_outcome(predicted_class: str) -> str:
    """Map mapped label name to human-readable appellate outcome string."""
    lower = predicted_class.strip().lower()
    if lower == "accepted":
        return "Appeal Accepted"
    if lower == "rejected":
        return "Appeal Rejected"
    return predicted_class


def _blend_hybrid_probabilities(
    rf_accepted: float,
    merit_score: float,
    label_mapping: dict[int, str],
) -> tuple[int, str, float, dict[str, float]]:
    """Combine Experiment 3 RF appellate baseline (0.30) with statutory merit score (0.70)."""
    accepted_prob = round(max(0.0, min(1.0, 0.30 * rf_accepted + 0.70 * merit_score)), 4)
    rejected_prob = round(max(0.0, min(1.0, 1.0 - accepted_prob)), 4)

    target_key = "accepted" if accepted_prob >= 0.5 else "rejected"
    reverse_map = {str(name).strip().lower(): int(cid) for cid, name in label_mapping.items()}
    class_id = reverse_map.get(target_key, 1 if target_key == "accepted" else 0)
    predicted_class = label_mapping.get(class_id, target_key.capitalize())
    confidence = accepted_prob if target_key == "accepted" else rejected_prob
    return class_id, predicted_class, confidence, {
        "accepted": accepted_prob,
        "rejected": rejected_prob,
    }


def predict_case_outcome(request: PredictionRequest) -> PredictionResponse:
    """Run Experiment 3 preprocessing and Random Forest inference on a case request."""
    bundle = get_random_forest_artifacts()
    raw_text = clean_case_text(request.case_text)

    input_mode = "raw_case_text"
    model_input_text = raw_text
    statutory_merit_score: Optional[float] = None
    applicable_provisions: list[str] = []
    legal_basis_note = ""
    if request.use_firac:
        try:
            (
                model_input_text,
                statutory_merit_score,
                applicable_provisions,
                legal_basis_note,
            ) = generate_firac_and_merit(raw_text)
            input_mode = "firac_structured"
        except GeminiServiceError as exc:
            logger.warning("FIRAC formatting unavailable (%s); falling back to raw case_text.", exc)
            input_mode = "raw_case_text_fallback"

    preprocessed_text = preprocess_text(model_input_text)

    case_category, case_type, has_article, article_source = _normalize_metadata(
        request=request,
        cleaned_text=raw_text,
        bundle=bundle,
    )

    feature_matrix, matched_tfidf_terms = _build_feature_matrix(
        cleaned_text=preprocessed_text,
        case_category=case_category,
        case_type=case_type,
        has_article=has_article,
        bundle=bundle,
    )

    raw_prediction = bundle.model.predict(feature_matrix)[0]
    predicted_class_id = int(raw_prediction)
    predicted_class = bundle.label_mapping[predicted_class_id]

    proba_row = bundle.model.predict_proba(feature_matrix)[0]
    model_classes: list[Any] = list(bundle.model.classes_)

    class_prob_map: dict[str, float] = {}
    predicted_confidence = 0.0
    for idx, cls_value in enumerate(model_classes):
        cls_id = int(cls_value)
        label_name = bundle.label_mapping[cls_id].strip().lower()
        prob = round(float(proba_row[idx]), 4)
        class_prob_map[label_name] = prob
        if cls_id == predicted_class_id:
            predicted_confidence = prob

    if (
        statutory_merit_score is not None
        and not _VERDICT_LEAKAGE_PATTERN.search(raw_text)
    ):
        predicted_class_id, predicted_class, predicted_confidence, class_prob_map = (
            _blend_hybrid_probabilities(
                rf_accepted=class_prob_map["accepted"],
                merit_score=statutory_merit_score,
                label_mapping=bundle.label_mapping,
            )
        )

    return PredictionResponse(
        success=True,
        model="Random Forest Experiment 3",
        class_id=predicted_class_id,
        predicted_class=predicted_class,
        predicted_outcome=_format_outcome(predicted_class),
        confidence=predicted_confidence,
        probabilities=ClassProbabilities(
            accepted=class_prob_map["accepted"],
            rejected=class_prob_map["rejected"],
        ),
        feature_count=int(feature_matrix.shape[1]),
        matched_tfidf_terms=matched_tfidf_terms,
        input_mode=input_mode,
        applicable_provisions=applicable_provisions,
        legal_basis_note=legal_basis_note,
        metadata_used=AppliedMetadata(
            case_category=case_category,
            case_type=case_type,
            has_article_reference=has_article,
            article_reference_source=article_source,
        ),
    )
