"""FastAPI application entry point."""

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.config import get_settings
from app.models.random_forest import ModelArtifactError, get_random_forest_artifacts
from app.services.retrieval_service import (
    RetrievalIndexError,
    get_query_encoder,
    get_retrieval_index,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Preload ML and retrieval artifacts once at application startup."""
    try:
        bundle = get_random_forest_artifacts()
        logger.info(
            "Loaded Random Forest Experiment 3 artifacts (%d features).",
            bundle.expected_total_features,
        )
    except ModelArtifactError as exc:
        logger.error("Failed to preload Random Forest Experiment 3 artifacts: %s", exc)

    try:
        ret_bundle = get_retrieval_index()
        get_query_encoder(str(ret_bundle.manifest["embedding_model"]))
        logger.info(
            "Loaded persistent retrieval index (%d documents, %d chunks).",
            ret_bundle.manifest.get("document_count", 0),
            len(ret_bundle.chunks),
        )
    except RetrievalIndexError as exc:
        logger.warning("Retrieval index not preloaded: %s", exc)

    yield


def create_application() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    settings = get_settings()

    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.get("/health", tags=["Health"])
    async def health_check() -> dict[str, str]:
        """Lightweight liveness check for server readiness."""
        return {"status": "ok"}

    application.include_router(api_router, prefix=settings.API_PREFIX)

    return application


app = create_application()
