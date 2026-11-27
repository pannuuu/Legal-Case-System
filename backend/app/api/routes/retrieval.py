"""FastAPI routes for persistent Supreme Court judgment retrieval."""

from fastapi import APIRouter, HTTPException, status

from app.api.schemas.retrieval_schemas import (
    RetrievalSearchRequest,
    RetrievalSearchResponse,
    RetrievalStatusResponse,
)
from app.services.retrieval_service import (
    RetrievalIndexError,
    get_retrieval_status,
    search_similar_judgments,
)

router = APIRouter(prefix="/retrieval", tags=["Retrieval"])


@router.get(
    "/status",
    response_model=RetrievalStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Check persistent retrieval vector index status",
)
async def retrieval_status() -> RetrievalStatusResponse:
    """Return readiness and corpus metadata for the retrieval index."""
    try:
        return get_retrieval_status()
    except RetrievalIndexError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.post(
    "/judgments/search",
    response_model=RetrievalSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve similar Supreme Court judgments by semantic and lexical similarity",
)
async def search_judgments(request: RetrievalSearchRequest) -> RetrievalSearchResponse:
    """Search the persistent vector index for top-K relevant Supreme Court precedents."""
    try:
        return search_similar_judgments(request)
    except RetrievalIndexError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
