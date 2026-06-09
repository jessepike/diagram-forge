# Spec: Railway → Vercel backend migration (single-platform consolidation)

**Author:** CTO · **Date:** 2026-06-03 · **Status:** Ready for operator
**Supersedes:** launch-plan §1.1 (Edge-TS proxy) — amended, see Decision below
**Owner action required:** Vercel dashboard changes (§5) gate the deploy — operator does code only.

---

## 1. Why

The live demo `diagram-forge.vercel.app` shows **"Could not load templates. Check that the backend is running."** Root cause: the Vercel frontend proxies to a **Railway backend** (`api-production-0eac.up.railway.app`) that has **no active deployment** — a casualty of the planned (but never completed) Railway retirement. The frontend's `/api/templates` route returns HTTP 404 `{"error":"Failed to fetch templates"}` (the `!res.ok` branch — the fetch reached Railway's "Application not found" edge), confirming the backend is gone, not the wiring.

**Goal:** consolidate to Vercel-only. Move the backend onto the same Vercel project, kill Railway.

## 2. Decision (amends launch-plan §1.1)

Launch-plan §1.1 chose a **thin TS Edge Function proxy**. That decision is **reversed** — it doesn't survive the actual backend:

- `/generate` runs `diagram_forge.template_engine.build_prompt` (the core IP — templates + design tokens + theme). Edge-TS would require **porting the engine to TypeScript**, forking the highest-churn code into permanent dual maintenance.
- `/extract` uses **PyMuPDF (`fitz`, a C extension)** — **cannot run in the Edge runtime at all.**
- `/generate` can take ~60s — beyond Edge limits.

**Chosen: Option A — deploy the existing FastAPI backend as a Python function on Vercel.** One engine, no fork, keeps `/extract`, supports 60s+ generate, BYOK stays stateless. Smallest diff: it's the same Python, Railway→Vercel.

