# Decisions

This log distinguishes approved direction from proposals. Do not treat a
recommended default as accepted without an owner decision. Superseded entries
must remain in the log with a link to the replacing decision.

## Accepted decisions

### D-001 — Permanent single-owner scope

- **Status:** Accepted
- **Decision:** One owner account exists for the installation's lifetime.
  First-run setup initializes it and later account creation is disabled.
- **Consequences:** Domain tables do not require generic ownership scoping.
  Authentication protects private local data.

### D-002 — Fedora-local, loopback-only first milestone

- **Status:** Accepted
- **Decision:** Initial operation is Docker-based on the owner's Fedora
  computer, with published access restricted to loopback.
- **Consequences:** Remote access requires a later explicit security review.

### D-003 — Core technology direction

- **Status:** Accepted
- **Decision:** Next.js/TypeScript frontend, Python/FastAPI backend,
  PostgreSQL system of record, and Docker local environment.

### D-004 — MVP document storage

- **Status:** Recommended default
- **Proposal:** Protected local filesystem storage with metadata and digests in
  PostgreSQL. S3-compatible storage remains deferred until justified.
- **Rationale:** It fits a local installation with fewer moving parts.

### D-005 — Authentication baseline

- **Status:** Accepted
- **Decision:** Argon2id, opaque HTTP-only cookie sessions, CSRF defense, login
  rate limiting, logout, server-side idle/absolute expiry, and a future-compatible
  TOTP boundary are required. TOTP is not an M1 factor.

### D-006 — Human approval boundary

- **Status:** Accepted
- **Decision:** No submission without explicit Final Apply. Approval binds one
  exact payload and destination; material changes invalidate it. Every attempt
  and result is audited.

### D-007 — Truth and provenance boundary

- **Status:** Accepted
- **Decision:** Generated content cannot invent candidate facts; unknown facts
  remain unknown. Job and candidate provenance is retained.
- **Verification rule:** Only explicit owner confirmation makes an immutable,
  versioned fact verified. D-015 defines its binding lifecycle.

### D-008 — Third-party controls

- **Status:** Accepted
- **Decision:** ApplyPilot never bypasses CAPTCHAs, anti-bot or authentication
  controls, consent, rate limits, or terms. Official APIs, OAuth, and
  owner-authenticated sessions are preferred over stored site passwords.

### D-009 — Optional infrastructure

- **Status:** Accepted
- **Decision:** Redis and S3-compatible storage are not MVP dependencies and
  remain deferred until measurements or deployment needs justify them.

### D-010 — Milestone 1 loopback HTTP transport

- **Status:** Accepted; resolves U-015
- **Decision, amended by D-021:** Milestone 1 uses plain HTTP strictly over
  loopback. Only Next.js publishes by default at host `127.0.0.1:3000`;
  FastAPI, PostgreSQL, and worker remain private to Docker. Host `0.0.0.0`, LAN,
  public ingress, ordinary port forwarding, and remote access are prohibited.
- **Session policy, finalized by D-020:** Use opaque server-managed sessions.
  The host-only cookie has no `Domain`; `Secure=false` is permitted only for the
  explicit loopback HTTP environment. Tokens never enter browser storage, URLs,
  or logs. Unsafe requests require session-bound CSRF and exact Origin checks.
- **Future boundary:** Any non-loopback configuration requires HTTPS and
  `Secure=true`; the backend fails closed otherwise. Locally trusted HTTPS is
  deferred until non-loopback access is intentionally introduced.

### D-011 — Local-shell password recovery

- **Status:** Accepted; resolves U-009
- **Decision:** Password recovery is available only through a dedicated CLI
  command run from the local ApplyPilot project/runtime environment. Control of
  the local Fedora OS account plus authorized runtime/database access is the
  recovery authority. No HTTP, email, SMS, security-question, phrase-based, or
  remote recovery flow exists. The login page may show a `Forgot password?`
  control that displays local-shell reset instructions only; that control is
  instructional disclosure, not a recovery UI, and cannot reset or retrieve a
  password.
