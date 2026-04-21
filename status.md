# Diagram Forge — Status

## Current State
- **Stage:** Develop
- **Last ticket:** Deploy (Railway + Vercel provisioned) — complete
- **Branch:** main
- **Latest commit:** cf2d1cd feat(web): add Railway + Vercel deploy config (WUI-06)

## Live URLs
- **Frontend:** https://diagram-forge.vercel.app
- **Backend:** https://api-production-0eac.up.railway.app

## Session Log
- 2026-02-28: Deploy complete — Railway backend (FastAPI) + Vercel frontend (Next.js), env vars set, CORS configured, e2e smoke test passed (OpenAI generation OK, Gemini free-tier quota hit)
- 2026-02-27: WUI-06 complete — Dockerfile dynamic PORT, CORS fail-closed, railway.toml, .dockerignore, standalone Next.js, DEPLOY.md
- 2026-02-27: WUI-05 complete — error/loading states polish across API proxies and UI
- 2026-02-27: WUI-04 complete — drop zone with drag-and-drop, /extract POST, auto-switch to paste tab
- 2026-02-27: WUI-03 complete — wired /generate to real diagram-forge providers, base64 image display
- 2026-02-27: WUI-02 complete — 15 files, Next.js 15 + React 19 + Tailwind v4, zero build errors

## Next Steps
- WUI-07+: TBD
