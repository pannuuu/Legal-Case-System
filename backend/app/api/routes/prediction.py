"""FastAPI routes for Experiment 3 Random Forest outcome prediction."""

from fastapi import APIRouter, HTTPException, status

from app.api.schemas.prediction_schemas import PredictionRequest, PredictionResponse
from app.models.random_forest import ModelArtifactError
from app.services.prediction_service import predict_case_outcome

router = APIRouter(prefix="/prediction", tags=["Prediction"])


@router.post(
    "/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Predict appellate outcome using Random Forest Experiment 3",
)
async def predict_outcome(request: PredictionRequest) -> PredictionResponse:
    """Preprocess confirmed case text and metadata and return Random Forest outcome prediction."""
    try:
        return predict_case_outcome(request)
    except ModelArtifactError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
