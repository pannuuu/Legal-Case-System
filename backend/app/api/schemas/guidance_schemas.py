"""Pydantic schemas for conversational legal guidance, case summary, and RAG synthesis."""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

from app.api.schemas.retrieval_schemas import JudgmentResult


class CaseSummaryPayload(BaseModel):
    """Structured five-field case summary matching Section 02 of the UI."""

    problem_type: str = Field(..., min_length=1)
    jurisdiction: str = Field(..., min_length=1)
    key_facts: str = Field(..., min_length=1)
    claimed_harm: str = Field(..., min_length=1)
    requested_outcome: str = Field(..., min_length=1)

    @field_validator(
        "problem_type",
        "jurisdiction",
        "key_facts",
        "claimed_harm",
        "requested_outcome",
    )
    @classmethod
    def validate_non_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Summary field must not be blank.")
        return cleaned


class ChatMessageOut(BaseModel):
    """Single conversational turn in the intake transcript."""

    id: str
    role: Literal["user", "assistant"]
    content: str
    created_at: str


class GuidanceSessionResponse(BaseModel):
    """Full guidance session snapshot."""

    session_id: str
    messages: List[ChatMessageOut]
    next_question: Optional[str] = None
    summary: Optional[CaseSummaryPayload] = None
    summary_confirmed: bool = False


class HistoryTurnIn(BaseModel):
    """Optional prior turn used to restore context if a session expired after reload."""

    role: Literal["user", "assistant"]
    content: str


class SendMessageRequest(BaseModel):
    """User message payload for POST /api/guidance/sessions/{session_id}/messages."""

    message: str = Field(..., min_length=1)
    history: Optional[List[HistoryTurnIn]] = None

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("message must not be empty or whitespace-only.")
        return cleaned


class SendMessageResponse(BaseModel):
    """Response after Gemini processes a user intake turn."""

    session_id: str
    user_message: ChatMessageOut
    assistant_message: ChatMessageOut
    next_question: Optional[str] = None
    summary: Optional[CaseSummaryPayload] = None
    summary_confirmed: bool = False


class UpdateSummaryResponse(BaseModel):
    """Response after saving a draft summary revision."""

    success: bool = True
    session_id: str
    summary: CaseSummaryPayload
    summary_confirmed: bool = False


class ConfirmSummaryResponse(BaseModel):
    """Response after confirming summary, retrieving precedents, and generating RAG guidance."""

    success: bool = True
    session_id: str
    summary: CaseSummaryPayload
    summary_confirmed: bool = True
    assistant_message: ChatMessageOut
    judgments: List[JudgmentResult]
    retrieved_count: int
    rag_grounded: bool = True
