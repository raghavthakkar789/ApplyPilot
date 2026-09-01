# Development Roadmap

## Roadmap rules

No phase may weaken the invariants in
[Product Requirements](PRODUCT_REQUIREMENTS.md). Unresolved decisions must be
accepted in [Decisions](DECISIONS.md) before dependent implementation begins.
Milestone completion requires recorded evidence in [Progress](PROGRESS.md).

## M0 — Foundational documentation

**Current phase.** Create and review the eight repository documents, reconcile
terminology, identify unresolved decisions, and do not scaffold code.

Acceptance criteria:

- All eight approved files exist and only documentation/Git metadata exist.
- `git diff --check` passes.
- Scope searches and human review find no accidental additional-account or
  hosted-service assumptions.
- Every permanent invariant appears in product, architecture, security, and
  repository guidance.
- Unresolved questions are recorded without silent resolution.

## M1 — Local foundation and owner security

After explicit approval, establish the Docker-based Next.js, FastAPI, and
PostgreSQL environment, protected storage boundary, first-run setup, login,
sessions, CSRF, throttling, logout, expiry, and local-shell password recovery.
Docker Compose is the sole supported and acceptance-tested runtime and the
canonical interface for all M1 operational commands.

Acceptance criteria:

- Next.js alone publishes by default at host `127.0.0.1:3000`; same-origin
  `/api` reaches FastAPI through the private Docker network. FastAPI,
  PostgreSQL, and worker have no default host ports.
- Network tests distinguish container-internal `0.0.0.0` listeners from host
  publication and reject host `0.0.0.0`, LAN, and public bindings. An explicit
  debug profile may publish FastAPI only on loopback.
- Node.js, Python, PostgreSQL, and relevant toolchain versions are pinned.
- PostgreSQL survives container recreation through a named volume; private
  documents survive through protected local storage or a dedicated volume.
- Application containers run non-root wherever practical, and bind-mount tests
  confirm created files are not root-owned on Fedora.
- Secret-handling checks confirm ignored local values and safe-placeholder-only
  `.env.example` content.
- Health checks and readiness-aware startup pass dependency failure/recovery
  tests.
- Setup, development, test, migration, backup, and recovery instructions use
  Docker Compose; any native Fedora commands are labeled debugging-only.
- Backup tests create only age-encrypted final bundles outside repository/live
  storage, verify the versioned manifest and checksums, and remove restrictive
  plaintext staging on both success and injected failure.
- Content tests include credential/profile/provenance/application/approval/
  submission/audit history and required documents while excluding sessions,
  tokens, logs, caches, environment files, and plaintext secrets.
- Retention tests preserve 7 daily, 4 weekly, 6 monthly, and the last known-good
  verified bundle; migration tests require a verified pre-migration backup.
- A documented isolated restore drill validates compatibility and readability,
  replaces database/documents as one unit, preserves the previous state until
  success, revokes sessions, and records a redacted post-start event.
- Restore tests preserve and reapply tombstones newer than the selected backup
  before requests can be served.
- Legal-scope documentation identifies India personal use as an assumption,
  never a certification, and preserves stricter source restrictions.
- Timestamp-driven retention tests cover facts/resumes, jobs, drafts,
  applications, audits, logs, temporary data, inferred signals, and sensitive
  answers at every accepted boundary.
- Deletion tests cover dry runs, dependency preview, export, 30-day trash,
  immediate sensitive purge, derived-data cleanup, application-snapshot choices,
  tombstones, prospective policy changes, and failure atomicity.
- A 20-request concurrent setup test produces exactly one owner.
- Account creation is inaccessible after setup.
- Session tests verify at least 256 bits of token entropy, hash-only database
  storage, cookie name/attributes, no JWT or Remember me, authoritative
  revocation, 60-minute idle and 12-hour absolute expiry, and no extension of
  absolute expiry by activity.
- CSRF tests verify at least 256 bits of entropy, session binding, custom-header
  delivery, rotation, exact `http://127.0.0.1:3000` Origin validation, and
  rejection of missing/malformed/expired/mismatched values.
- Three-session-cap tests revoke the least recently active fourth session;
  session management supports individual/all-other revocation without invasive
  fingerprinting.
- Password change, recovery, restore, future-factor-change hooks, suspected
  compromise, logout, expiry, and credential version tests revoke sessions.
