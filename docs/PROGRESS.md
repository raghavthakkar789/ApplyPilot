# Progress

## Current state

- **Date:** 2026-09-02 (Asia/Kolkata)
- **Phase:** Milestone 1 foundation in progress
- **Overall status:** Foundational documentation and the M1 design direction are
  owner-approved. The service scaffold, synthetic Discover slice, M1 owner
  authentication, structured profile, and verified-fact lifecycle foundations
  are implemented.
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
- Accepted D-023 and implemented M1 owner security: atomic singleton setup,
  Argon2id password authentication, hash-only opaque sessions, session-bound
  CSRF, persistent login backoff, logout/revocation, session inspection, and
  local-shell password recovery. The accepted Argon2id parameters benchmark at
  approximately 289 ms in the pinned API container.
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

## Current implementation

- Service-separated Next.js, FastAPI, worker, and PostgreSQL Compose scaffold
- D-022 Discover workspace using synthetic typed fixtures only
- Same-origin `/api` proxy and safe API live/ready health endpoints
- Alembic authentication migration with `installation`, `owner_account`,
  `sessions`, `session_csrf_tokens`, `login_rate_limits`, and `security_events`
- Accessible setup and login screens, protected Discover route, logout,
  five-minute expiry warning, and session inspection/revocation UI
- Lifecycle-only worker without a queue or U-016 mechanism
- Separate frontend, API, and worker test suites
- Forward candidate-record migration with singleton profile, stable fact
  identities, immutable version values, confirmations, lifecycle events,
  evidence, conflicts, and conflict membership
- Authenticated, CSRF-protected profile/fact/conflict routes with explicit
  verification, reconfirmation, revocation, and owner-only resolution
- Protected Profile and Evidence destinations with structured editing,
  provenance/history, lifecycle text, due dates, and deliberate dialogs

## Resume ingestion foundation (2026-09-02)

- Added Alembic revision `20260902_0003` for resume identities, immutable
  versions, stored-document digests, extractions, review candidates, and
  document lifecycle events.
- Added API-only protected local storage backed by the `document-data` named
  volume, deterministic PDF/DOCX/UTF-8 parsing under D-024, authorized
  downloads, duplicate detection, and trash/restore/deletion paths.
- Added authenticated resume and candidate-review APIs. Candidate acceptance
  produces only an unverified D-015 fact; explicit verification remains in
  Evidence.
- Added the responsive `/resumes` workspace with version history, warnings,
  extracted text, review candidates, distinct acceptance/verification messaging,
  and deletion confirmations.
- AI/LLM extraction, OCR, matching, asynchronous worker jobs,
  application generation, and external submission remain unimplemented.

## Secure configuration boundary (2026-09-02)

- Backend configuration now requires a validated database DSN held in a
  redacting secret type and reveals it only at SQLAlchemy/Alembic boundaries.
- Startup rejects malformed DSNs, insecure non-loopback Origin/cookie
  combinations, non-origin URLs, relative document roots, and production
  placeholder credentials.
- Added a repository security-boundary scan for committed environment files,
  frontend-public secret names, and prohibited owner/recovery/token fields.
- Login explains that passwords cannot be retrieved and points only to the
  local Fedora-shell reset command; no clickable recovery workflow exists.

## Approved job discovery foundation (2026-09-02)

- Added revision `20260902_0004` for reviewed ATS boards, synchronization runs,
  immutable raw payload versions, canonical versions, source links, manual
  records, and deduplication candidates.
- Implemented fixed-origin, public, read-only Greenhouse Job Board, Lever
  Postings, Ashby Public Job Posting, and Remotive adapters after checking
  official documentation on 2026-09-02.
- Manual URLs are stored but never fetched; manual provenance is visibly
  unverified. Remotive attribution and supplied links are preserved.
- Discover loads the authenticated catalog and labels matching `Not evaluated`;
  no matching calculation was introduced.
- Refresh is synchronous and bounded without a worker queue. Provider failure
  preserves valid data and remains distinct from closure.
- Exact application URLs link provenance to one canonical job. Deterministic
  normalized-key similarities create owner-reviewed deduplication candidates;
  merge/split decisions require a reason and retain source history. Two
  consecutive successful refresh misses are required before closure.

## Canonical lint runtime (2026-09-02)

- `make lint` no longer invokes `pnpm` in the production web runner. Frontend
  lint and typecheck run in Compose `web-test`; API lint remains on `api-test`;
  worker lint runs in `worker-test`.
- Production web, API, and worker images keep their runtime layers. The
  `test` profile still publishes no host ports.

## Not started

- Any source beyond the four D-018-approved public adapters
- Deployment beyond the local Compose runtime
- AI extraction, inferred signals, matching, application persistence/generation,
  and external submission

## Scaffold validation completed

- `git diff --check` passed.
- Frontend formatting, lint, strict TypeScript, 22 unit/accessibility tests,
  and production build pass.
- API Ruff, mypy, Alembic history/import, and application import pass. The API
  suite now has 67 passing tests, including
  the 20-request initialization race, expiry, CSRF, throttling, recovery, and
  redaction coverage, plus resume validation, extraction, storage, versioning,
  candidate-review, authorization, and deletion coverage.
- Frontend authentication, Discover, Profile, Evidence, and Resumes suites pass
  22 tests, including basic axe checks, lifecycle dialogs, CSRF mutation
  headers, and browser-storage safeguards.
- Worker Ruff, mypy, and its lifecycle test pass.
- Compose configuration confirms one default loopback host publication and no
  floating image tags. Container build, health, visual QA, and final repository
  checks are recorded in `design-qa.md` and the implementation commit report.

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

Complete the remaining M1 foundation controls, beginning with general and
expensive-operation request throttling plus initialization-attempt throttling.
Preserve all still-unresolved decisions; do not add an AI provider, external
submission, source scraping, public hosting, or a worker queue.
