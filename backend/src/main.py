from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the API router created in the project
from src.api.mental_metric_routes import router as metrics_router


app = FastAPI(title="heroes-of-the-brain - backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(metrics_router, prefix="/api/metrics")


@app.get("/health")
async def health_check():
    """Simple health-check endpoint."""
    return {"status": "ok"}


def main() -> None:
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, log_level="info")


if __name__ == "__main__":
    main()
