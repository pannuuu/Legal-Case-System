"""Stateful session orchestration for Gemini legal intake, summary, and RAG retrieval."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import threading
from typing import Dict, List, Optional
import uuid

from app.api.schemas.guidance_schemas import (
    CaseSummaryPayload,
    ChatMessageOut,
    ConfirmSummaryResponse,
    GuidanceSessionResponse,
    HistoryTurnIn,
    SendMessageResponse,
    UpdateSummaryResponse,
)
from app.api.schemas.retrieval_schemas import RetrievalSearchRequest
from app.config import get_settings
from app.services.gemini_service import generate_intake_turn, generate_rag_guidance
from app.services.retrieval_service import search_similar_judgments


class SessionNotFoundError(KeyError):
    """Raised when a guidance session ID does not exist."""


@dataclass
class _GuidanceSession:
    session_id: str
    messages: List[ChatMessageOut] = field(default_factory=list)
    next_question: Optional[str] = None
    summary: Optional[CaseSummaryPayload] = None
    summary_confirmed: bool = False


_SESSIONS_LOCK = threading.Lock()
_SESSIONS: Dict[str, _GuidanceSession] = {}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _build_retrieval_query(summary: CaseSummaryPayload) -> str:
    return "\n".join(
        [
            f"Problem type: {summary.problem_type}",
            f"Jurisdiction: {summary.jurisdiction}",
            f"Key facts: {summary.key_facts}",
            f"Claimed harm: {summary.claimed_harm}",
            f"Requested outcome: {summary.requested_outcome}",
        ]
    )


def _to_session_response(session: _GuidanceSession) -> GuidanceSessionResponse:
    return GuidanceSessionResponse(
        session_id=session.session_id,
        messages=list(session.messages),
        next_question=session.next_question,
        summary=session.summary,
        summary_confirmed=session.summary_confirmed,
    )


def create_guidance_session() -> GuidanceSessionResponse:
    """Create and store a fresh legal guidance intake session."""
    session_id = str(uuid.uuid4())
    session = _GuidanceSession(session_id=session_id)
    with _SESSIONS_LOCK:
        _SESSIONS[session_id] = session
    return _to_session_response(session)


def get_guidance_session(session_id: str) -> GuidanceSessionResponse:
    """Return an existing guidance session snapshot."""
    with _SESSIONS_LOCK:
        session = _SESSIONS.get(session_id)
        if session is None:
            raise SessionNotFoundError(f"Guidance session '{session_id}' was not found.")
        return _to_session_response(session)


def process_guidance_message(
    session_id: str,
    message_text: str,
    prior_history: Optional[List[HistoryTurnIn]] = None,
) -> SendMessageResponse:
    """Append user turn, query Gemini for follow-up/guidance & summary, and persist state."""
    with _SESSIONS_LOCK:
        session = _SESSIONS.get(session_id)
        if session is None:
            raise SessionNotFoundError(f"Guidance session '{session_id}' was not found.")

        if not session.messages and prior_history:
            for item in prior_history:
                text = item.content.strip()
                if text:
                    session.messages.append(
                        ChatMessageOut(
                            id=f"{item.role}-{uuid.uuid4().hex[:10]}",
                            role=item.role,
                            content=text,
                            created_at=_now_iso(),
                        )
                    )

        user_msg = ChatMessageOut(
            id=f"user-{uuid.uuid4().hex[:10]}",
            role="user",
            content=message_text.strip(),
            created_at=_now_iso(),
        )
        projected_messages = [*session.messages, user_msg]
        existing_summary = session.summary

    assistant_reply, next_question, extracted_summary = generate_intake_turn(
        messages=projected_messages,
        current_summary=existing_summary,
    )

    assistant_msg = ChatMessageOut(
        id=f"assistant-{uuid.uuid4().hex[:10]}",
        role="assistant",
        content=assistant_reply,
        created_at=_now_iso(),
    )

    with _SESSIONS_LOCK:
        session = _SESSIONS.get(session_id)
        if session is None:
            raise SessionNotFoundError(f"Guidance session '{session_id}' was not found.")
        session.messages.append(user_msg)
        session.messages.append(assistant_msg)
        session.next_question = next_question
        if extracted_summary is not None:
            session.summary = extracted_summary
            session.summary_confirmed = False

        return SendMessageResponse(
            session_id=session.session_id,
            user_message=user_msg,
            assistant_message=assistant_msg,
            next_question=session.next_question,
            summary=session.summary,
            summary_confirmed=session.summary_confirmed,
        )


def save_summary_revision(
    session_id: str,
    summary_payload: CaseSummaryPayload,
) -> UpdateSummaryResponse:
    """Persist user edits to the 5-field case summary without confirming yet."""
    with _SESSIONS_LOCK:
        session = _SESSIONS.get(session_id)
        if session is None:
            raise SessionNotFoundError(f"Guidance session '{session_id}' was not found.")
        session.summary = summary_payload
        session.summary_confirmed = False
        return UpdateSummaryResponse(
            success=True,
            session_id=session.session_id,
            summary=summary_payload,
            summary_confirmed=False,
        )


def confirm_summary_and_synthesize(
    session_id: str,
    summary_payload: CaseSummaryPayload,
) -> ConfirmSummaryResponse:
    """Confirm summary, retrieve top-K Supreme Court judgments, and synthesize RAG guidance."""
    settings = get_settings()

    with _SESSIONS_LOCK:
        session = _SESSIONS.get(session_id)
        if session is None:
            raise SessionNotFoundError(f"Guidance session '{session_id}' was not found.")
        history_snapshot = list(session.messages)

    retrieval_response = search_similar_judgments(
        RetrievalSearchRequest(
            query_text=_build_retrieval_query(summary_payload),
            top_k=settings.RETRIEVAL_TOP_K,
        )
    )

    rag_reply = generate_rag_guidance(
        confirmed_summary=summary_payload,
        messages=history_snapshot,
        judgments=retrieval_response.judgments,
    )

    synthesis_msg = ChatMessageOut(
        id=f"assistant-{uuid.uuid4().hex[:10]}",
        role="assistant",
        content=rag_reply,
        created_at=_now_iso(),
    )

    with _SESSIONS_LOCK:
        session = _SESSIONS.get(session_id)
        if session is None:
            raise SessionNotFoundError(f"Guidance session '{session_id}' was not found.")
        session.summary = summary_payload
        session.summary_confirmed = True
        session.next_question = None
        session.messages.append(synthesis_msg)

        return ConfirmSummaryResponse(
            success=True,
            session_id=session.session_id,
            summary=summary_payload,
            summary_confirmed=True,
            assistant_message=synthesis_msg,
            judgments=retrieval_response.judgments,
            retrieved_count=retrieval_response.retrieved_count,
            rag_grounded=True,
        )
