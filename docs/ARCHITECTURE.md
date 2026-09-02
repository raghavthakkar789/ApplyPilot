# Architecture

## 1. Status and constraints

**Accepted decision:** ApplyPilot is a permanently single-owner system deployed
in Milestone 1 only through Docker Compose on one Fedora computer and reachable
only through loopback. PostgreSQL is the system of record. The UI uses Next.js with
TypeScript; the API and domain enforcement use Python with FastAPI.

This architecture implements the requirements in
[Product Requirements](PRODUCT_REQUIREMENTS.md) and the controls in
[Security and Compliance](SECURITY_AND_COMPLIANCE.md).

## 2. MVP component model

```text
Owner browser on Fedora
        | loopback HTTP: 127.0.0.1:3000
        v
Next.js web component -- same-origin /api proxy --> FastAPI application
                                                      | private Docker network
                                                      +---- PostgreSQL
                                                      +---- protected local storage
                                                      +---- worker process
                                                      +---- approved adapters
```

### Responsibilities

- **Next.js:** rendering, interaction, and same-origin `/api` proxying to
  FastAPI. It does not independently authorize submissions or decide whether
  facts are verified.
- **FastAPI:** authentication, validation, domain rules, source adapters,
  scoring orchestration, generation controls, approval verification, and audit
  writes.
- **PostgreSQL:** authoritative structured state, transactional invariants,
  versions, approvals, attempts, and audit data.
- **Protected local storage:** recommended MVP default for resumes and generated
  documents. PostgreSQL stores identifiers, digests, metadata, and paths; paths
  are never accepted directly from requests.
- **Worker:** optional process using PostgreSQL-backed work claiming as the
  recommended default. It handles slow ingestion, extraction, matching, and
  generation, but never converts an approval into a submission on its own.
- **Adapters:** narrow interfaces for approved job sources, AI providers, and
  any later submission destinations. Each enforces configured limits and
  records provenance.

## 3. Network and deployment boundaries

**Accepted Milestone 1 network policy**

- Use plain HTTP strictly over loopback.
- Publish only Next.js by default, bound on the host as `127.0.0.1:3000`.
- Keep FastAPI, PostgreSQL, and the worker reachable only through the private
  Docker network. The browser uses the Next.js same-origin `/api` proxy and
  does not directly access FastAPI.
- A container may listen on internal `0.0.0.0` when required for communication
  on the isolated Docker network. This is not host or public exposure.
- A temporary FastAPI host port is permitted only in an explicit debugging
  profile and must bind to host loopback; it is absent from default Compose.
- Do not provide LAN access, public ingress, port forwarding, or remote access.
- Keep PostgreSQL exclusively on the private Docker network with no
  host-published port.
- Enforce the canonical browser-visible Host and Origin
  `http://127.0.0.1:3000`; unsafe requests require exact Origin validation.
- Permit `Secure=false` for session cookies only in the explicit loopback HTTP
  environment. Any non-loopback configuration requires HTTPS and
  `Secure=true`; the backend MUST fail closed before serving requests when
  those requirements are absent.
- Defer locally trusted HTTPS until remote or non-loopback access is
  intentionally introduced and reviewed.

All services communicate through a private Docker network. Only Next.js
publishes a default host port. PostgreSQL never publishes a default host port.
Publishing any service through host `0.0.0.0`, a LAN address, or a public
interface violates M1 policy; this restriction does not prohibit internal
container listeners on `0.0.0.0`.

**Accepted Milestone 1 runtime policy**

- Docker Compose is the canonical and only supported runtime.
- Docker Compose commands are the canonical interface for setup, development,
  tests, migrations, backup, and local-shell recovery.
- Pin Node.js, Python, PostgreSQL, and relevant toolchain versions.
- Persist PostgreSQL in a named volume.
- Persist private documents in protected local storage or a dedicated volume;
  never store them in the repository.
- Run application containers as non-root wherever practical and map ownership
  so bind-mounted files do not become root-owned on Fedora.
- Store secrets only in ignored local environment files or an equivalent local
  secret mechanism. A committed `.env.example` may contain variable names and
  safe placeholders only.
- Define service health checks and make dependent startup readiness-aware.
- Native Fedora commands may be documented as debugging aids, but they are not
  a supported or acceptance-tested deployment method.

**Recommended storage and secret defaults**

- Store application files in a dedicated owner-readable directory with least
  permissions; do not mount the repository as document storage.
- Use Docker secrets or owner-protected, ignored environment files for local
  secrets.