**BYOK is already implemented** (frontend keeps the user's key in `sessionStorage` `df_api_key` and sends `api_key` in the generate body; the dead `X-API-Secret` was a separate cross-origin abuse-gate, now unnecessary). This is a **lift-and-shift**, not a BYOK build.

## 3. Target architecture

**Primary: Vercel Services** (`experimentalServices`) — the 2026-canonical polyglot-monorepo pattern. Two services on one project/domain:
- `web` → Next.js frontend (`web/frontend`, `routePrefix: "/"`)
- `api` → FastAPI backend (`web/api/main.py`, `routePrefix: "/server"`, `maxDuration: 120`, Fluid Compute)

Browser calls `/server/templates|generate|extract` same-origin (no CORS). The monorepo-install problem (core lives at repo-root `src/`, Next builds from `web/frontend`) is solved by setting Vercel **Root Directory = repo root** and bundling `src/**` + `config/**` into the api function via `includeFiles`.

**Fallback (if Services beta is not enabled on `pikeholdings` org, or the spike isn't green in one cycle): stable single-function + rewrites.** Keep framework = Next.js, Root Directory = repo root, add `api/index.py` exposing the FastAPI `app`, and `vercel.json` `rewrites` mapping `/server/(.*)` → the function. Everything else (requirements, includeFiles, Python pin, route-prefix handling, deleting TS proxies) is identical. **The spike decides which.**

## 4. Operator tasks (code only — DO NOT deploy; owner gates deploy per §5)

**Task 0 — Spike first (decides Services vs fallback). Smallest proof before porting anything:**
1. Confirm whether `experimentalServices` is enabled on the `pikeholdings` org (ask owner / check a throwaway preview).
2. Stand up a stub `api` service/function with `/server/health` that does `from diagram_forge.template_engine import load_all_templates; return {"count": len(load_all_templates())}` AND opens `config/design_tokens.yaml`. Deploy to **preview only**.
3. Green = the monorepo install (`.` in requirements under Vercel's `uv`+pyproject build) AND runtime `config/` access both work. This is the single highest-risk step — prove it before the full port.
4. Confirm path-prefix behavior: does the FastAPI app receive `/server/generate` or `/generate`? Set route prefixing accordingly (mount routers under `/server`, or `FastAPI(root_path="/server")` — whichever the spike shows Vercel's mount expects).

**Task 1 — `vercel.json` at repo root** (Services primary; see deployment-expert recommendation for exact shape): two services, `includeFiles: "{src/**,config/**}"`, `excludeFiles` for `tests/ evals/ .venv/ data/ diagram-forge-plugin/` if bundle creeps (500MB uncompressed cap).

**Task 2 — `web/api/requirements.txt`:** replace `diagram-forge @ file:../../` with a plain `.` (installs the repo-root package under uv); drop `uvicorn` from deployed deps (keep for local `vercel dev`). Add the core's runtime deps explicitly (pydantic, pyyaml, httpx, google-genai, openai, Pillow, python-dotenv) since the function installs the package, not the dev env.

**Task 3 — Python pin:** add `/.python-version` = `3.13` (guarantees a PyMuPDF manylinux wheel; avoids an sdist build).

**Task 4 — Route prefixing:** make the FastAPI routers serve under `/server` per the Task-0 finding. Verify `web/api/main.py`'s `from web.api.routers import ...` import resolves from the Vercel entrypoint (may need `web/__init__.py`, `web/api/__init__.py`, or a PYTHONPATH/`root_path` adjustment — confirm in spike).

**Task 5 — Re-point frontend:** delete the 3 TS proxies (`web/frontend/src/app/api/{templates,generate,extract}/route.ts`); change the frontend fetches in `page.tsx` / `LeftPanel.tsx` from `/api/*` to `/server/*` (or the injected `NEXT_PUBLIC_API_URL`). Keep the `df_api_key` BYOK flow exactly as-is.

**Task 6 — Decommission Railway artifacts:** delete `railway.toml` and `web/api/Dockerfile` (dead post-migration). Leave a one-line note in `status.md`.

**Task 7 — Verify no key logging:** confirm the 3 routers + `main.py`'s exception handler never log the request body's `api_key` (the handler already strips `api_key` — keep it). BYOK keys must never hit logs.

## 5. Owner-gated actions (Vercel dashboard — operator cannot do these)

| Action | Detail |
|---|---|
| Framework preset | → **Services** (primary) or keep **Next.js** (fallback) |
| Root Directory | `web/frontend` → **repo root** (blank) — required so the Python build sees `src/` + `config/` |
| Plan tier | Confirm **Pro** (needed for `maxDuration: 120` / Fluid extended duration) |
| Services beta | Confirm enabled on `pikeholdings` org (gates the primary path) |
| Env vars | **Delete** `RAILWAY_API_URL` + `RAILWAY_API_SECRET` |
| Re-link | `vercel link` after framework/root change; first deploy from new config |
| Railway | Stop/delete the `api-production-0eac` service; revoke its env-var token (carry-forward backlog item) |

## 6. Acceptance criteria

- [ ] Spike green: `diagram_forge` imports + `config/*.yaml` opens in the deployed function.
- [ ] `GET /server/templates` returns the template list (frontend "Could not load templates" gone).
- [ ] `POST /server/generate` with a real BYOK key returns a base64 image (≤3MB cap honored), within `maxDuration`.
- [ ] `POST /server/extract` parses a PDF and a DOCX (PyMuPDF + python-docx working on Vercel).
- [ ] No Railway dependency remains (env vars deleted, `railway.toml` + Dockerfile removed, service stopped).
- [ ] No `api_key` in any function log.
- [ ] Bundle < 500MB uncompressed (check first build log).

## 7. Risks (operator must verify, do not assume)

1. `experimentalServices` beta enablement on org — if absent, take the fallback. **(spike Task 0)**
2. Path-prefix footgun: confirm whether the app receives the `/server` prefix. **(spike Task 0)**
3. uv + local-package (`.`) resolution under Vercel's Python build — the highest-risk step. **(spike Task 0)**
4. Runtime `config/**` access (root-relative `open()` paths in the core). **(spike Task 0)**
5. PyMuPDF wheel on the pinned Python — mitigated by `.python-version = 3.13`.
6. Cold start on `/extract` (PyMuPDF import) — acceptable for this workload; do not over-engineer.

## 8. Out of scope (backlog, do not build here)

- BYOK demo polish, gallery, privacy-notice copy (launch-plan Phase 3 — separate).
- OSS-launch repo hygiene (B22), PyPI publish (would simplify the `.` install later but not required now).
- Streaming the generate response (nice-to-have; flagged by deployment-expert, not required for parity).