- **Password behavior:** Prompt twice with hidden input, enforce the first-run
  password policy, and atomically replace the Argon2id hash, revoke all
  sessions, and append a redacted security event. Any failure leaves the
  current hash and sessions unchanged. Messages are generic and reveal no
  secrets.
- **Future TOTP boundary:** M1 password recovery works without TOTP records and
  has no TOTP reset option. If TOTP is activated later, password reset does not
  reset it; TOTP reset requires a separate option, prominent warning, and
  additional confirmation and invalidates the credential, recovery codes, and
  all sessions while writing a redacted event.
- **Command:** `docker compose run --rm api python -m applypilot.cli.reset_password`.
  Backups are not password recovery.

### D-012 — Canonical Milestone 1 runtime

- **Status:** Accepted; resolves U-014
- **Decision:** Docker Compose is the canonical and only supported Milestone 1
  runtime. It is the canonical interface for setup, development, tests,
  migrations, backup, and recovery. Native Fedora commands may be debugging
  aids only and are not separately supported or acceptance-tested.
- **Network, amended by D-021:** Next.js alone publishes by default at host
  `127.0.0.1:3000`; it proxies `/api` to private-network FastAPI. PostgreSQL and
  worker have no host ports. A debug-only FastAPI publication may bind to
  loopback. Host publication on `0.0.0.0`, LAN, or public interfaces violates
  M1 policy; internal container listeners may use `0.0.0.0`.
- **Runtime controls:** Pin Node.js, Python, PostgreSQL, and toolchain versions;
  use a PostgreSQL named volume and protected persistent document storage; run
  application containers non-root where practical; prevent root-owned Fedora
  bind-mount output; keep secrets in ignored local files or an equivalent local
  mechanism; limit `.env.example` to safe placeholders; and use health checks
  with readiness-aware startup.
- **Deferred:** Podman, Kubernetes, cloud deployment, public hosting, and
  remote access.

### D-013 — TOTP deferred beyond Milestone 1

- **Status:** Accepted; resolves U-013
- **Decision:** M1 uses the owner password as its only application-level
  authentication factor. Fedora OS access remains part of the trust boundary.
  TOTP is future-compatible but is not implemented, configured, advertised,
  generated, or enabled in M1.
- **M1 exclusions:** No TOTP secrets or recovery codes are generated; no MFA
  enrollment, verification, reset, recovery UI, HTTP routes, dormant handlers,
  or capability claims exist. Password recovery requires no TOTP record.
- **Future gate:** Activation requires threat-model review, complete enrollment
  and verification, encrypted secrets, hashed single-use recovery codes, reset
  and disable procedures, session invalidation, migrations, rollback, and
  dedicated tests. Non-loopback or remote-access proposals reopen this decision.
- **Preserved future behavior:** A future explicit TOTP reset is separate from
  password reset and invalidates sessions and recovery codes.

### D-014 — Encrypted backup and isolated restoration

- **Status:** Accepted; resolves U-010
- **Bundle:** Create versioned bundles containing a consistent PostgreSQL dump,
  required uploaded/generated historical documents, and a manifest with time,
  application/schema/format versions, inventory, sizes, and checksums. Preserve
  credentials, profiles, provenance, application/approval/submission history,
  and audit events; exclude sessions/tokens, temporary data, caches, logs,
  plaintext secrets, environment files, and unnecessary artifacts.
- **Encryption:** Encrypt every final bundle to an age public key. Restrictive
  plaintext staging is removed on success/failure. The private identity stays
  outside Git, repository, database, bundle, and destination; the owner keeps
  an offline copy and accepts that loss prevents restoration.
- **Storage and retention:** Write outside repository and live database/document
  storage. M1 does not upload backups; encrypted copies may be placed on an
  external drive or OneDrive-synced folder. Keep 7 daily, 4 weekly, 6 monthly,
  and always the last known-good bundle. Cleanup follows successful verified
  creation. Data-altering migrations require a prior verified backup.
