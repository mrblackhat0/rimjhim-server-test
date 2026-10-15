# Rimjhim API

FastAPI backend for health checks and playback URL resolution testing.

## Run locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## Endpoints

- `GET /health`
- `GET /api/v1/capabilities`
- `GET /api/v1/search?videoId=YALvuUpY_b0`
- `GET /api/v1/playback/resolve?videoId=YALvuUpY_b0`
- `GET /docs`

## Test

```bash
curl "http://127.0.0.1:8000/api/v1/playback/resolve?videoId=YALvuUpY_b0"
```

A successful response includes `audioUrl`, a temporary upstream media URL.

Do not persist resolved URLs: they may expire. Resolve again when needed.

This prototype does not download or relay audio through the server.
Extraction can fail when the upstream source changes or restricts access.
A resolved URL is not proof that playback will work in every player or
network. Test actual playback, buffering, seeking, and background behavior.

Use only content and playback methods you are authorized to access.
This prototype is not production-ready and has no authentication or rate
limiting. Configure allowed origins and add abuse protection before public use.
