"""API routes for retrieving mental health metrics.

This module exposes an endpoint to retrieve the current computed metrics
for stress, focus, and tiredness.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta

# Import singleton model instances
from src.models.stress_model import stress_service
from src.models.focus_model import focus_service
from src.models.tiredness_model import tiredness_service
from src.models.music_model import music_service
from src.models import update_models_from_latest_csv, mean_metrics
from fastapi import HTTPException

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
    timestamp: str

@router.get("/mean_metrics")
async def get_mean_metrics():
    """Zwraca uśrednione metryki z ostatnich 2 minut (bufor EEG)."""
    import datetime as dt
    result = mean_metrics()
    if result is None:
        raise HTTPException(status_code=404, detail="Brak danych w buforze")
    # Zamień timestamp na ISO
    ts_str = dt.datetime.fromtimestamp(result["timestamp"]).isoformat()
    return {
        "timestamp": ts_str,
        "focus_level": result["focus_level"],
        "stress_level": result["stress_level"],
        "tiredness_level": result["tiredness_level"],
    }

@router.get("/current", response_model=MetricsResponse)
async def get_current():
    """Return the latest computed metrics from the model singletons.

    Returns:
        MetricsResponse: Current stress, focus and tiredness levels.
    """
    # Zawsze aktualizuj modele na podstawie najnowszego pliku CSV
    import logging
    import datetime as dt
    
    mean_ts = update_models_from_latest_csv()
    stress = stress_service.get_value()
    focus = focus_service.get_value()
    tiredness = tiredness_service.get_value()
    if mean_ts is not None:
        ts_str = dt.datetime.fromtimestamp(mean_ts).isoformat()
    else:
        ts_str = dt.datetime.now().isoformat()
    logging.info(f"Zwracane metryki: stress={stress}, focus={focus}, tiredness={tiredness}, timestamp={ts_str}")
    return {
        "timestamp": ts_str,
        "stress_level": stress,
        "focus_level": focus,
        "tiredness_level": tiredness,
    }


@router.get("/music")
async def get_music():
    recommended_type = music_service.get_value()
    if recommended_type == "none":
        recommended_type = "focus"
    return {
        "music_type": recommended_type,
    }


@router.get("/history", response_model=List[MetricsResponse])
async def get_history(limit: int = 10):

    now = datetime.now()
    data_points = []

    for i in range(limit - 1, -1, -1):
        time_point = now - timedelta(minutes=i)
        data_points.append(
            {
                "timestamp": time_point.strftime("%H:%M"),
                "stress_level": 30 + (i % 5) * 10,
                "focus_level": 65 - (i % 3) * 5,
                "tiredness_level": 20 + (i % 4) * 8,
            }
        )

    return data_points