The container topology and health checks preserve host binding and fail-closed
rules; Docker defaults must not silently publish a service on all host
interfaces. Remote ingress remains deferred and requires a new threat-model
review.

### M1 session and request-control flow

After successful authentication, FastAPI generates an opaque session token with
at least 256 bits of secure entropy, stores only its cryptographic hash, and
returns the raw value only in the host-only `applypilot_session` cookie. The
server record is authoritative. JWT browser authentication and Remember me do
not exist. Idle expiry is 60 minutes and absolute expiry is 12 hours; activity
never extends the latter. At most three sessions remain active, with the least
recently active revoked upon creation of a fourth.

Next.js sends unsafe same-origin API requests through its private-network proxy
with a custom-header CSRF token. The token has at least 256 bits of entropy, is
bound to and rotated with the session, never appears in a URL, and is validated
alongside exact Origin `http://127.0.0.1:3000`. FastAPI rejects missing,
malformed, expired, or mismatched tokens. Safe read-only methods and explicitly
documented non-browser endpoints are the only possible exemptions.

PostgreSQL holds persistent login-failure/backoff state, active session limits,
revocation and credential-version state, and request-throttle accounting where
durability is required. Session activity persistence is coalesced to at most
one write per five minutes while effective idle expiry is still enforced.

## 4. Critical flows

### First-run setup

FastAPI checks initialization state within a transaction, locks the singleton
setup record or equivalent database primitive, creates one Argon2id credential,
and permanently marks setup complete. Database constraints make a second owner
impossible even when requests race. The setup endpoint returns unavailable
after completion. M1 setup creates no TOTP secret or recovery-code material.

### Local-shell password recovery

Password recovery is a dedicated CLI operation available only from the local
ApplyPilot project/runtime environment. Possession of the Fedora OS account
plus authorized runtime/database access is the recovery authority. No recovery
operation is exposed through Next.js, FastAPI, or any HTTP route.

The M1 CLI prompts twice for the new password using hidden input, applies the same
password policy as first-run setup, and uses one database transaction to
replace the Argon2id hash, revoke every session, and append a redacted security
event. Validation or transaction failure rolls back all three effects, leaving
the existing credential and sessions unchanged. Output and errors are generic
and never contain secrets. It operates correctly when no TOTP configuration
exists, which is the required M1 state.

M1 has no TOTP reset option. If TOTP is activated in a future milestone, its
reset must be a separate explicit CLI option with a high-visibility warning and
additional confirmation. A confirmed future reset invalidates the TOTP
credential, all recovery codes, and all active sessions and appends a redacted
event. Password reset alone never alters TOTP.

### M1 authentication boundary

The owner password is the only application-level authentication factor in M1;
Fedora OS access remains part of the local trust boundary. The authentication
service may expose internal interfaces suitable for a future factor, but M1 has
no TOTP implementation, configuration, secret generation, recovery-code
generation, HTTP route, UI, advertisement, or unreachable placeholder handler.

Future activation requires a documented threat-model review, enrollment and
verification workflows, encrypted secret storage, single-use hashed recovery
codes, reset and disable procedures, session invalidation, migration and
rollback procedures, and dedicated tests. Any proposal for non-loopback or
remote access must reopen the TOTP decision before implementation.

### Backup flow

Docker Compose is the canonical interface for a local-shell backup operation.
The operation obtains a transactionally consistent PostgreSQL dump and stages
the required documents with restrictive permissions. It builds a manifest with
creation time, application/schema/backup-format versions, file inventory,
sizes, and cryptographic checksums, then encrypts the complete bundle to the
owner's age public recipient. No unencrypted final bundle exists. Plaintext
staging is removed on success and failure.

The final encrypted bundle is written to a configured location outside the Git
repository, PostgreSQL named volume, and live document storage. The application
does not upload it. The owner may copy it to an external drive or a
OneDrive-synced folder and should keep at least one copy physically separate
from live data. The age private identity and its offline copy remain entirely
outside the repository, database, bundle, and destination.

The database dump includes required credential state and all profile,
provenance, application, approval, submission, status, and audit history. The
bundle includes uploaded resumes/supporting files and generated documents that
form application history. Sessions/tokens, temporary files, caches, runtime
logs, plaintext secrets, environment files, and unnecessary artifacts are
excluded.

### Restore flow

Restore is a local-shell-only Docker Compose operation. It stops application
services and requires explicit confirmation showing the backup timestamp and
replacement target. It decrypts into a restrictive temporary area, validates
the manifest and checksums, checks backup/schema compatibility, and restores
database and documents into an isolated temporary target. Database readability
and document consistency are tested before replacement.

