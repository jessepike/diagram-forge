# Diagram Forge — New Template Proposals

**Status:** Proposals for review. Authored by Forge for CTO/user review.
**Goal:** Expand template coverage at launch to demonstrate category breadth beyond pure architectural diagrams.
**Priority:** Ship 3-4 of these at launch (Phase 2.5); others in v1.1.

---

## Recommendation summary

| # | Template | Priority | Effort | Ship at launch? |
|---|----------|----------|--------|-----------------|
| 1 | `network_diagram` | P1 | 2h | ✅ Yes |
| 2 | `database_schema` | P1 | 2h | ✅ Yes |
| 3 | `state_machine` | P1 | 2h | ✅ Yes |
| 4 | `user_flow` | P2 | 2h | ✅ Recommended |
| 5 | `okr_tree` | P3 | 1.5h | Defer to v1.1 |
| 6 | `timeline` | P3 | 1h | Defer to v1.1 |
| 7 | `competitive_2x2` | P3 | 1.5h | Defer to v1.1 |

**Rationale for the 4 at launch:** Each hits a different audience (SRE, backend, distributed systems, product) and each addresses a real gap in existing tooling. Together they roughly double the effective "who is this for?" surface without diluting focus.

---

## 1. `network_diagram` (P1)

### Purpose
Generate L2/L3 and cloud network topologies: switches, VLANs, subnets, routers, firewalls, NAT, load balancers, VPCs.

### Audience
- SRE / network engineers / platform engineers
- Security teams (for network segmentation reviews)
- Cloud architects (VPC diagrams for AWS/GCP/Azure)
- Documentation writers (infra handoff docs)

### Market gap
- **Visio** is the industry default and is brutal — expensive, Windows-centric, manual every stencil
- **Lucidchart** has network templates but is expensive and requires manual layout
- **Draw.io** is fine but unopinionated and unguided
- **CloudMapper / AWS Network Visualizer** render live infra but aren't for design/docs
- **No AI-native option exists.** If your docs describe a network, no tool turns that into a diagram

### Design

**Colors:** Subnet groups get pastel fills to show segmentation. Traffic arrows color-coded: blue (internal), orange (egress), green (ingress).

**Iconography:** Stylized but recognizable — rectangles for switches/firewalls, cylinders for servers, clouds for external networks, rounded boxes for VPCs/subnets. Keep to simple shapes so the image model renders reliably (ornate Cisco-style icons are hard for image gen).

**Style defaults:**
```yaml
background: white
font: bold sans-serif
corners: rounded for groupings, sharp for devices
borders: dark gray (#555555)
aspect_ratio: "16:9"
```

**Color system:**
```yaml
description: "Subnet colors distinguish zones; traffic arrows show direction"
palette:
  public_zone: "#FFF3E0 (light orange, border #FB8C00)"
  private_zone: "#E3F2FD (light blue, border #1976D2)"
  dmz: "#FCE4EC (light pink, border #C2185B)"
  management: "#F3E5F5 (light purple, border #7B1FA2)"
  device: "#FFFFFF (white, border #424242)"
  internal_traffic: "#1976D2 (blue)"
  egress_traffic: "#E65100 (orange)"
  ingress_traffic: "#2E7D32 (green)"
```

**Template variables:**
- `subnets` — list of {name, cidr, zone_type, devices}
- `devices` — list of {name, type, ip, subnet}
- `connections` — list of {from, to, direction, label}
- `external_links` — list of {name, type} (internet, partner VPCs, etc.)

**Example prompt input:**
```
Network topology for a 3-tier web application:
- Public zone: ALB (10.0.1.10), WAF
- Private zone: 3 web servers (10.0.10.20-22), app tier (10.0.20.30-32)
- Data zone: RDS primary (10.0.30.40), read replica (10.0.30.41)
- Management: Bastion host (10.0.99.10)
- Ingress from internet to ALB only; ALB → web tier; web tier → app tier; app tier → RDS
```

**Known limitations:**
- Image models can't render CIDR notation perfectly reliably; provide explicit instructions in the template about legibility of IP addresses
- More than ~15 devices produces cramped layouts; recommend breaking into multiple diagrams (one per zone)

**Recommended quality:** `medium` — network diagrams need readability of labels but don't need full `high` tier

**Recommended provider:** `gemini` — Nano Banana Pro's text rendering handles IPs and device names reliably

---

## 2. `database_schema` (P1)

### Purpose
Entity-relationship diagrams: tables, columns, primary/foreign keys, cardinality, logical groupings.

### Audience
- Backend engineers (reading/writing schemas)
- Data engineers (warehouse modeling)
- DBAs
- Tech-forward PMs validating a feature's data model

### Market gap
- **dbdiagram.io** is the main option — requires manual DSL (DBML), no AI
- **Prisma / Drizzle** generate text ERDs but not visual
- **ERAlchemy / SchemaSpy** can render from live DBs but are ops tools, not design tools
- **Lucidchart** has ER templates but requires manual layout
- **No tool goes from "describe my data model" → beautiful ERD.** This is the gap.

