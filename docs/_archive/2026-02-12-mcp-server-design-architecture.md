---
type: "design"
parent: "./design.md"
section: "architecture"
version: "0.1"
updated: "2026-02-12"
---

# Design: Architecture

## System Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                        CORE PLATFORM                             │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │ Scheduler    │  │ Findings     │  │ Notification          │  │
│  │              │──│ Store        │──│ Router                │  │
│  │ (node-cron)  │  │ (SQLite)     │  │ (Slack/SMS/Push)      │  │
│  └──────┬───────┘  └──────┬───────┘  └───────────────────────┘  │
│         │                 │                                      │
│  ┌──────┴───────┐  ┌──────┴───────┐                              │
│  │ Monitoring   │  │Classification│                              │
│  │ Jobs         │  │ Engine       │                              │
│  │ (claude -p)  │  │ (YAML rules) │                              │
│  └──────────────┘  └──────────────┘                              │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│                      EXPOSURE LAYER                              │
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────────────────────────┐  │
│  │ MCP Server       │  │ API Server (Fastify)                 │  │
│  │ (stdio → REST)   │  │ REST + WebSocket (interface access)  │  │
│  └──────────────────┘  └──────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
         │                          │
         │ MCP tools                │ REST/WS
         ▼                          ▼
┌──────────────┐          ┌──────────────┐  ┌──────────────┐
│ Krypton      │          │ iOS App      │  │ Desktop App  │
│ + agents     │          │ (SwiftUI)    │  │ (Next.js)    │
└──────────────┘          └──────────────┘  └──────────────┘
```

## Component Design

### Monitoring Jobs

Background processes that observe system state and produce structured findings. Each job is a `claude -p` call with a focused prompt and MCP tool access. Jobs are stateless — read current state, produce findings, exit.

**Execution model:** `claude -p` on Max subscription (zero marginal cost). Each job runs as a separate process for failure isolation. The prompt defines what to observe, what constitutes a finding, and the output schema.

**Pre-flight DLP sanitization:** Before assembling job prompts, source data (status.md content, git diffs, hook logs) is scanned for known secret patterns using regex matchers (API keys, JWTs, private keys, passwords, connection strings, bearer tokens). Matches are replaced with `[REDACTED]` before inclusion in the prompt. The sanitizer is a shared module (`packages/core/src/dlp/sanitizer.ts`) used by the scheduler before every job invocation. Findings produced by jobs are also scanned on write — any finding that contains a secret pattern is rejected and a BLUE meta-finding is created ("finding rejected: potential secret in output").

**Job prompt pattern:**

```
You are a monitoring job for the Nerve Center. Your task: {job_description}.

Read the following data sources: {data_sources}

For each issue found, produce a finding in this JSON schema:
{finding_schema}

Rules:
- Only report genuine issues, not normal states
- Include concrete evidence (timestamps, file paths, values)
- Never include secrets or credentials in findings
- If no issues found, return empty findings array
```

#### Job Specifications

| Job | Purpose | Data Sources | Frequency | Tier |
|-----|---------|-------------|-----------|------|
| **Governance Sentinel** | Rule violations, unauthorized actions, secret exposure | Hook logs, git diffs, audit trail | Every 1h (D8: sweep-only for v1) | RED |
| **Drift Detector** | Stalled projects, divergence from plan | status.md files, BACKLOG.md, git log | Every 4h | YELLOW |
| **Priority Alignment** | Agent activity vs stated priorities | Recent commits, BACKLOG.md rankings | Daily | YELLOW |
| **Health Prober** | MCP server connectivity, data source accessibility | MCP tool calls (ping), file existence | Every 30min | BLUE |
| **Quality Tracker** | Validator scores, test pass rates | Validation reports, test outputs, KB stats | Daily | BLUE/YELLOW |
| **Knowledge Auditor** | Stale entries, duplicates, synthesis opportunities | KB MCP (search, stats), Memory MCP | Weekly | GREEN |
| **Autonomy Assessor** | Human/agent ratios vs targets | Decision logs, session logs, intervention frequency | Weekly | GREEN |

#### Data Sources (Existing — No New Pipelines)

| Source | Format | Location | Read By |
|--------|--------|----------|---------|
| Project status | Markdown | `*/status.md` | Drift Detector, Priority Alignment |
| Backlogs | Markdown | `*/BACKLOG.md` | Priority Alignment, Drift Detector |
| KB data | SQLite + Chroma | `knowledge-base/data/` | Knowledge Auditor, Quality Tracker |
| Memory data | SQLite + Chroma | `memory/data/` | Knowledge Auditor |
| ADF health | MCP tools (live) | adf-server | Health Prober, Drift Detector |
| KB stats | MCP tools (live) | kb-server | Knowledge Auditor |
| Memory stats | MCP tools (live) | memory-server | Knowledge Auditor |
| Git activity | Git log | Each project repo | Drift Detector |
| Hook logs | File | `.claude/` hook outputs | Governance Sentinel |

### Classification Engine

Determines finding tier based on configurable rules. Sits between monitoring jobs and the findings store — jobs may suggest a tier, but the classification engine has final say.

**Implementation:** YAML configuration file evaluated in order. First matching rule wins. Default fallback to BLUE.

```yaml
# ~/.nerve-center/classification.yaml
rules:
  # RED — Safety & Governance
  - match:
      category: ["secret_exposure", "unauthorized_action", "governance_violation"]
    tier: RED
    halt_recommended: true  # NC emits recommendation; enforcement is out of NC scope

  - match:
      category: "stage_bypass"
    tier: RED

  # YELLOW — Drift & Alignment
  - match:
      category: "drift"
      details.days_stalled: { gte: 7 }
    tier: YELLOW

  - match:
      category: ["priority_misalignment", "quality_degradation"]
    tier: YELLOW

  # BLUE — Health & Performance
  - match:
      category: ["mcp_health", "data_freshness", "sync_error"]
    tier: BLUE

  # GREEN — Optimization
  - match:
      category: ["improvement", "synthesis_opportunity", "autonomy_recommendation"]
    tier: GREEN

  # Default
  - default:
      tier: BLUE