Live database and documents are replaced only as one consistent unit. The
previous live state remains recoverable until the candidate state passes every
check; failure never leaves a partial replacement. Restored session state is
discarded and all sessions are revoked. Before replacement, preserve the current
minimal deletion-tombstone ledger; after restoring the isolated candidate,
merge and apply every tombstone newer than the backup so deleted live records
cannot reappear. Only then may services start and append a redacted restore
audit event.

Retention cleanup runs only after a new bundle completes and verifies. It keeps
7 daily, 4 weekly, and 6 monthly backups and never deletes the last known-good
bundle. A verified backup is mandatory before a schema migration that can alter
stored data. A restore drill is required before M1 acceptance and after any
material backup-format or schema change.

### Retention and deletion flow

An auditable scheduler evaluates explicit basis timestamps and versioned policy,
including source-specific caps. It never runs from startup or page-view side
effects. Every automatic run first produces a dry-run report with affected
counts, storage, pins, dependencies, and stricter rules. Execution is
transactional where possible, coordinates database/files/indexes/caches to
avoid partial divergence, and appends a redacted event.

Deletion preview resolves application-history and integrity dependencies and
shows exact scope. Owner confirmation moves eligible records to 30-day trash;
sensitive data can bypass trash through an explicitly confirmed permanent path.
Export is offered first. Permanent deletion removes live and derived content,
then writes a content-free tombstone. A fact referenced by an application is
removed from the reusable profile only if its immutable application snapshot is
retained, unless the owner deletes the entire application/snapshot set.

Policy changes are prospective unless the owner approves a migration plan. No
automatic job deletes an in-window submitted application. Source rules may
shorten retention but never silently lengthen the owner's selected period.

### Job ingestion

The common source-adapter contract is read-only and permits only public posting
retrieval, normalization, provenance, freshness, and health operations. M1
implements Greenhouse Job Board, Lever Postings, Ashby Public Job Posting, and
Remotive public APIs. It exposes no candidate creation, owner authentication,
employer/private API, or submission operation.

An approved adapter retrieves data within documented terms and limits. The
system stores the raw source representation or a permitted canonical subset,
source identity, URL, external identifier, retrieval time, and parser version.
Normalization produces a versioned listing. Deduplication links source listings
to a canonical job without deleting provenance.

Normalization keeps owner/runtime jurisdiction separate from job-location and
employer/destination jurisdiction. Structured fields include country, region,
city, timezone, remote classification, relocation, work-authorization and
sponsorship language, employment type, compensation/currency, languages, and
licensing requirements. Adapters retain original URL/source/location/employer
and the source's available eligibility text; unknown fields remain unknown.

Raw payload versions remain distinct from normalized versions; every normalized
or inferred field records derivation and never overwrites the original. Each
adapter independently configures rate limits, retries, timeout, circuit breaker,
pagination, deduplication keys, attribution rendering, retention, and health.
Failure is isolated: other adapters and stored jobs remain usable, and failure
never deletes the last valid copy. A posting is marked closed only after
confirmation across scheduled refreshes.

Greenhouse/Lever/Ashby adapters read only owner-reviewed registry entries.
Remotive rendering always includes “Source: Remotive” and its supplied URL.
Manual entry writes explicit unverified provenance and performs no URL fetch.
Deduplication attaches all manual/source records to a canonical job without
collapsing their distinct provenance.

Greenhouse uses no Harvest, Candidate Ingestion, partner, admin, or private API;
Lever uses no Data, candidate, partner, internal, credentialed, or private API;
Ashby uses no authenticated employer/candidate/partner/private API. No M1
adapter submits. Unsupported sites and browser/internal endpoints have no
adapter contract implementation.

### Matching and generation

A match run snapshots the job version, immutable extracted requirements,
eligible candidate fact versions, preferences, scoring-rule version, weight-set
version, and formula version. Recalculation appends a match version and never
rewrites history. Application approval/submission snapshots retain the match
shown at that time; changed rules or weights can produce stored score diffs.

LLM-assisted extraction may propose typed requirements with exact source text,
location, rationale, and high/medium/low parsing confidence. Deterministic
domain code alone classifies evaluability and computes alignment, coverage,
eligibility, blockers, and ranking. Changed source content invalidates affected
requirements and triggers a new extraction and match version. Owner corrections
are audited and also create new immutable versions.

The scoring service implements D-019's accepted weights and formula. Unknowns
are excluded from alignment numerator and denominator and reduce evidence
coverage; they never become gaps. Capability, preferences, eligibility,
coverage, extraction confidence, ranking, factor lists, and owner actions are
separate outputs. Capability coverage below 40% suppresses a precise combined
alignment. Full-precision components are stored; UI values are rounded.