- **Restore:** Local-shell-only through Docker Compose, with services stopped,
  explicit timestamp/target confirmation, isolated validation, compatible
  versions, checksum/readability tests, atomic database/document replacement,
  previous-state preservation, session revocation, and a redacted post-start
  event. Complete an M1 drill and repeat after material format/schema changes.
- **Separation:** Backups are not password recovery. Private keys/passphrases
  never pass through arguments, logs, Git configuration, or committed files.

### D-015 — Verified-fact lifecycle and conflicts

- **Status:** Accepted; resolves U-006
- **Lifecycle:** Canonical facts have immutable versions in `unverified`,
  `verified`, `stale`, `conflicted`, or `revoked` states. Only explicit owner
  confirmation verifies; edits create unverified versions; revocation blocks
  future use without rewriting history.
- **Evidence and inference:** Extraction/import/owner entry create unverified
  candidates. Inference is a separate, labelled matching-only signal. Agreement,
  confidence, recency, majority, models, and missing evidence never establish or
  resolve truth. Claims cite exact eligible verified versions.
- **Reconfirmation:** Stable completed history has no automatic expiry but may
  become stale on change/edit/revocation; current identity/preferences use 90
  days; authorization/availability/compensation use 30 days plus attestation;
  legal declarations use each exact payload; highly sensitive voluntary answers
  use each destination and attempt and are not retained by default.
- **Conflicts:** Overlapping same-key values are blocked until the owner selects,
  corrects, scopes, or revokes and supplies an audited reason.
- **Applications:** Approval binds the exact payload, fact versions, immutable
  snapshots, destination, and attempt. Ineligible/unknown facts block required
  answers and Final Apply. Supporting fact changes or conflict resolution
  invalidate affected approval while historical applications remain unchanged.

### D-016 — India personal-use legal scope and data lifecycle

- **Status:** Accepted; resolves U-012
- **Scope:** India is the owner and local runtime jurisdiction; use is
  single-owner personal/domestic. This is an
  engineering assumption, not legal advice or universal compliance
  certification. Foreign destinations still require their forms, declarations,
  transfers, and terms. Stricter source/destination rules win; D-018 governs
  approved M1 sources and their compliance profiles.
- **Reopen gate:** Public, multi-user, commercial, remote/non-loopback,
  employer/recruiter, multi-person analytics, high-volume automated use, or
  processing another person's profile.
- **Retention:** Active data while active; superseded facts/resumes 24 months
  unless referenced; unacted jobs 180 days; saved jobs two years unless pinned;
  abandoned drafts 180 days after warning; submitted application history five
  years after final status; security/admin audits one year subject to holds;
  logs at most 30 days; temporary files immediately; signals with source/recompute.
- **Sensitive data:** Unsubmitted answers purge within 30 days of abandonment;
  submitted answers follow application history, are visibly marked, never
  speculatively collected/reused, and remain owner-deletable with dependencies.
- **Deletion:** Dependency preview and export precede confirmation; default
  trash is 30 days with immediate sensitive purge. Permanent deletion removes
  live/derived content, preserves only a redacted tombstone, and gives an
  explicit fact-snapshot/application deletion choice.
- **Backups:** Existing encrypted bundles expire under D-014 rather than being
  surgically rewritten. Newer tombstones are reapplied after restore before
  serving. Cleanup is dry-run-first, auditable, prospective, dependency-aware,
  and cannot automatically delete an in-window submitted application.

### D-017 — Worldwide job discovery with explicit eligibility dimensions

- **Status:** Accepted
- **Decision:** Discovery is worldwide; India is not a job filter. Include
  India, international remote, overseas hybrid/on-site, relocation, sponsorship,
  internship, part-time, contract, and full-time opportunities.
- **Structure:** Store owner jurisdiction, job country/region/city/timezone,
  employer/destination jurisdiction, remote class, relocation, authorization,
  sponsorship, employment type, compensation/currency, languages, and source
  eligibility text separately. Preserve original URL/source/employer/location.
