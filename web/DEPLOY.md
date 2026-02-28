# Diagram Forge Web UI — Deploy Reference

## Architecture

- **Backend:** FastAPI on Railway (Docker)
- **Frontend:** Next.js on Vercel

## Railway (Backend)

Railway auto-detects the Dockerfile via `railway.toml`.

### Environment Variables

| Variable | Required | Description |
|---|---|---|
| `RAILWAY_API_SECRET` | Yes | Shared secret for frontend → backend auth |
| `ALLOWED_ORIGINS` | Yes | Comma-separated allowed CORS origins (e.g. `https://your-app.vercel.app`) |
| `GEMINI_API_KEY` | Yes* | Google Gemini provider key |
| `OPENAI_API_KEY` | Yes* | OpenAI GPT Image provider key |
| `REPLICATE_API_TOKEN` | Yes* | Replicate Flux provider key |

*At least one provider key required.

### Health Check

`GET /health` — returns `{"status": "ok"}` (no auth required).

## Vercel (Frontend)

### Setup

1. Import repo in Vercel
2. Set **Root Directory** to `web/frontend`
3. Framework preset: **Next.js** (auto-detected)

### Environment Variables

| Variable | Required | Description |
|---|---|---|
| `RAILWAY_API_URL` | Yes | Railway backend URL (e.g. `https://your-app.up.railway.app`) |
| `RAILWAY_API_SECRET` | Yes | Must match the backend's `RAILWAY_API_SECRET` |

## Auth Flow

Frontend API routes (`/api/*`) proxy requests to Railway, injecting `X-API-Secret` header from the shared `RAILWAY_API_SECRET`. Provider API keys never leave the backend.