- Persistent login tests cover failures 5–10 at 30/60/120/240/480/900 seconds,
  the 900-second cap, success reset, generic errors, no permanent lockout, and
  local recovery availability.
- Request-limit tests cover 300 per five minutes, expensive operations 10 per
  minute, setup three per five minutes, one active sync per adapter, HTTP 429
  with safe Retry-After, and authenticated administrative health data.
- Activity-coalescing tests limit database writes to once per five minutes
  without weakening idle enforcement. Audit tests cover every D-020 event class
  and prove passwords/session/CSRF values are absent.
- CLI tests verify hidden double-entry, first-run password policy reuse, atomic
  hash replacement, all-session invalidation, and a redacted security event.
- Failure-injection tests verify that password and sessions remain unchanged
  when validation, hash replacement, session revocation, or audit writing fails.
- No frontend or HTTP recovery route exists. Password-recovery tests verify the
  command operates with no TOTP records.
- First-run, login, and recovery tests verify that no TOTP secret or
  recovery-code material is generated.
- Route, API-schema, UI, and configuration inventories verify that no MFA
  enrollment, verification, reset, recovery, dormant handler, or capability
  claim is exposed in M1.
- Secret scanning reports no committed secrets or private data.

Session parameters are accepted in D-020. The exact password-recovery command
name and implementation structure will be finalized during this milestone
without changing the accepted security behavior.

## M2 — Candidate record and documents

Implement versioned profile, preferences, resume storage/extraction, explicit
fact confirmation, and provenance.

Acceptance criteria:

- Upload validation rejects unsupported, oversized, and path-manipulating
  inputs in all test cases.
- File/database failure tests leave no untracked partial artifact.
- Owner-entered, imported, and extracted values remain unverified until a
  dedicated owner-confirmation action; source agreement never verifies them.
- Immutable versions contain all required typed value, provenance, evidence,
  lifecycle, extraction, confirmation, sensitivity, reconfirmation, revocation,
  supersession, and integrity metadata.
- Tests enforce all lifecycle transitions and 90-day, 30-day, attestation, and
  per-payload reconfirmation policies.
- Conflict fixtures for resumes, profile edits, and imports remain blocked until
  owner resolution; newest/confident/majority/model resolution is impossible.
- Inferred signals remain labelled matching-only records and are rejected from
  generation and payload fact references.
- Sensitive answers are neither inferred nor automatically reused and require
  destination-and-attempt confirmation without default retention.
- Review shows supporting facts/provenance; unsupported or ineligible required
  answers block Final Apply. Fact changes invalidate affected approvals while
  historical application snapshots remain exact.

Blocked only by later implementation approval and the D-018 compliance profile
for each enabled source.

## M3 — Job ingestion and discovery

Implement only accepted source adapters, normalization, deduplication,
freshness, and source-attributed detail views.

Acceptance criteria:

- 100% of displayed test listings retain source identity and URL.
- Contract tests cover the read-only Greenhouse Job Board, Lever Postings,
  Ashby Public Job Posting, and Remotive Jobs APIs and reject private,
  authenticated, candidate-creation, and submission operations.
- Greenhouse, Lever, and Ashby fixtures can run only through active,
  owner-reviewed employer-board registry entries; altered, redirected, or
  employer/domain-mismatched boards are disabled.
- Remotive fixtures always render “Source: Remotive,” retain its supplied URL,
  and cannot enter a redistribution workflow.
- Worldwide fixtures cover India, international remote, overseas on-site/hybrid,
  relocation, sponsorship, and every supported employment type without an
  India-only exclusion.
- Normalized records distinguish owner jurisdiction, job location, and
  employer/destination jurisdiction and preserve source location, remote,
  employer, URL, and eligibility language.
- Repeat ingestion is idempotent for identical source versions.
- Deduplication never deletes source provenance.
- Raw source versions remain immutable and separate from normalized values;
  every derived field is traceable to its input and adapter version.
- Manual listings show “Manually entered — source not automatically verified,”
  trigger no URL retrieval, and retain separate provenance after deduplication.
- Rate-limit, authentication, CAPTCHA, consent, and terms stop conditions have
  automated or adapter-contract tests.
- Adapter timeout, retry, pagination, circuit-breaker, attribution, retention,
  and health tests show that one failing source cannot disable other sources or
  delete the last valid copy.
- Closure requires confirmation across scheduled refreshes; stale, partial,
  uncertain, and conflicting data remains visible.