- **Preferences:** Support worldwide, country/city include/exclude/preference,
  remote mode, relocation, timezones, sponsorship, employment types, minimum
  compensation by currency, and languages.
- **Matching:** Explain separate technical, experience, location, remote,
  authorization, sponsorship, language, timezone, and relocation lanes. Never
  infer citizenship/nationality/visa/authorization/protected traits/relocation.
  Unknowns remain unknown; technical strength cannot hide other blockers.
- **Legal boundary:** ApplyPilot explains sourced requirements but does not
  determine immigration eligibility or claim universal compliance. D-015
  governs current owner answers; stricter destination/source rules and D-018
  remain authoritative. Worldwide discovery does not make the tool a service.

### D-018 — Approved M1 read-only discovery sources

- **Status:** Accepted; resolves U-001
- **Approved adapters:** Greenhouse Job Board API, Lever Postings API, Ashby
  Public Job Posting API, and Remotive Public Jobs API. They retrieve only
  public published postings through documented public interfaces and cannot
  authenticate as the owner, create candidates, call employer/private APIs, or
  submit applications.
- **ATS registry:** Greenhouse board tokens, Lever employer sites, and Ashby
  board names must be explicit, owner-managed, reviewed configurations. Each
  registry entry records employer, verified domain, provider, board identifier,
  career URL, state, verification time, and method. Discovery never crawls for
  boards; invalid, redirected, repurposed, or mismatched entries are disabled.
- **Source boundaries:** Greenhouse excludes Harvest, Candidate Ingestion,
  partner, admin, and private APIs; Lever excludes Data, candidate, partner,
  internal, credentialed, and private APIs; Ashby excludes authenticated,
  employer, candidate, partner, and private APIs. Remotive requires visible
  “Source: Remotive” attribution, its supplied URL, and no redistribution.
- **Provenance:** Preserve source/posting ID, source and canonical application
  URLs, employer and board, retrieval and supplied publication/update times,
  original location/remote values, attribution, raw payload version/hash, and
  adapter version. Raw and normalized values remain distinct, derivations are
  traceable, unknowns remain unknown, and duplicates retain every source link.
- **Unsupported automation:** LinkedIn, Indeed, Glassdoor, Naukri, Wellfound,
  Google Jobs, social media, arbitrary search results, and sites without an
  approved API/feed or permission cannot be scraped, crawled, reverse-
  engineered, or accessed through copied endpoints or owner cookies. Controls,
  consent, rate limits, terms, and access restrictions are never bypassed.
- **Manual entry:** Owner-supplied jobs are labelled “Manually entered — source
  not automatically verified,” cause no URL fetch, and preserve distinct
  provenance through reconciliation and duplicate detection.
- **Resilience and terms:** Each adapter owns rate, retry, timeout, circuit
  breaker, pagination, deduplication, attribution, retention, and health rules.
  Failure is isolated and never deletes the last valid copy; closure requires
  confirmation across refreshes. Stricter source terms override defaults.
- **Application boundary:** This decision approves discovery only. Apply opens
  Application Studio for package preparation; no M1 source adapter submits.
  Later submission requires a destination-specific decision, terms and threat
  reviews, payload mapping, approval contract, and tests. Success requires a
  destination receipt or owner-confirmed outcome.
- **Conditional future sources:** Adzuna requires an account, current terms,
  attribution/quota/caching/retention review, coverage tests, and contract
  tests; Arbeitnow requires recorded API/attribution rules; USAJOBS requires a
  separate evaluation. A free API key is not approval. Every added source needs
  a new decision and adapter-specific compliance profile.

### D-019 — Deterministic matching, blockers, confidence, and fairness

- **Status:** Accepted; resolves U-007
- **Boundary:** Matching is deterministic, explainable, versioned, and
  reproducible. LLMs may extract cited requirements but cannot set final scores,
  eligibility, or blockers. Outputs describe alignment, never hiring/interview
  probability, recruiter interest, candidate quality, or job performance.