```

**Rule evaluation:** The engine loads rules at startup and reloads on file change. Each finding is evaluated against rules in order. The `match` object supports exact match (string/array) and comparison operators (`gte`, `lte`, `gt`, `lt`) for numeric fields. Nested fields use dot notation.

### Notification Router

Dispatches findings to appropriate channels based on tier. Enforces notification content safety — only metadata and summaries, never raw data.

**Channels:**

| Channel | Technology | Tiers | Purpose |
|---------|-----------|-------|---------|
| SMS/Telegram | Twilio or Telegram Bot API | RED | Get-my-attention. Breaks through everything. |
| Slack | Slack webhook | RED, YELLOW | Async feed. Tier-appropriate channels. |
| Push | APNs via iOS app | RED, YELLOW | Mobile alerts. Critical can break DND. Requires Apple Developer Account, APNs key, and device token registration (Phase 3). |
| Digest | Generated summary | BLUE, GREEN | Batched — daily (BLUE), weekly (GREEN). |

**Routing configuration:**

```yaml
# ~/.nerve-center/routing.yaml
routing:
  RED:
    - channel: sms
    - channel: slack
      target: "#nerve-center-critical"
    - channel: push
      priority: critical
      interrupt: true  # breaks through DND

  YELLOW:
    - channel: slack
      target: "#nerve-center-alerts"
    - channel: push
      priority: normal

  BLUE:
    - channel: digest
      schedule: daily

  GREEN:
    - channel: digest
      schedule: weekly
```

**Content safety:** The router receives a finding and produces a notification payload. The payload contains: tier, title, summary, timestamp, finding ID. It never includes `details`, `recommended_actions`, or any field that could contain sensitive data. The full finding is available via the API/MCP server — the notification is a pointer, not the content.

**Deduplication and rate-limiting:**
- **Dedup window:** If a finding with the same `job_id + category + project` was already notified within the last 60 minutes, suppress the duplicate notification. The finding is still stored — only the notification is suppressed.
- **Rate limit:** Max 10 notifications per channel per hour (configurable). Excess notifications are queued and delivered in the next window.
- **RED tier bypass:** RED-tier notifications are never suppressed or rate-limited. They always deliver immediately.
- **Escalation:** If a YELLOW finding remains `open` for 4+ hours after initial notification, re-notify once as a reminder.

### Scheduler

Orchestrates monitoring job execution. Manages job lifecycle, tracks runs, handles failures.

**Implementation:** Node.js process using `node-cron` for scheduling. Single long-running process.

**Responsibilities:**
- Execute jobs on schedule per configuration
- Track job runs in the findings store (job_runs table)
- Write job output (findings) to the findings store
- Run findings through classification engine
- Trigger notification router for classified findings
- Handle job failures (log error, retry once, then alert)
- Expose job status via API

**Concurrency control:**
- **Max concurrent jobs:** 2 (configurable). Jobs are queued if limit is reached.
- **Job queue:** FIFO with priority — RED-tier jobs (Governance Sentinel) jump the queue.
- **Timeout enforcement:** Each job spawns a child process (`child_process.spawn`). If the process exceeds its configured timeout, it is killed (`SIGTERM`, then `SIGKILL` after 5s). The job_run record is marked `failed` with timeout error.
- **Timed-out job findings:** Partial output is discarded. Incomplete findings are unreliable. A BLUE finding is created: "Job {job_id} timed out after {timeout}ms."
- **Retry policy:** On failure (including timeout), retry once with the same timeout. On second failure, create a BLUE finding and skip until next scheduled run.

**Schedule configuration:**

```yaml
# ~/.nerve-center/jobs.yaml
jobs:
  health-prober:
    schedule: "*/30 * * * *"  # every 30 minutes
    timeout: 60000  # 1 minute
    prompt: "prompts/health-prober.md"

  drift-detector:
    schedule: "0 */4 * * *"  # every 4 hours
    timeout: 120000  # 2 minutes
    prompt: "prompts/drift-detector.md"

  priority-alignment:
    schedule: "0 8 * * *"  # daily at 8am
    timeout: 180000  # 3 minutes
    prompt: "prompts/priority-alignment.md"

  quality-tracker:
    schedule: "0 9 * * *"  # daily at 9am
    timeout: 180000
    prompt: "prompts/quality-tracker.md"

  governance-sentinel:
    schedule: "0 * * * *"  # hourly sweep
    timeout: 120000
    prompt: "prompts/governance-sentinel.md"

  knowledge-auditor:
    schedule: "0 8 * * 1"  # weekly Monday 8am
    timeout: 300000  # 5 minutes
    prompt: "prompts/knowledge-auditor.md"

  autonomy-assessor:
    schedule: "0 8 * * 1"  # weekly Monday 8am
    timeout: 300000
    prompt: "prompts/autonomy-assessor.md"
