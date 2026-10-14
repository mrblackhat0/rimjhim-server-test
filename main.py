from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

app = FastAPI(
    title="Rimjhim API",
    version="0.1.0",
    description="Minimal backend smoke-test for Rimjhim.",
)

# Prototype only. Restrict origins before public release.
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins if origin.strip()],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


@app.get("/", response_model=HealthResponse)
def root():
    return HealthResponse(status="ok", service="rimjhim-api", version=app.version)


@app.get("/health", response_model=HealthResponse)
@app.head("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok", service="rimjhim-api", version=app.version)


@app.get("/api/v1/capabilities")
def capabilities():
    return {
        "service": "rimjhim-api",
        "stage": "smoke-test",
        "audio_proxy": False,
        "persistent_storage": False,
        "features": ["health-check", "capability-check"],
        "notes": [
            "Audio should stream directly from a source that permits the intended use.",
            "Do not store downloaded audio on this server; use app-private device storage.",
            "This endpoint is a deployment smoke-test, not the finished music API.",
        ],
    }