- **Outputs:** Separately show 0–100 capability alignment, 0–100 preference
  compatibility, compatible/unclear/blocked eligibility, 0–100 evidence
  coverage, high/medium/low extraction confidence, factor/action lists, and a
  visible ranking derivation.
- **Weights:** Capability relative weights are technical 35, experience/
  seniority 25, role/responsibility 15, domain 10, education/certifications 10,
  normalized into 85% of combined alignment. Preferences are employment type
  4, location/workplace 4, compensation 4, and timezone 3, totaling 15%.
- **Formula:** Evaluable requirements score full 1.0, partial 0.5, or verified
  gap 0.0. Unknowns leave numerator and denominator and reduce weighted evidence
  coverage. Combined alignment is 85% capability plus 15% preference. Ranking
  is `combined_alignment * (0.50 + 0.50 * evidence_coverage)`. Under 40%
  capability coverage, show “Insufficient evidence,” not a precise combined
  percentage. Store precision and versions; round display to whole numbers.
- **Requirements:** Mandatory items receive 3x preferred weight; substantive
  descriptive work may receive 0.5x preferred; boilerplate/marketing receives
  zero. Preferred wording cannot become mandatory. Mandatory status needs a
  citation; low-confidence classification is unclear pending owner review.
- **Blockers:** Eligibility is separate. Blocking requires an explicit cited
  mandatory requirement, adequate extraction confidence or owner review, and a
  directly contradictory current verified fact with citations. Missing data,
  ambiguity, preference, or inference cannot block. Blocked jobs stay visible;
  overrides preserve original result, reason, time, and view preference.
- **Inference/confidence:** Inference supports discovery recall and a separate
  Possible relevance explanation only. It cannot score, satisfy requirements,
  affect blockers, or enter application content. Confidence measures parsing,
  not suitability or truth; changed source content invalidates affected
  requirements and creates a new match version.
- **Fairness:** Protected traits and proxies, prestige, source identity,
  employment gaps, and generic career-change penalties never affect match
  output. Authorization/sponsorship affect eligibility only; compensation
  affects preferences only. M1 does not learn weights from outcomes.
- **Versioning/UX:** Requirement, rule, weight, match, correction, override,
  diff, and application-time snapshots are immutable. Every component expands
  to its evidence; unknowns, gaps, possible relevance, and blockers are visibly
  distinct. Score-only celebratory or discouraging language is prohibited. The
  owner may later adjust preference weights within documented limits; every
  change creates a weight-set version. AI cannot silently change capability
  weights, and older-version scores are labelled.

### D-020 — M1 sessions, CSRF, and throttling

- **Status:** Accepted; resolves U-017
- **Session:** Generate opaque tokens with at least 256 bits of secure entropy
  only after successful authentication, send raw values only to the browser,
  and store only cryptographic hashes. JWT browser authentication is prohibited.
  Server state is authoritative.
- **Cookie:** Use host-only `applypilot_session` with `HttpOnly=true`,
  `SameSite=Strict`, `Path=/`, no `Domain`, and lifetime no longer than absolute
  expiry. `Secure=false` is loopback-HTTP-only; future HTTPS/non-loopback uses
  `Secure=true`.
- **Expiry and concurrency:** Idle expiry is 60 minutes and absolute expiry is
  12 hours. Activity extends only idle. M1 has no Remember me. Allow three
  active sessions; a fourth revokes the least recently active. Provide
  non-invasive session inspection and individual/all-other revocation.
- **Invalidation:** Password change, local recovery, restore, future factor
  change, and suspected compromise revoke affected sessions. Expiry returns to
  login without sensitive browser/URL persistence; backend drafts protect work.
- **CSRF:** Every unsafe request uses a session-bound custom-header token with
  at least 256 bits of entropy plus exact allowed-Origin validation. Rotate it
  with session replacement; reject missing, malformed, expired, or mismatched
  values. SameSite is defense in depth.
