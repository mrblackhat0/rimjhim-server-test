# Rimjhim API — smoke-test scaffold

This is a tiny FastAPI service for testing deployment and connectivity before adding source-specific music features.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Check:
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/api/v1/capabilities`
- `http://127.0.0.1:8000/docs`

## Deploy to Render

1. Push this folder to a GitHub repository.
2. In Render, choose **New → Blueprint** and connect that repository.
3. Render reads `render.yaml`; select the free plan if offered for the account.
4. After deployment, open `/health` and `/api/v1/capabilities`.

Free Render services sleep after inactivity and have ephemeral local storage. This prototype intentionally does not relay audio or store music files.

## Important

This is only a server connectivity smoke test. It does not yet implement search, audio extraction, streaming, or downloads. Those features must use sources and methods permitted for the intended use. Never put API secrets in the mobile app or commit them to Git.
