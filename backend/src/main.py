"""Backend application entrypoint.

This module exposes a FastAPI `app` instance so the service can be run
by an ASGI server (for example `uvicorn backend.main:app`). It also
provides a `__main__` runner that launches `uvicorn` for local
development.
"""

from fastapi import FastAPI

# Import the API router created in the project
from src.api.mental_metric_routes import router as metrics_router


app = FastAPI(title="heroes-of-the-brain - backend")

# Mount metric-related routes under /metrics
app.include_router(metrics_router, prefix="/metrics")


@app.get("/health")
async def health_check():
    """Simple health-check endpoint."""
    return {"status": "ok"}


def main() -> None:
    """Run the application using uvicorn (development only).

    This function is intentionally lightweight and is only executed when
    the module is run as a script (`python -m backend.main` or
    `python backend/main.py`). In production use an ASGI server to run
    `backend.main:app` instead.
    """
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, log_level="info")


if __name__ == "__main__":
    main()
