"""Pydantic schemas for Random Forest Experiment 3 outcome prediction."""

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class CaseMetadataInput(BaseModel):
    """Metadata fields matching experiment_3_metadata_encoder.pkl and article indicator."""

    case_category: str = Field(
        default="unknown",
        description="Case category ('civil', 'criminal', or 'unknown').",
    )
    case_type: Optional[str] = Field(
        default=None,
        description=(
            "Case type matching encoder categories (e.g., 'appeal', 'writ petition', "
            "'special leave petition', etc.)."
        ),
    )
    has_article_reference: Optional[bool] = Field(
        default=None,
        description=(
            "Optional constitutional article indicator. When omitted, inferred from case_text."
        ),
    )


class PredictionRequest(BaseModel):
    """Input payload for POST /api/prediction/predict."""

    case_text: str = Field(
        ...,
        min_length=1,
        description="The complete confirmed legal case description.",
    )
    metadata: CaseMetadataInput = Field(
        default_factory=CaseMetadataInput,
        description="Optional structured case metadata.",
    )
    use_firac: bool = Field(
        default=False,
        description=(
            "When true, converts confirmed intake text into a neutral FIRAC representation "
            "before TF-IDF feature extraction (falls back to raw case_text if unavailable)."
        ),
    )

    @field_validator("case_text")
    @classmethod
    def validate_case_text(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("case_text must not be empty or whitespace-only.")
        return value


class ClassProbabilities(BaseModel):
    """Predicted probabilities for each binary class."""

    accepted: float = Field(..., ge=0.0, le=1.0)
    rejected: float = Field(..., ge=0.0, le=1.0)


class AppliedMetadata(BaseModel):
    """Normalized metadata actually fed into the Experiment 3 feature vector."""

    case_category: str
    case_type: str
    has_article_reference: bool
    article_reference_source: str


class PredictionResponse(BaseModel):
    """Structured prediction response from Random Forest Experiment 3."""

    success: bool = True
    model: str
    class_id: int
    predicted_class: str
    predicted_outcome: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    probabilities: ClassProbabilities
    feature_count: int
    matched_tfidf_terms: int = 0
    input_mode: str = "raw_case_text"
    applicable_provisions: List[str] = Field(default_factory=list)
    legal_basis_note: str = ""
    metadata_used: AppliedMetadata