```

**Job execution flow:**

```
Schedule triggers → Create job_run record (status: running)
  → Spawn `claude -p` with job prompt + MCP permissions
  → Parse JSON output
  → Run each finding through classification engine
  → Write findings to store
  → Trigger notification router per tier
  → Update job_run record (status: completed, findings_count, duration)
  → On failure: log error, retry once, then create BLUE finding for job failure
```

**Startup reconciliation:** On scheduler start, scan `job_runs` for entries with `status = 'running'` older than their configured timeout + 60s grace period. Mark them `failed` with error "scheduler restart — job orphaned". This handles crashes, reboots, and unclean shutdowns without manual intervention.

**LLM unavailability:** If `claude -p` fails to launch or returns a non-zero exit code indicating service unavailability, the scheduler skips the run, logs a BLUE finding ("job skipped: LLM unavailable"), and retries at the next scheduled interval.

## Deployment Model

All components run locally on the development machine:

- **Scheduler process:** Long-running Node.js process (managed via launchd on macOS)
- **API server:** Long-running Node.js process (same or separate from scheduler)
- **MCP server:** Stdio-based, launched by clients as needed
- **Findings store:** SQLite file at `~/.nerve-center/data/findings.db`
- **Configuration:** YAML files at `~/.nerve-center/config/`
- **Job prompts:** Markdown files at `~/.nerve-center/prompts/`
- **Logs:** `~/.nerve-center/logs/`

**Directory structure:**

```
~/.nerve-center/
├── config/
│   ├── classification.yaml
│   ├── routing.yaml
│   └── jobs.yaml
├── data/
│   └── findings.db
├── prompts/
│   ├── drift-detector.md
│   ├── governance-sentinel.md
│   ├── health-prober.md
│   ├── priority-alignment.md
│   ├── quality-tracker.md
│   ├── knowledge-auditor.md
│   └── autonomy-assessor.md
├── logs/
│   ├── scheduler.log
│   └── api.log
└── nerve-center.plist  # launchd config
```

## Proactive Intelligence Features

These features are built into the core platform, consumed by Krypton and interfaces:

- **Confidence decay** — derived from decisions and findings data. For each project, the system tracks the most recent decision timestamp as a proxy for "last human verified." If no decision has been made for a project in 14+ days and findings exist, a GREEN "confidence decay" finding is produced by the Autonomy Assessor job. No separate schema needed — this is a query pattern over existing tables (`SELECT MAX(d.timestamp) FROM decisions d JOIN findings f ON d.finding_id = f.id WHERE f.project = ?`).
- **Decision quality feedback** — decisions table has `outcome` and `outcome_quality` fields. Tracked over time to surface patterns in decision quality.
- **"All clear" confirmation** — produced daily (8 AM, after morning jobs complete). The scheduler checks the most recent run of every job — if all have zero findings, a GREEN "all clear" finding is created. If any job has not run in its expected window, no "all clear" is produced (absence of data is not absence of issues).
- **Digest generation** — the scheduler generates digests on schedule (daily at 6 PM for BLUE, weekly Monday 9 AM for GREEN). Generation is template-based (not agentic): query findings by tier and period, group by category and project, format into a structured summary with counts and top items. Stored in the digests table. Delivered via configured channels (Slack digest channel, push summary). The scheduler is responsible for both generation and delivery scheduling.
