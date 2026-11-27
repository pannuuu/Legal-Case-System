"""FastAPI application entry point."""

from contextlib import asynccontextmanager
import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import api_router
from app.config import get_settings
from app.config.settings import BASE_DIR
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

    frontend_dist_dir = (BASE_DIR.parent / "frontend_dist").resolve()
    index_file = frontend_dist_dir / "index.html"
    if index_file.is_file():
        assets_dir = frontend_dist_dir / "assets"
        if assets_dir.is_dir():
            application.mount(
                "/assets",
                StaticFiles(directory=str(assets_dir)),
                name="frontend-assets",
            )

        @application.get("/{full_path:path}", include_in_schema=False)
        async def serve_spa(full_path: str) -> FileResponse:
            """Serve built frontend assets or SPA entrypoint in single-container deployments."""
            if full_path.startswith("api/") or full_path == "api" or full_path == "health":
                raise HTTPException(status_code=404, detail="Not found")
            if full_path:
                candidate = (frontend_dist_dir / full_path).resolve()
                if candidate.is_relative_to(frontend_dist_dir) and candidate.is_file():
                    return FileResponse(str(candidate))
            return FileResponse(str(index_file))

    return application


app = create_application()
