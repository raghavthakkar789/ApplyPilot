# Progress

## Current state

- **Date:** 2026-09-02 (Asia/Kolkata)
- **Phase:** Product Design handoff complete; M1 scaffolding is next
- **Overall status:** Foundational documentation and the M1 design direction are
  owner-approved. Application implementation has not started.
- **Technical blockers:** None.
- **Decision blockers:** The unresolved decisions in
  [Decisions](DECISIONS.md) block their identified future milestones.

## Unresolved-decision classification

No remaining unresolved decision blocks the M1 foundation.

- **Blocks a later named milestone:** U-002 (M7), U-004 (M6–M7), U-005
  (M5–M7), and U-011 (M7).
- **Requires external/provider-specific research:** U-003 (M7 destination
  integrations) and U-008 (M5 AI-provider boundary).
- **Deferred optional capability:** U-016, until a later milestone demonstrates
  a need for asynchronous work.

## Completed

- Initialized the Git repository.
- Accepted permanent single-owner scope and Fedora-local, loopback-only initial
  operation.
- Accepted authentication, Final Apply, verified-information, provenance,
  auditability, and third-party-control boundaries.
- Resolved U-015: Milestone 1 uses plain HTTP strictly on `127.0.0.1`, with
  strict Host/Origin allowlists and loopback-only cookie policy. Non-loopback
  operation requires HTTPS, `Secure=true`, and fail-closed validation.
- Resolved U-009: password recovery is a local-shell-only CLI operation with
  atomic credential replacement, all-session invalidation, redacted audit, and
  no web or remote recovery. Any separate confirmed TOTP-reset path is future
  behavior under D-013, not an M1 capability.
- Resolved U-014: Docker Compose is the sole supported and acceptance-tested M1
  runtime and canonical operational interface. Native Fedora execution is a
  debugging aid only; alternative deployment platforms remain deferred.
- Resolved U-013: M1 uses password-only application authentication and creates
  or exposes no TOTP/MFA material or capability. Future TOTP activation has an
  explicit security, migration, and testing gate.
- Resolved U-010: backups are versioned age-encrypted bundles stored outside
  live/repository data with fixed retention; restore is a confirmed local-shell
  Docker Compose operation with isolated validation, atomic database/document
  replacement, session revocation, and recurring drills.
- Resolved U-006: only explicit owner confirmation verifies immutable fact
  versions; reconfirmation, conflicts, inferred matching signals, sensitive
  answers, application snapshots, and approval invalidation now have binding
  lifecycle rules.
- Resolved U-012: India personal-use is the non-certifying legal-scope
  assumption; explicit retention, sensitive-data, trash, export, permanent
  deletion, tombstone, and restore-reapplication rules are accepted.
- Accepted D-017: job discovery is worldwide, with structured geographic and
  eligibility attributes, configurable owner preferences, separate match lanes,
  no India-only filter, and no immigration-eligibility determination.
- Resolved U-001 through D-018: M1 discovery is limited to read-only Greenhouse
  Job Board, Lever Postings, Ashby Public Job Posting, and Remotive Public Jobs
  APIs. ATS boards require an owner-reviewed finite registry; unsupported
  sources cannot be scraped; manual jobs remain visibly unverified; source
  provenance, attribution, isolation, and stricter terms are binding.
- Resolved U-007 through D-019: deterministic matching now has accepted
  capability/preference weights, coverage-adjusted ranking, separate eligibility
  and confidence outputs, evidence-bound blocker rules, immutable versioning,
  prohibited inputs, and measurable fairness tests.
- Resolved U-017 through D-020: M1 now has accepted opaque hashed sessions,
  host-only cookie settings, 60-minute idle/12-hour absolute expiry, a
  three-session cap, session-bound CSRF, persistent login backoff, request
  limits, revocation, and redacted auditing.
- Accepted D-021, amending D-010 and D-012: only Next.js publishes by default at
  `127.0.0.1:3000`; same-origin `/api` proxies to private-network FastAPI.
  Internal container `0.0.0.0` listeners are allowed, while non-loopback host
  publication remains prohibited.
- Accepted D-022 and [Design System](DESIGN_SYSTEM.md): the approved fourth
  concept now governs the M1 sidebar, editorial workspace, responsive
  master/detail layout, evidence-first matching UI, accessible states, and
  preparation-only action boundary. Mock identities, jobs, scores, dates, and
  eligibility claims remain synthetic rather than product data.
- Drafted the foundational documentation set:
  - [Repository instructions](../AGENTS.md)
  - [Product Requirements](PRODUCT_REQUIREMENTS.md)
  - [Architecture](ARCHITECTURE.md)
  - [Database Schema](DATABASE_SCHEMA.md)
  - [Security and Compliance](SECURITY_AND_COMPLIANCE.md)
  - [Development Roadmap](DEVELOPMENT_ROADMAP.md)
  - [Design System](DESIGN_SYSTEM.md)
  - [Decisions](DECISIONS.md)
  - this progress record

## Not started

- Application scaffolding or implementation
- Database migrations
- Dependency selection or installation
- Automated or manual application tests
- External-source integration
- Deployment beyond the empty repository

## Documentation validation completed

- `git diff --check` passed.
- `git status --short` reported only the new documentation files.
- A targeted scope search found prohibited concepts only in explicit
  prohibitions or deferred-capability statements.
- Cross-document review corrected a premature HTTP label in the architecture
  diagram and this progress record's pre-validation state.
- No application tests were run because no application code exists.

## Risks

- An integration may be designed before its source terms and authorization are
  approved.
- Verified-fact rules may be implemented without the required state-transition,
  inference-separation, conflict, or approval-invalidation tests.
- Local-only deployment may be mistaken for permission to reduce controls.
- Approval canonicalization or retry behavior may be implemented before its
  exact policy is accepted.
- Private documents, secrets, or logs may be placed inside the repository
  without enforced ignore and storage boundaries.

## Exact next recommended task

Scaffold the pinned Docker Compose modular monolith and implement the first
D-022 UI slice with synthetic typed data. Keep U-008 unresolved until M5; do not
add an AI provider, external submission, email sending, public hosting, or other
later-milestone behavior.
