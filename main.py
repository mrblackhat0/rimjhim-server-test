import asyncio
import re
from urllib.parse import parse_qs, urlparse

import yt_dlp
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="Rimjhim API",
    version="0.2.0",
    description="Rimjhim playback URL resolution prototype",
)


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class PlaybackResponse(BaseModel):
    status: str
    videoId: str
    title: str | None = None
    audioUrl: str
    expiresAt: int | None = None
    contentType: str | None = None
    formatId: str | None = None
    durationSeconds: float | None = None


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "HEAD", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/", response_model=HealthResponse)
def root():
    return HealthResponse(
        status="ok",
        service="rimjhim-api",
        version=app.version,
    )


@app.get("/health", response_model=HealthResponse)
@app.head("/health")
def health():
    return HealthResponse(
        status="ok",
        service="rimjhim-api",
        version=app.version,
    )


@app.get("/api/v1/capabilities")
def capabilities():
    return {
        "service": "rimjhim-api",
        "stage": "playback-resolution-test",
        "audio_proxy": False,
        "persistent_storage": False,
        "features": [
            "health-check",
            "capability-check",
            "playback-url-resolution",
        ],
    }


def resolve_audio(video_id: str) -> dict:
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    options = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "skip_download": True,
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": 12,
        "retries": 1,
        "extractor_retries": 1,
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(video_url, download=False)

    if not info:
        raise ValueError("No media information returned.")

    audio_url = info.get("url")
    selected = info

    if not audio_url:
        formats = [
            item
            for item in info.get("formats", [])
            if item.get("url")
            and item.get("acodec") not in (None, "none")
            and item.get("vcodec") == "none"
        ]

        if not formats:
            raise ValueError("No audio-only format available.")

        selected = formats[-1]
        audio_url = selected["url"]

    parsed = urlparse(audio_url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("Invalid upstream audio URL.")

    expiry = parse_qs(parsed.query).get("expire", [])
    try:
        expires_at = int(expiry[0]) if expiry else None
    except (ValueError, TypeError):
        expires_at = None

    extension = selected.get("ext") or info.get("ext")
    content_types = {
        "m4a": "audio/mp4",
        "mp4": "audio/mp4",
        "webm": "audio/webm",
        "opus": "audio/ogg",
        "ogg": "audio/ogg",
        "mp3": "audio/mpeg",
    }

    return {
        "status": "ready",
        "videoId": video_id,
        "title": info.get("title"),
        "audioUrl": audio_url,
        "expiresAt": expires_at,
        "contentType": content_types.get(extension),
        "formatId": selected.get("format_id"),
        "durationSeconds": info.get("duration"),
    }


async def resolve_with_timeout(video_id: str) -> dict:
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(resolve_audio, video_id),
            timeout=25,
        )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail={
                "code": "RESOLUTION_TIMEOUT",
                "message": "Audio URL resolution timed out.",
            },
        )
    except yt_dlp.utils.DownloadError:
        raise HTTPException(
            status_code=502,
            detail={
                "code": "RESOLUTION_FAILED",
                "message": (
                    "Could not resolve audio. The video may be "
                    "unavailable, restricted, or unsupported."
                ),
            },
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "code": "NO_AUDIO_FORMAT",
                "message": str(exc),
            },
        )
    except Exception:
        raise HTTPException(
            status_code=502,
            detail={
                "code": "UPSTREAM_ERROR",
                "message": "Unexpected upstream resolution error.",
            },
        )


@app.get(
    "/api/v1/search",
    response_model=PlaybackResponse,
)
@app.get(
    "/api/v1/playback/resolve",
    response_model=PlaybackResponse,
)
async def playback_resolve(
    video_id: str = Query(
        ...,
        alias="videoId",
        min_length=11,
        max_length=11,
    ),
):
    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_VIDEO_ID",
                "message": "videoId must be an 11-character ID.",
            },
        )

    return await resolve_with_timeout(video_id)
