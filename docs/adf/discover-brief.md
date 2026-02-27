# Discover Brief — Diagram Forge Web UI

## Classification
`App · personal → community · mvp · standalone`

## Problem Statement

Diagram Forge's 13 professional diagram templates and AI generation pipeline are only accessible via MCP clients. Non-technical users — PMs, designers, executives, clients — are entirely excluded. The web UI removes that barrier: select a template, provide content, generate a diagram.

## Target Users

**Primary (v1):** Technical-adjacent users who have a Gemini or OpenAI API key but don't use MCP clients. Colleagues, collaborators, developers on non-MCP editors.

**Secondary (future):** Non-technical users once a hosted key option is added.

**Out of scope (v1):** End consumers with no API knowledge. That requires a hosted key and is a v2 decision.

## Core User Flow

```
1. Open app (no login required)
2. Select a template from the 13 available
3. Paste text/markdown OR upload a file (PDF, DOCX, MD)
4. Enter API key (Gemini or OpenAI) — stored in browser session only
5. Click Generate
6. View generated diagram
7. Regenerate (same prompt, new output) OR Download PNG
```

## Success Criteria

In priority order:
1. **Usability:** A non-technical teammate can produce a diagram with zero hand-holding
2. **Traction:** Someone outside the creator's network finds and uses it organically
3. **Demand signal:** At least one unsolicited request to pay for it

## MVP Scope

### In
- Template picker — all 13 templates with name, description, use case
- Content input — text/markdown paste + file upload (PDF, DOCX, MD)
- BYOK API key input — Gemini or OpenAI, stored in browser session only
- Generate → view → regenerate → download PNG
- Provider selection (Gemini / OpenAI) or auto
- Anonymous — no login required

### Out (v1)
- User accounts / authentication
- Diagram history or saved gallery
- Sharing / collaboration features
- Payment or billing
- Hosted API key (v2 when demand is validated)
- Style reference upload (v2)
- Edit/iterate on existing diagram (v2)

## Tech Stack

| Layer | Technology | Rationale |
|---|---|---|
| Frontend | Next.js (React) | User preference, Vercel-native |
| Frontend hosting | Vercel | Simple deploy, free tier |
| Backend API | FastAPI (Python) on Railway | Reuses diagram-forge Python code directly |
| Backend hosting | Railway | User has account, cheap, good Python support |
| Database | None (v1) | No persistence needed |
| Auth | None (v1) | Anonymous |

### Key Architecture Decision
The diagram-forge MCP server Python code is wrapped by a thin FastAPI layer on Railway. The Next.js frontend calls this API. No Python rewrite — the template engine, provider clients, and prompt logic are reused as-is.

API key is submitted by the user on each session and passed through to the backend. Never persisted server-side.

## Design Direction

**Aesthetic:** Linear × Zed IDE × Todoist — dark, minimal, high contrast, nothing loud or bright.

- Dark background (not pitch black — Zed-style dark gray)
- Minimal color — muted accent, not neon
- Clean typography, no visual clutter
- Diagrams are the hero — UI gets out of the way
- Professional and focused, not flashy

## Open Questions

| Question | Status | Notes |
|---|---|---|
| Repo structure — monorepo or separate repo? | Open | Monorepo (web/ subdir) vs. new repo `diagram-forge-web` |
| API key UX — where does user enter it? | Open | Settings panel, inline prompt, or per-generation modal |
| File upload text extraction — library choice | Open | PyMuPDF for PDF, python-docx for DOCX |
| Error UX — what happens on failed generation? | Open | Retry button, error message, or inline feedback |
| Railway API auth — how does Next.js authenticate to Railway API? | Open | Simple shared secret / env var for prototype |

## Constraints

- Prototype mindset — ship fast, validate, don't over-engineer
- Reuse diagram-forge Python code — no core logic rewrite
- BYOK only in v1 — no backend cost exposure
- Anonymous — no auth infrastructure in v1
- Budget: minimal — Railway free tier + Vercel free tier where possible

## Session State

- **Phase:** Crystallization complete
- **Last action:** Discover brief drafted from exploration session (2026-02-27)
- **Next step:** Review loop — Ralph Loop internal review, then external model review
- **Blockers:** None

## Revision History

| Date | Change |
|---|---|
| 2026-02-27 | Initial draft from exploration session |