The eligibility evaluator is separate from scoring. A blocker requires an
explicit cited mandatory requirement, sufficient confidence or owner review,
and a directly contradictory current verified fact. Ambiguity, missing data,
inference, and preferred requirements yield no blocker. Overrides add a reason,
timestamp, and view preference without mutating the original determination.
Blocked jobs remain visible and retain their capability result.

Inferred signals are isolated to discovery recall and a separate Possible
relevance explanation. They cannot enter scoring, eligibility, blocker, or
application paths. Matching cannot use protected traits or proxies, prestige,
employment gaps, career changes, or source identity. Authorization affects only
eligibility and compensation only preferences. M1 contains no learned weighting
from application outcomes.

Generation receives only eligible verified facts plus the job snapshot. Outputs
retain fact references and provider metadata. Unknown or conflicting
information is surfaced rather than filled by inference. Authorization,
sponsorship, relocation, and availability use current D-015-confirmed facts.

Extraction/import writes evidence-backed unverified candidates; inference
writes separate matching signals. Neither path can call the owner-confirmation
transition. The confirmation command is an explicit owner action enforced by
FastAPI and appends an audit event. Scheduled/on-use eligibility evaluation
marks verified versions stale under their 90-day, 30-day, attestation, or
per-payload policies without rewriting history.

Conflict detection groups active versions by semantic key and overlapping
scope. It records competing versions and affected drafts, marks them conflicted,
and blocks generation/submission use. No confidence, recency, majority, or
model-based resolver exists. Owner resolution creates a new verified version or
explicitly selects and reconfirms an existing one, records its reason, and
invalidates affected approvals.

### Final Apply boundary

1. FastAPI creates a canonical review snapshot containing destination, fields,
   values, exact fact-version IDs and snapshots, document digests, consents,
   relevant source URL, and attempt identity.
2. The owner reviews that snapshot and invokes the distinct Final Apply action.
3. FastAPI stores approval time and a digest bound to the snapshot and
   destination.
4. Immediately before an attempt, FastAPI recomputes and compares the digest
   and verifies session/CSRF state and every supporting fact's eligibility.
5. Any material difference rejects the attempt and requires a new review.
6. The attempt and exact payload are recorded before external interaction; the
   final or ambiguous result is appended afterward.

Which changes are "material," approval expiry, and retry authorization are
**unresolved decisions** and must default safely to requiring reapproval.
Any change, staleness, conflict, or revocation affecting a supporting fact is
already classified as material and invalidates approval.

## 5. Reliability and data consistency

- Use database transactions for initialization, fact confirmation, approval,
  attempt creation, and state transitions.
- Use idempotency identifiers for ingestion and any supported submission
  adapter, without interpreting idempotency as owner approval.
- Record ambiguous external outcomes explicitly and do not blindly retry.
- File writes use temporary files, digest verification, atomic rename, and
  compensating cleanup when database persistence fails.
- Audit records are append-oriented; corrections add events rather than
  rewriting history.

## 6. Recommended defaults

- Modular monolith rather than independently deployed services.
- PostgreSQL-backed jobs before adding a separate queue.
- Local filesystem before object storage.
- D-019 deterministic, versioned match scoring; opaque learned ranking is
  prohibited in M1.
- Enable only reviewed employer boards and approved source configurations.

These defaults do not resolve the AI-provider or direct-submission questions.

## 7. Deferred capabilities

- Redis, until queue throughput or coordination measurements justify it
- S3-compatible storage, until deployment or durability needs justify it
- Browser extension
- Remote access, public ingress, and hosted deployment
- Podman, Kubernetes, and cloud deployment
- Any submission adapter not expressly approved
- Adzuna, Arbeitnow, USAJOBS, and every other source not accepted in D-018;
  each requires a new decision and adapter-specific compliance profile

## 8. Unresolved architecture decisions

- Disaster recovery beyond the accepted local backup/restore policy
- Worker implementation and when it first becomes necessary
- AI provider boundary and data minimization requirements
- Future source additions and submission-adapter contracts
- Exact canonicalization and material-change rules for approval payloads
- Whether status synchronization uses source APIs, email access, manual entry,
  or some combination

Data structures are detailed in [Database Schema](DATABASE_SCHEMA.md), and
decision status is authoritative in [Decisions](DECISIONS.md).

## 9. Implemented M1 scaffold (2026-09-02)

