"""API routes for retrieving mental health metrics.

This module exposes an endpoint to retrieve the current computed metrics
for stress, focus, and tiredness.
"""

from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel

from src.models import mean_metrics, update_models_from_latest_csv
from src.models.focus_model import focus_service
from src.models.music_model import music_service
from src.models.pomodoro_model import PomodoroStepper

# Import singleton model instances
from src.models.stress_model import stress_service
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
    timestamp: str

@router.get("/mean_metrics")
async def get_mean_metrics():
    """Return mean metrics averaged over the last 2 minutes (EEG buffer).

    Returns:
        dict: Averaged focus, stress, tiredness, and timestamp in ISO format.

    Raises:
        HTTPException: If no data is available in the buffer.

    """
    import datetime as dt
    import logging
    result = mean_metrics()
    if result is None:
        logging.getLogger(__name__).warning("No data in EEG buffer for mean_metrics endpoint.")
        raise HTTPException(status_code=404, detail="Brak danych w buforze")
    ts_str = dt.datetime.fromtimestamp(result["timestamp"]).isoformat()
    logging.getLogger(__name__).info(
        "Returned mean_metrics: focus=%d, stress=%d, tiredness=%d, timestamp=%s",
        result["focus_level"], result["stress_level"], result["tiredness_level"], ts_str,
    )
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
    import datetime as dt
    import logging

    mean_ts = update_models_from_latest_csv()
    stress = stress_service.get_value()
    focus = focus_service.get_value()
    tiredness = tiredness_service.get_value()
    if mean_ts is not None:
        ts_str = dt.datetime.fromtimestamp(mean_ts).isoformat()
    else:
        ts_str = dt.datetime.now().isoformat()
    logging.getLogger(__name__).info(
        "Returned metrics: stress=%d, focus=%d, tiredness=%d, timestamp=%s",
        stress, focus, tiredness, ts_str,
    )
    return {
        "timestamp": ts_str,
        "stress_level": stress,
        "focus_level": focus,
        "tiredness_level": tiredness,
    }


@router.get("/music")
async def get_music():
    """Return the recommended music type based on current metrics.

    Returns:
        dict: Recommended music type.

    """
    recommended_type = music_service.get_value()
    if recommended_type == "none":
        recommended_type = "focus"
    return {
        "music_type": recommended_type,
    }


@router.get("/history", response_model=list[MetricsResponse])
async def get_history(limit: int = 10):
    """Return a list of historical metrics (mock data).

    Args:
        limit (int): Number of data points to return.

    Returns:
        list[MetricsResponse]: List of historical metrics.

    """
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
            },
        )
    return data_points


pomodoro_stepper = PomodoroStepper()


@router.post("/pomodoro/update_times")
async def update_pomodoro_times(
    work_time: int = Body(..., embed=True),
    short_break_time: int = Body(..., embed=True),
    long_break_time: int = Body(..., embed=True),
):
    """
    Update Pomodoro stepper times (work, short break, long break) in minutes.
    """
    global pomodoro_stepper
    pomodoro_stepper = PomodoroStepper(
        session_length=work_time,
        break_length=short_break_time,
        long_break_length=long_break_time,
    )
    return {"status": "ok", "work_time": work_time, "short_break_time": short_break_time, "long_break_time": long_break_time}

@router.get("/pomodoro/config")
async def get_pomodoro_config():
    """
    Return current Pomodoro config (work, shortBreak, longBreak) in seconds.
    """
    # Użyj domyślnego PomodoroStepper z aktualnymi wartościami
    return {
        "work": pomodoro_stepper.session_length * 60,
        "shortBreak": pomodoro_stepper.break_length * 60,
        "longBreak": pomodoro_stepper.long_break_length * 60,
    }
