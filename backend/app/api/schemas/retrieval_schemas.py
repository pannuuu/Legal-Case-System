"""Pydantic schemas for Supreme Court similar-judgment retrieval."""

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class RetrievalSearchRequest(BaseModel):
    """Input payload for POST /api/retrieval/judgments/search."""

    query_text: str = Field(
        ...,
        min_length=1,
        description="Confirmed case summary or legal query text.",
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of distinct precedent judgments to return.",
    )
    category: Optional[str] = Field(
        default=None,
        description="Optional legal category filter matching dataset subfolders.",
    )

    @field_validator("query_text")
    @classmethod
    def validate_query_text(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("query_text must not be empty or whitespace-only.")
        return value


class JudgmentResult(BaseModel):
    """Single retrieved Supreme Court precedent matching JudgmentCard props."""

    id: str
    court: str
    title: str
    citation: str
    date: str
    category: str
    similarity_score: float = Field(..., ge=0.0, le=100.0)
    semantic_score: float = Field(..., ge=0.0, le=1.0)
    lexical_score: float = Field(..., ge=0.0, le=1.0)
    excerpt: str
    offset_start: int
    offset_end: int
    context: str


class RetrievalSearchResponse(BaseModel):
    """Response payload for POST /api/retrieval/judgments/search."""

    success: bool = True
    total_indexed_documents: int
    total_indexed_chunks: int
    retrieved_count: int
    embedding_model: str
    judgments: List[JudgmentResult]


class RetrievalStatusResponse(BaseModel):
    """Status metadata for the persistent retrieval index."""

    ready: bool
    embedding_model: str
    document_count: int
    chunk_count: int
    categories: List[str]