The repository now applies the documented modular-monolith boundary as three service trees: `apps/web`, `apps/api`, and `apps/worker`. Each has an independent manifest, tests, and Dockerfile. `packages/api-client` is the generated OpenAPI client boundary; frontend code must not duplicate backend domain schemas manually.

Default Compose publishes only Next.js at `127.0.0.1:3000`. The web container joins a host-edge network for that publication and the internal private network for API proxying; the other services join only the private network. Next.js rewrites same-origin `/api/*` traffic to private-network FastAPI. FastAPI, PostgreSQL 17.4, and the worker publish no default host ports. PostgreSQL uses a named volume. A loopback-only API port exists solely in the explicit `api-debug` profile.

The FastAPI foundation contains an application factory, versioned `/api`
router, non-sensitive live/ready health endpoints, settings with fail-closed
transport validation, redacting logging hooks, SQLAlchemy session/Base
boundaries, stable error schema, and Alembic. Migration
`20260902_0001_owner_authentication` implements the singleton installation and
owner records, hash-only sessions and CSRF verifiers, persistent login
throttling, and redacted security events.

Authentication is separated into routes, dependencies, schemas, services,
repositories, models, and security utilities under `apps/api`. Next.js owns
only the setup/login/session-management presentation and same-origin client.
The implemented endpoints are `/api/initialization/status`,
`/api/initialization`, `/api/auth/login`, `/api/auth/status`,
`/api/auth/logout`, `/api/sessions/current`, `/api/sessions`,
`/api/sessions/{session_id}`, and `/api/sessions/revoke-others`. Password
recovery is deliberately absent from HTTP and runs as
`python -m applypilot.cli.reset_password` inside the API container.

The worker remains lifecycle-only; U-016 remains unresolved and no job
mechanism is implied. The explicit Compose `test` profile builds a test-only
API image and uses an unpublished tmpfs PostgreSQL instance, preserving the
production image and live named volume.

Alembic revision `20260902_0002_candidate_facts` adds the candidate record
foundation. FastAPI owns profile persistence, immutable candidate-fact values,
explicit verification/reconfirmation, revocation, overlap-based conflict
detection, owner resolution, provenance, and redacted audit writes. A database
trigger rejects in-place changes to fact identity, version number, typed value,
or integrity hash. Row locks plus uniqueness constraints serialize concurrent
version creation.

The authenticated API adds `/api/profile`, `/api/candidate-facts`, version and
lifecycle actions, and `/api/candidate-fact-conflicts`. Every mutation uses
D-020 session, CSRF, Host, and exact-Origin enforcement. Next.js renders the
protected `/profile` and `/evidence` destinations and never decides fact
eligibility. Broad lists suppress private, eligibility, and highly sensitive
values; exact authenticated detail is fetched for deliberate inspection.

### Implemented protected resume boundary

Alembic revision `20260902_0003_resume_ingestion` adds resume identities,
immutable versions, content-addressed stored-document metadata, deterministic
extractions, unverified review candidates, and append-oriented document events.
The API container alone mounts the persistent `document-data` volume at
`/var/lib/applypilot/documents`; web, worker, and PostgreSQL cannot read it.
Its owner-only `originals`, `extracted`, `temporary`, `quarantine`, and `trash`
directories use random internal keys. Browser responses never reveal paths.

Upload processing checks request/file size, sanitized display filename,
extension, declared media type, signature/container structure, encryption,
archive safety, parser limits, and SHA-256 before atomic final placement.
PyMuPDF 1.28.2 extracts PDF text by page, python-docx 1.2.0 extracts paragraphs
and tables, and Python 3.13.15 decodes strict UTF-8 text. No OCR, HTML rendering,
external relationship traversal, macro execution, or active-content execution
exists. Temporary input is removed on every success/failure path.

FastAPI exposes authenticated resume metadata/version/extraction, authorized
download, and candidate-review routes. Every mutation uses D-020 CSRF and exact
Origin enforcement. Candidate acceptance invokes the existing fact service
and creates only an `unverified` fact version; the independent Evidence
verification action remains mandatory.

### Typed backend configuration boundary

`apps/api/src/applypilot/core/config.py` is the sole typed runtime-settings
boundary. Database credentials use Pydantic's redacting `SecretStr` and are
revealed only to SQLAlchemy/Alembic. Startup validates a complete psycopg DSN,
the exact Origin shape, the loopback/cookie transport relationship, and an
absolute protected-storage root; production rejects known placeholder
credentials. Settings contain no owner profile, document content, password,
recovery phrase, session, or CSRF values and are never exposed through API
schemas. Next.js receives no backend secrets and continues to use only the
same-origin FastAPI contract.