- **Login backoff:** Persist consecutive failures. Failures 5–10 delay 30, 60,
  120, 240, 480, and 900 seconds; later failures cap at 900. Success resets the
  count. There is no permanent lockout; failures and events are generic and
  redacted; local recovery remains available.
- **Request limits:** Per session, allow 300 authenticated requests per rolling
  five minutes and 10 expensive owner operations per minute. Setup allows three
  attempts per five minutes until permanently disabled. Only one synchronization
  runs per adapter. Return safe HTTP 429/Retry-After. U-008 governs generation
  limits and U-002 governs future submission limits.
- **Storage/audit:** Retain token hash, creation/activity/expiry/revocation,
  credential version, and optional non-invasive label. Coalesce activity writes
  to once per five minutes without weakening idle checks. Distinguish all
  accepted login/session event classes without storing passwords or token values.

### D-021 — Same-origin Docker network amendment

- **Status:** Accepted amendment to D-010 and D-012
- **Boundary:** Host publication differs from container listening. Containers
  may listen internally on `0.0.0.0` when needed on the isolated Docker network;
  this is not public exposure. No host port may bind on `0.0.0.0`, LAN, or a
  public interface.
- **Topology:** Only Next.js publishes by default, at `127.0.0.1:3000`. It
  proxies same-origin `/api` to FastAPI through the private network. FastAPI,
  PostgreSQL, and worker are private. PostgreSQL never has a default host port.
- **Debugging:** FastAPI may publish temporarily only through an explicit
  debugging profile bound to loopback; this is absent from default Compose.
- **Browser security:** The canonical browser-visible origin is
  `http://127.0.0.1:3000`. Cookie, CSRF, Host, and Origin controls consistently
  enforce that single origin.

### D-022 — Approved M1 product-design direction

- **Status:** Accepted
- **Visual direction:** Use the owner-approved fourth concept: a dark structured
  sidebar, light editorial workspace, split opportunity list/detail layout, and
  evidence-rich match analysis. `DESIGN_SYSTEM.md` is the implementation
  contract for tokens, typography, spacing, responsive behavior, components,
  states, accessibility, and the first UI slice.
- **Mockup boundary:** The reference defines hierarchy and composition only. Its
  people, jobs, companies, dates, percentages, locations, eligibility claims,
  and source records are synthetic and cannot be hardcoded or treated as verified
  owner/job data.
- **Terminology corrections:** Derived alignment is not an overall-fit or hiring
  prediction. Eligibility uses compatible, unclear, or blocked. Under 40%
  capability evidence coverage, show Insufficient evidence rather than a precise
  combined percentage. Score-only praise or discouragement is prohibited.
- **Action boundary:** Prepare application opens a preparation workflow and does
  not submit, send email, create a candidate, or contact an employer. Final Apply
  remains outside M1 and unresolved later-milestone behavior cannot be mocked as
  active functionality.
- **Implementation gate:** The first slice is an authenticated, responsive shell
  with synthetic typed Discover data and working search, filter, sort, save,
  selection, match-evidence, loading, empty, uncertain, blocked, insufficient-
  evidence, and error states. Design QA, keyboard operation, and WCAG 2.2 AA are
  required before handoff.

### D-023 — M1 Argon2id implementation parameters

- **Status:** Accepted implementation decision
- **Measurement:** Benchmarked through Docker Compose on the owner's Fedora
  computer using Python 3.13.15, `argon2-cffi` 23.1.0, and the pinned API
  container. Five interactive hashes at 65,536 KiB memory, time cost 8, and
  parallelism 2 measured approximately 167, 313, 332, 249, and 382 ms (about
  289 ms mean). Time cost 4 averaged about 127 ms and was rejected as below the
  accepted 250–500 ms target.
- **Parameters:** Argon2id; memory cost 65,536 KiB; time cost 8; parallelism 2;
  hash length 32 bytes; salt length 16 bytes. The encoded verifier stores its
  algorithm and parameters in PostgreSQL; no plaintext password is stored.
