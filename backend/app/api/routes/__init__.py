"""Modular API route definitions."""

from fastapi import APIRouter

from app.api.routes.guidance import router as guidance_router
from app.api.routes.prediction import router as prediction_router
from app.api.routes.retrieval import router as retrieval_router

api_router = APIRouter()
api_router.include_router(guidance_router)
api_router.include_router(prediction_router)
api_router.include_router(retrieval_router)