### Design

**Colors:** Tables are grouped by logical domain (auth, billing, core, audit). Each domain gets an accent color. Primary keys bolded, foreign keys italicized. Relationship lines use crow's-foot notation.

**Style defaults:**
```yaml
background: white
font: monospace for column names, sans-serif for table names
corners: slightly rounded
borders: dark gray (#555555)
aspect_ratio: "16:9"
```

**Color system:**
```yaml
description: "Domain groupings get accent colors; keys distinguished by weight"
palette:
  auth_domain: "#1565C0 (blue accent)"
  billing_domain: "#2E7D32 (green accent)"
  core_domain: "#6A1B9A (purple accent)"
  audit_domain: "#616161 (gray accent)"
  table_header: "#F5F5F5 (light gray)"
  primary_key: "#D32F2F (red, bold)"
  foreign_key: "#F57C00 (orange)"
  relationship_line: "#424242 (dark gray)"
```

**Template variables:**
- `tables` — list of {name, domain, columns: [{name, type, pk, fk, nullable, index}]}
- `relationships` — list of {from_table, to_table, cardinality} (cardinality: "1:1" | "1:N" | "N:M")
- `domains` — optional named groupings

**Example prompt input:**
```
Schema for a simple SaaS app:
- Auth domain: users (id PK, email unique, created_at), sessions (id PK, user_id FK → users.id, token, expires_at)
- Billing domain: subscriptions (id PK, user_id FK → users.id, plan, status, renewal_at), invoices (id PK, subscription_id FK → subscriptions.id, amount, paid_at)
- Core domain: projects (id PK, owner_id FK → users.id, name), project_members (project_id FK → projects.id, user_id FK → users.id, role)
Relationships:
- users 1:N sessions
- users 1:N subscriptions
- users N:M projects via project_members
- subscriptions 1:N invoices
```

**Known limitations:**
- Large schemas (>15 tables) get cramped; recommend per-domain diagrams
- Image models may render column types imperfectly (VARCHAR(255) might become VARCHAR(256) — acceptable for docs, not for production schema reference)
- Use `high` quality for any schema intended as a reference artifact

**Recommended quality:** `high` — ERD legibility is critical; users will read cell-by-cell
**Recommended provider:** `openai` at high quality for text density, or `gemini` pro for faster iteration

---

## 3. `state_machine` (P1)

### Purpose
State machine / state transition diagrams: states, events, transitions, guards, entry/exit actions, initial and final states.

### Audience
- Backend engineers (order states, session states, workflow engines)
- UX engineers (multi-step wizards, form flows)
- Distributed systems engineers (protocol state machines)
- Anyone who has been burned by undocumented state logic

### Market gap
- **Mermaid** supports `stateDiagram-v2` but renders utilitarian, not presentation-quality
- **XState visualizer** is gorgeous but tied to XState ecosystem
- **Graphviz DOT** works but is aesthetically brutal
- **No general-purpose, beautiful state diagram tool exists.** Engineering teams hand-draw these on whiteboards because no tool is good enough.

### Design

**Colors:** State types get distinct fills. Start state = filled circle. End state = ring. Composite states = dashed border. Error/rejection states highlighted.

**Style defaults:**
```yaml
background: white
font: bold sans-serif for state names, regular for event labels
corners: rounded (15px+) for state rectangles
borders: solid for atomic states, dashed for composite
aspect_ratio: "16:9"
```

**Color system:**
```yaml
description: "State categories distinguished by fill color; transitions labeled with event/guard"
palette:
  initial_state: "#2E7D32 (green, filled circle)"
  final_state: "#424242 (dark gray, ring)"
  active_state: "#E3F2FD (light blue fill)"
  pending_state: "#FFF3E0 (light orange fill)"
  error_state: "#FFEBEE (light red fill, border #C62828)"
  composite_state: "#F3E5F5 (light purple, dashed border)"
  transition_label: "#1565C0 (blue italic)"
  guard_label: "#7B1FA2 (purple, bracketed)"
```

**Template variables:**
- `states` — list of {name, type: "initial" | "atomic" | "composite" | "final" | "error", parent?, entry_action?, exit_action?}
- `transitions` — list of {from, to, event, guard?, action?}
- `initial_state` — name of starting state

**Example prompt input:**
```
Order state machine for an e-commerce checkout:
- Initial: cart
- States: cart → pending_payment (on checkout) → paid (on payment_success) → shipped (on ship) → delivered (on delivery_confirmation)
- Error branches: pending_payment → failed_payment (on payment_error); failed_payment → cart (on retry)
- Cancellation: any of {cart, pending_payment, paid} → cancelled (on cancel)
- Final states: delivered, cancelled
```

**Known limitations:**
- Composite (nested) states are visually tricky; image models may flatten them unintentionally
- More than ~8 states with full transitions = visual spaghetti; recommend splitting into sub-state-machines

