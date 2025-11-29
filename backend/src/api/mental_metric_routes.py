"""API routes for ingesting EEG data and returning computed metrics.

This module exposes two endpoints using FastAPI:

* POST /ingest - Accepts EEG alpha and beta wave lists and updates the
  registered model singletons.
* GET /current - Returns the latest computed stress, focus and tiredness
  metrics as integers in the 0-100 range.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

# Import singleton model instances
from src.models.stress_model import stress_service
from src.models.focus_model import focus_service
from src.models.tiredness_model import tiredness_service

router = APIRouter()


class EEGInput(BaseModel):
    """Request body for EEG ingestion.

    Attributes:
        alpha_waves: A list of alpha-wave amplitude measurements.
        beta_waves: A list of beta-wave amplitude measurements.
    """

    alpha_waves: List[float]
    beta_waves: List[float]


class MetricsResponse(BaseModel):
    """Response model containing computed metrics.

    Attributes:
        stress_level: Stress level (0-100).
        focus_level: Focus level (0-100).
        tiredness_level: Tiredness level (0-100).
    """

    stress_level: int
    focus_level: int
    tiredness_level: int





@router.get("/current", response_model=MetricsResponse)
async def get_current():
    """Return the latest computed metrics from the model singletons.

    Returns:
        MetricsResponse: Current stress, focus and tiredness levels.
    """
    # Collect results from three separate model singletons
    return {
        "stress_level": stress_service.get_value(),
        "focus_level": focus_service.get_value(),
        "tiredness_level": tiredness_service.get_value(),
    }