"""FastAPI backend for Diagram Forge Web UI."""

from __future__ import annotations

import logging
import os

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from web.api.routers import extract, generate, templates

logger = logging.getLogger("diagram_forge_api")

app = FastAPI(title="Diagram Forge API", version="0.1.0")

# --- CORS ---

_allowed_origins = os.environ.get("ALLOWED_ORIGINS", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _allowed_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- API Secret dependency ---


def verify_api_secret(request: Request) -> None:
    """Validate X-API-Secret header against RAILWAY_API_SECRET env var."""
    expected = os.environ.get("RAILWAY_API_SECRET")
    if not expected:
        raise HTTPException(status_code=500, detail="RAILWAY_API_SECRET not configured")
    provided = request.headers.get("X-API-Secret")
    if provided != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing API secret")


# --- Exception handler ---


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> None:
    """Log unhandled exceptions, stripping api_key from request body."""
    body = {}
    try:
        body = await request.json()
    except Exception:
        pass
    sanitized = {k: v for k, v in body.items() if k != "api_key"} if isinstance(body, dict) else body
    logger.error("Unhandled exception on %s %s: %s | body=%s", request.method, request.url.path, exc, sanitized)
    raise HTTPException(status_code=500, detail="Internal server error")


# --- Health (no auth) ---


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


# --- Routers (auth required) ---

app.include_router(generate.router, dependencies=[Depends(verify_api_secret)])
app.include_router(templates.router, dependencies=[Depends(verify_api_secret)])
app.include_router(extract.router, dependencies=[Depends(verify_api_secret)])