**Recommended quality:** `medium` — legibility of transition labels matters but not dense text
**Recommended provider:** `gemini` for clean flow layout, or `openai` for strong text rendering of event labels

---

## 4. `user_flow` (P2)

### Purpose
User flow diagrams: user actions, system responses, decision points, happy paths, error paths.

### Audience
- Product managers (communicating flows to engineering)
- UX designers (wireframing multi-step experiences)
- Support teams (documenting resolution paths)
- Founders explaining product to investors

### Market gap
- **Whimsical / Miro / FigJam** do this manually, no automation
- **Figma** has flow plugins but manual layout
- **Lucidchart** is again manual + expensive
- **Mermaid flowcharts** are utilitarian, not presentation-quality
- **No AI-native option** for "describe a user flow in prose → get a clean flow diagram"

### Design

**Colors:** Actors (user vs system vs external) have lane colors. Success paths green. Failure/error paths red. Decision diamonds use purple accent.

**Style defaults:**
```yaml
background: white
font: sans-serif regular for actions, bold for actors
corners: fully rounded for user actions, sharp for system, diamond for decisions
borders: subtle
aspect_ratio: "16:9"
```

**Color system:**
```yaml
description: "Actor lanes distinguished by color; path sentiment (success/failure) in arrow color"
palette:
  user_actor: "#E3F2FD (light blue lane)"
  system_actor: "#F5F5F5 (light gray lane)"
  external_actor: "#FFF3E0 (light orange lane)"
  action_node: "#FFFFFF (white, border #424242)"
  decision_node: "#F3E5F5 (light purple, diamond)"
  success_path: "#2E7D32 (green arrow)"
  failure_path: "#C62828 (red arrow)"
  normal_path: "#424242 (dark gray arrow)"
  outcome_success: "#E8F5E9 (light green fill)"
  outcome_failure: "#FFEBEE (light red fill)"
```

**Template variables:**
- `actors` — list of {name, type: "user" | "system" | "external"}
- `steps` — list of {id, actor, description, next: list of ids}
- `decisions` — list of {id, question, branches: {condition: next_id}}
- `outcomes` — list of {id, description, sentiment: "success" | "failure" | "neutral"}

**Example prompt input:**
```
User flow for sign-up + first login:
1. User visits landing page
2. User clicks "Sign up"
3. User enters email + password
4. System validates email format
   - Invalid → show error, back to step 3
   - Valid → continue
5. System sends verification email
6. User clicks verification link
7. System marks email verified
8. User redirected to onboarding
9. User completes 3-step onboarding (or skips)
10. User lands on dashboard (success)

Error path: if verification email not clicked within 24h, account is marked pending and user sees "resend verification" on next login attempt.
```

**Known limitations:**
- Flows with >12 steps become cramped; recommend splitting by phase
- Decision branches with >3 outputs look messy; image models handle 2-way branches best
- Swim lane layout (actors on left, flow left-to-right) works better than grid layout for readability

**Recommended quality:** `medium`
**Recommended provider:** `gemini` for clean flow rendering, or `openai` for text-heavy step descriptions

---

## Deferred (v1.1 or later)

### `okr_tree` (P3)
Tree structure: objective at top, key results branching, initiatives below each KR. Business/strategy audience. Status indicators (on track / at risk / off track) via color. Useful but not launch-critical.

### `timeline` (P3)
Horizontal timeline with phase markers, milestones, current-position indicator. Versatile (product timelines, project timelines, event timelines) but easily covered by existing product_roadmap template for most engineering use cases.

### `competitive_2x2` (P3)
Classic 2x2 grid with axes, quadrant labels, positioned points. Marketing/strategy artifact. Useful but narrow audience; lower launch impact.

---

## Implementation notes (for each template)

For every template, the implementation pattern is the same:

1. **Create YAML** at `src/diagram_forge/templates/{name}.yaml` following existing v2 template structure
2. **Add to `DiagramType` enum** in `models.py` (and to the `supports` list in `generate_diagram` docstring)
3. **Test one generation** per provider (Gemini 3 Pro, gpt-image-2 medium)
4. **Save best output** as a style reference in `src/diagram_forge/styles/{template}-baseline/`
5. **Add one test case** to `evals/benchmark_v1.yaml`
6. **Add gallery entry** at `docs/gallery/{template}/README.md` with 1-3 examples

Each template is ~2h when the content design (colors, variables, prompt structure) is decided. Most time is design iteration to make the generated output consistent.

---

## What this costs

Building all 4 launch templates:
- **Code/YAML effort:** 4 × 2h = 8h
- **Test generation cost:** 4 templates × 2 providers × 1 test = ~$0.30
- **Gallery generation cost:** 4 templates × 3 examples × medium quality = ~$0.50
- **Total:** 8h + <$1

Low enough that it shouldn't be the constraint on shipping.
