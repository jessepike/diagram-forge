---
type: "brief"
project: "Diagram Forge Web UI"
version: "0.2"
status: "in-review"
review_cycle: 2
created: "2026-02-27"
updated: "2026-02-27"
intent_ref: "./intent.md"
---

# Brief: Diagram Forge Web UI

## Classification

- **Type:** App
- **Scale:** personal (v1) → community (post-validation)
- **Scope:** mvp
- **Complexity:** multi-component (Next.js frontend + Python API backend)

## Summary

Diagram Forge's 13 professional diagram templates are only accessible via MCP clients, excluding most potential users. This project builds a web application that exposes the same generation capability through a browser UI — users select a template, provide content (text or file), enter their own API key, and download the result. See `intent.md` for the North Star. The v1 prototype validates usability and demand before committing to a hosted-key model that would open access to fully non-technical users.

## Scope

### In Scope
- Template picker — all 13 templates with name, description, and use case
- Content input — text/markdown paste and file upload (PDF, DOCX, MD)
- BYOK API key entry — Gemini or OpenAI, stored in browser session only, never persisted server-side
- Provider selection — Gemini, OpenAI, or auto
- Generate → view → regenerate → download PNG
- Anonymous use — no login required

### Out of Scope (v1)
- User accounts / authentication — adds complexity, not needed to validate core UX
- Diagram history or saved gallery — no persistence in v1
- Sharing / collaboration — v2 when demand is validated
- Payment or billing — v2 when demand signal is confirmed
- Hosted API key — v2; requires rate limiting and cost management infrastructure
- Style reference upload — v2
- Edit/iterate on existing diagram — v2

## Success Criteria

- [ ] A non-technical colleague uses the app to produce a usable diagram without any instructions from me
- [ ] At least 3 people outside my immediate network discover and use the app within 30 days of launch
- [ ] At least 1 person asks unprompted whether they can pay for it or get more usage

## Constraints

- Prototype mindset — validate demand before investing in production infrastructure
- BYOK only in v1 — no backend API cost exposure until demand is confirmed
- Reuse existing diagram-forge Python code — no rewrite of core template or provider logic
- Anonymous in v1 — no auth infrastructure
- Deploy targets: Vercel (frontend) and Railway (Python API backend)
- Budget: free tiers where possible; Railway ~$5/month acceptable for prototype

## Technical Preferences

*Preferences captured in Discover to inform Design. Architecture decisions made in Design.*

- **Frontend:** Next.js (React) — user preference, Vercel-native
- **Backend:** Thin Python API wrapping existing diagram-forge code — preserves all existing logic
- **Deployment:** Vercel (frontend) + Railway (backend API)
- **No database in v1** — stateless, no persistence needed

*Key architecture question deferred to Design: how the Next.js frontend authenticates to the Railway API (shared secret is acceptable for prototype).*

## Open Questions

| Question | Priority | Notes |
|---|---|---|
| Monorepo vs. separate repo (`diagram-forge-web`)? | High | Impacts project structure — decide before Design begins |
| API key UX — where does user enter it? | Medium | Settings panel, inline prompt, or per-generation modal |
| File upload text extraction — library choice | Medium | PyMuPDF for PDF, python-docx for DOCX — confirm in Design |
| Error UX — what happens on failed generation? | Medium | Retry, error message, or inline feedback |

## Decision Log

| Decision | Options Considered | Chosen | Rationale | Date |
|---|---|---|---|---|
| API key model | BYOK / hosted key / hybrid | BYOK first | Zero cost risk for prototype; validates demand before investment | 2026-02-27 |
| Backend runtime | TypeScript port / Python on Railway / Vercel Python runtime | Python on Railway | Reuses existing code; Railway is simple; no rewrite risk | 2026-02-27 |
| Frontend stack | Next.js / SvelteKit | Next.js | User preference, Vercel-native, largest ecosystem | 2026-02-27 |
| Auth in v1 | Auth required / anonymous | Anonymous | Reduces complexity; BYOK acts as a natural access filter | 2026-02-27 |

## Issue Log

| # | Issue | Source | Severity | Status | Resolution |
|---|---|---|---|---|---|
| 1 | Missing YAML frontmatter | Ralph-Internal | Critical | Resolved | Added frontmatter with status, version, review_cycle |
| 2 | Missing Summary section | Ralph-Internal | Critical | Resolved | Added Summary section |
| 3 | Missing Issue Log section | Ralph-Internal | Critical | Resolved | Added this section |
| 4 | Success criteria 2 & 3 not measurable | Ralph-Internal | Critical | Resolved | Added "3 users in 30 days" and "1 unprompted pay request" thresholds |
| 5 | BYOK/non-technical tension not acknowledged | Ralph-Internal | High | Resolved | Added to Summary: v1 validates UX before hosting; BYOK is intentional prototype filter |
| 6 | Tech stack too detailed for Discover | Ralph-Internal | High | Resolved | Replaced with "Technical Preferences" section, noted as Design inputs |
| 7 | Session State embedded in Brief | Ralph-Internal | High | Resolved | Removed; session state tracked in status.md only |
| 8 | Classification format non-standard | Ralph-Internal | High | Resolved | Reformatted to spec-compliant structured fields |
| 9 | Missing Decision Log | Ralph-Internal | Low | Resolved | Added Decision Log with 4 key decisions from exploration |
| 10 | "personal → community" notation ambiguous | Ralph-Internal | Low | Resolved | Clarified as "(v1) → community (post-validation)" |
| 11 | Success criterion #1 assumes user can obtain an API key — non-trivial for non-technical users | Ralph-Internal | Low | Deferred | Acknowledged as prototype constraint; BYOK is intentional v1 filter |

## Review Log

### Phase 1: Internal Review

**Date:** 2026-02-27
**Mechanism:** Manual (Ralph Loop unavailable — script error)
**Cycle:** 1
**Issues Found:** 4 Critical, 4 High, 2 Low
**Actions Taken:**
- Auto-fixed (10 issues): All Critical and High issues resolved in this cycle; Low issues also resolved
**Outcome:** All Critical and High issues resolved. Proceeding to Cycle 2.

### Cycle 2

**Date:** 2026-02-27
**Issues Found:** 0 Critical, 0 High, 1 Low
**Actions Taken:**
- Logged only (1 issue): Issue #11 — API key acquisition assumption (Low) — deferred with rationale
**Outcome:** Exit criteria met. Ready for Phase 2 (external review).

## Revision History

| Version | Date | Changes |
|---|---|---|
| 0.1 | 2026-02-27 | Initial draft from exploration session |
| 0.2 | 2026-02-27 | Cycle 1 review — added frontmatter, Summary, Issue Log, Decision Log; sharpened success criteria; fixed classification; removed session state; scoped tech stack to preferences |