- Worldwide fixtures operate over the finite configured ATS-board registry and
  Remotive feed without crawling to discover additional boards.

Blocked only by later implementation approval; launch sources are accepted in
D-018.

## M4 — Transparent matching

Implement versioned scoring, confidence, evidence, strengths, gaps, unknowns,
and possible disqualifiers.

Acceptance criteria:

- Re-running an unchanged fixture with the same rule version produces the same
  score and explanation in 100% of cases.
- Every scored factor links to an immutable cited requirement, exact eligible
  verified fact version, rule version, and weight-set version; LLM output cannot
  directly set score, eligibility, or blocker state.
- Formula tests cover accepted dimension weights, mandatory 3x/preferred and
  descriptive 0.5x weighting, 1.0/0.5/0.0 outcomes, normalization, evidence
  coverage, uncertainty adjustment, precision, and UI rounding.
- Unknown and insufficient evidence are excluded from alignment numerator and
  denominator, reduce coverage, and never become contradictions. Below 40%
  capability coverage always renders “Insufficient evidence” without a precise
  combined percentage.
- Capability, preference, eligibility, coverage, extraction confidence, factor
  lists, and visible ranking derivation are separately asserted in every UI
  fixture. Hiring/interview probability language is absent.
- Blocker tests require cited mandatory language plus sufficient confidence or
  owner review and a contradictory current verified fact. Missing data,
  ambiguity, low-confidence unreviewed extraction, preference, and inference
  cannot create or clear a blocker.
- Blocked jobs remain inspectable with technical capability and evidence;
  overrides preserve the original determination and audit reason.
- Inferred signals affect only discovery recall/Possible relevance and have no
  scored-factor, blocker, eligibility, or application-content path.
- Prohibited-feature tests show protected traits and proxies never enter
  capability, preferences, eligibility, or ranking.
- Perturbing or removing names, photographs, birth dates, graduation years,
  addresses, or demographic answers leaves every output unchanged in 100% of
  fixtures. Authorization changes affect only explained eligibility;
  compensation only preferences; source-only changes with identical normalized
  content affect nothing.
- Golden cases cover high capability with blocker, unclear authorization, low
  coverage, preferred versus mandatory, inferred skills, career gaps,
  international relocation, conflicting facts, and changed job descriptions.
- Rule/weight changes append match versions and score diffs; corrections are
  audited; historical application-time snapshots remain byte-for-byte
  unchanged after recalculation.

Blocked only by later implementation approval; policy is accepted in D-019.

## M5 — Grounded generation

Implement drafts and claim-to-fact traceability for an accepted AI/provider
boundary.

Acceptance criteria:

- Every factual claim admitted to an application has at least one verified
  fact-version reference.
- Unsupported-claim and prompt-injection fixtures are blocked or flagged for
  correction in all expected cases.
- Provider/model, template, inputs, outputs, and document digests are retained.
- Unknown answers remain blank or explicitly unresolved.

Blocked by provider/data-processing and sensitive-field decisions.

## M6 — Review and Final Apply boundary

Implement complete review snapshots, canonicalization, digest-bound approval,
invalidation, and durable attempt auditing. A simulated destination is
sufficient; live submission is not implied.

Acceptance criteria:

- Changing any classified material field, document, consent, or destination
  invalidates approval in 100% of tests.
- No attempt can start without a valid snapshot-bound approval.
- Every attempted outcome, including timeout and ambiguity, is auditable.
- Concurrency tests prevent double starts where policy prohibits them.

Blocked by material-change taxonomy, approval lifetime, and retry policy.

## M7 — Approved submission integration and tracking

Only if separately approved, add narrowly supported destination adapters and
status tracking.

Acceptance criteria:

- Each adapter has documented authorization, terms, rate limits, consent,
  attribution, credential handling, and stop conditions.
- Contract tests demonstrate no CAPTCHA, control, or rate-limit bypass.
- Exact submitted fields/documents and every result are reconstructable.
- Ambiguous outcomes do not trigger blind retries.
- Status events preserve time, origin, and evidence.

Blocked by whether direct submission is in scope, destination selection, retry
rules, and status sources.

## Deferred evaluation

TOTP activation, Redis, S3-compatible storage, browser extension, Podman,
Kubernetes, cloud deployment, remote access, and hosted deployment each require
evidence of need and an explicit decision. Remote access additionally requires
a new security milestone and reopening the TOTP decision.
