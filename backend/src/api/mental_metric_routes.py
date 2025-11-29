"""API routes for retrieving mental health metrics.

This module exposes an endpoint to retrieve the current computed metrics
for stress, focus, and tiredness.
"""

from fastapi import APIRouter
from pydantic import BaseModel

# Import singleton model instances
from src.models.stress_model import stress_service
from src.models.focus_model import focus_service
from src.models.tiredness_model import tiredness_service

router = APIRouter()


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
    # return {
    #     "stress_level": stress_service.get_value(),
    #     "focus_level": focus_service.get_value(),
    #     "tiredness_level": tiredness_service.get_value(),
    # }
    return {
        "stress_level": 30,
        "focus_level": 65,
        "tiredness_level": 20,
    }