- **Password input:** 12-character minimum, 1,024-character maximum, no
  composition requirement, no silent truncation, and confirmation during
  setup and local-shell recovery.
- **Review trigger:** Re-benchmark after a material host/container hardware or
  runtime change. Any parameter change is a new documented decision and uses
  verifier rehashing after a successful authentication; it does not weaken
  D-020.

### D-024 — Resume storage and deterministic parser safety limits

- **Status:** Accepted implementation decision
- **Scope:** M2 resume-ingestion foundation under D-004 and D-015.
- **Storage:** Use an API-only protected Docker named volume outside Git with
  `0700` directories, `0600` files, random internal names, safe temporary files,
  atomic rename, and SHA-256 content identity. No browser-visible path exists.
- **Formats and versions:** PDF through PyMuPDF 1.28.2, DOCX through
  python-docx 1.2.0, multipart ingestion through python-multipart 0.0.32, and
  strict UTF-8 text through Python 3.13.15's standard library. OCR is absent.
  Package metadata reports PyMuPDF as AGPL-3.0/commercial dual-licensed,
  python-docx as MIT, and python-multipart as Apache-2.0; redistribution or a
  product-scope change requires a fresh license review.
- **Limits:** 10 MiB upload; 250 PDF pages; 2,000,000 extracted characters;
  2,000 DOCX entries; 50 MiB DOCX uncompressed content; 100:1 maximum per-entry
  compression ratio; 15-second fail-closed parser budget.
- **Boundary:** Deterministic labels may create cited review candidates only.
  Acceptance calls the existing fact service and creates an ordinary
  `unverified` version. Verification is a later separate owner action.
- **Change control:** Raising a limit, adding a format/parser, enabling OCR, or
  moving storage requires a new accepted decision and security/test review.

## Recommended defaults awaiting acceptance

- D-R01: Modular monolith with a PostgreSQL-backed worker when asynchronous
  work becomes necessary.
- D-R02: Protected local filesystem for documents.
- D-R06: Safest approval behavior: any uncertain materiality or retry requires
  a new review and Final Apply approval.

## Superseded recommendations

- D-R04: The former 30-minute idle/12-hour absolute session target is
  superseded by D-020's accepted 60-minute idle/12-hour absolute policy.

## Unresolved decisions

| ID | Decision needed | Classification | Affected milestone |
| --- | --- | --- | --- |
| U-002 | Does the initial product stop at an application package or submit anywhere directly? | blocks a later named milestone | M7 |
| U-003 | Which destinations, if any, support direct submission? | requires external/provider-specific research | M7 |
| U-004 | Approval lifetime, retry authorization, and material-change taxonomy | blocks a later named milestone | M6–M7 |
| U-005 | Which additional sensitive fields, beyond D-015's named categories, require per-application confirmation? | blocks a later named milestone | M5–M7 |
| U-008 | AI provider, data disclosure, processing region, retention, and training terms | requires external/provider-specific research | M5 |
| U-011 | Manual, source, or email-derived application-status updates | blocks a later named milestone | M7 |
| U-016 | Exact worker trigger and PostgreSQL-backed implementation | deferred optional capability | Later milestone that demonstrates an asynchronous-work need |

## Deferred capabilities

- Remote access and public hosting
- Browser extension
- Redis-backed queues/caching
- S3-compatible document storage
- Unapproved submission adapters
- Automated sending of follow-up communications
- Browser-based password reset, including any one-time short-lived reset token.
  A future proposal must be a new accepted security decision. If implemented,
  such a token must authorize password replacement only, never reveal the old
  password, be stored only as a hash, expire within 10 minutes, be single use,
  remain bound to loopback, revoke every session after reset, have strict
  attempt limits, and be audited without storing the token. Permanent recovery
  phrases are not an allowed design.

## Next recommended decision

Resolve U-008 next: select the AI provider boundary and accept data-disclosure,
processing-region, retention, and training-use rules before M5. It requires
provider-specific research and does not block the M1 foundation.
