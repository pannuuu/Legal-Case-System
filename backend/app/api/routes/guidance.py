"""FastAPI routes for Gemini-powered conversational legal guidance and RAG synthesis."""

from fastapi import APIRouter, HTTPException, status

from app.api.schemas.guidance_schemas import (
    CaseSummaryPayload,
    ConfirmSummaryResponse,
    GuidanceSessionResponse,
    SendMessageRequest,
    SendMessageResponse,
    UpdateSummaryResponse,
)
from app.services.gemini_service import GeminiServiceError
from app.services.guidance_service import (
    SessionNotFoundError,
    confirm_summary_and_synthesize,
    create_guidance_session,
    get_guidance_session,
    process_guidance_message,
    save_summary_revision,
)
from app.services.retrieval_service import RetrievalIndexError

router = APIRouter(prefix="/guidance", tags=["Guidance"])


@router.post(
    "/sessions",
    response_model=GuidanceSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new legal guidance session",
)
async def create_session() -> GuidanceSessionResponse:
    """Initialize a new conversational legal guidance session."""
    return create_guidance_session()


@router.get(
    "/sessions/{session_id}",
    response_model=GuidanceSessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get an existing legal guidance session",
)
async def fetch_session(session_id: str) -> GuidanceSessionResponse:
    """Retrieve messages, follow-up question, and summary state for a session."""
    try:
        return get_guidance_session(session_id)
    except SessionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


def _http_exception_for_service_error(exc: Exception) -> HTTPException:
    detail = str(exc)
    is_quota = isinstance(exc, GeminiServiceError) and (
        "quota" in detail.lower() or "429" in detail
    )
    return HTTPException(
        status_code=(
            status.HTTP_429_TOO_MANY_REQUESTS
            if is_quota
            else status.HTTP_503_SERVICE_UNAVAILABLE
        ),
        detail=detail,
    )


@router.post(
    "/sessions/{session_id}/messages",
    response_model=SendMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a user message and receive Gemini intake response",
)
async def send_message(
    session_id: str,
    request: SendMessageRequest,
) -> SendMessageResponse:
    """Submit a user fact or follow-up answer and generate Gemini intake response."""
    try:
        return process_guidance_message(session_id, request.message, request.history)
    except SessionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except GeminiServiceError as exc:
        raise _http_exception_for_service_error(exc) from exc


@router.put(
    "/sessions/{session_id}/summary",
    response_model=UpdateSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Save edits to the structured case summary",
)
async def update_summary(
    session_id: str,
    payload: CaseSummaryPayload,
) -> UpdateSummaryResponse:
    """Persist user edits to the five-field case summary."""
    try:
        return save_summary_revision(session_id, payload)
    except SessionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "/sessions/{session_id}/confirm",
    response_model=ConfirmSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Confirm case summary, retrieve similar judgments, and synthesize RAG guidance",
)
async def confirm_summary(
    session_id: str,
    payload: CaseSummaryPayload,
) -> ConfirmSummaryResponse:
    """Confirm case summary, retrieve top-K precedents, and generate grounded RAG guidance."""
    try:
        return confirm_summary_and_synthesize(session_id, payload)
    except SessionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except (GeminiServiceError, RetrievalIndexError) as exc:
        raise _http_exception_for_service_error(exc) from exc
