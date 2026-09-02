# Product Requirements

## 1. Product definition

ApplyPilot is a private, permanently single-owner application that helps its
owner discover jobs, evaluate fit, prepare truthful application materials,
review an exact application, and record the outcome. Its initial deployment is
local and loopback-only on the owner's Fedora computer.

Status vocabulary used throughout the documentation:

- **Accepted decision:** approved product or technical direction.
- **Recommended default:** proposed starting point requiring no product-scope
  assumption, but still subject to owner approval where noted.
- **Unresolved decision:** a choice that must not be silently resolved.
- **Deferred capability:** explicitly outside the current milestone.

## 2. Permanent invariants

The invariants in [AGENTS.md](../AGENTS.md) apply to every workflow. In
particular, no submission occurs without explicit Final Apply approval; an
approval identifies one exact payload and destination; material changes revoke
that approval; generated content cannot invent candidate facts; unknown facts
remain unknown; provenance is retained; all attempts are auditable; and source
protections, consent, rate limits, and terms are never bypassed.

## 3. Owner and operating context

**Accepted decisions**

- There is exactly one owner account for the lifetime of an installation.
- There is no public signup route. A secure first-run flow creates the owner,
  after which account creation is permanently disabled.
- Authentication exists solely to protect the owner's private data.
- Initial access is from the same Fedora computer over loopback.
- The sole browser-visible M1 origin is `http://127.0.0.1:3000`. Only Next.js
  publishes by default; it proxies `/api` to private-network FastAPI. PostgreSQL
  and worker remain private, and FastAPI host publication is debug-profile-only.
- Container-internal `0.0.0.0` listening is allowed for private Docker
  communication; host publication on `0.0.0.0`, LAN, or public interfaces is
  prohibited.
- Docker Compose is the only supported and acceptance-tested Milestone 1
  runtime. Native Fedora execution may be documented only for debugging.
- Initial jurisdiction is India under a personal/domestic-use engineering scope
  assumption. This is not legal advice or certification of universal legal,
  GDPR/UK GDPR, employment-law, source-term, or employer-form compliance.
- Job discovery is worldwide. India describes the owner's location and local
  runtime, not a geographic job filter or a claim of worldwide eligibility.

The words "owner" and "candidate" describe the same person. "Owner" is used
for authentication and approval; "candidate" is used for job-fit data.

## 4. Functional requirements

### 4.1 Security and setup

- First-run setup MUST create at most one owner, including under concurrent
  requests.
- Passwords MUST use Argon2id with upgradeable parameters.
- Authentication MUST use opaque, server-managed sessions in HTTP-only
  cookies, with CSRF protection, login throttling, logout, idle expiry, and
  absolute expiry.
- Session and CSRF tokens MUST each have at least 256 bits of cryptographically
  secure entropy. Store only the session-token hash. M1 does not use JWT browser
  authentication or Remember me.
- Use the host-only `applypilot_session` cookie with `HttpOnly`,
  `SameSite=Strict`, `Path=/`, no `Domain`, and a lifetime no longer than the
  authoritative server session. `Secure=false` is loopback-HTTP-only.
- Enforce a 60-minute idle timeout, 12-hour absolute timeout, and maximum three
  active sessions. Activity cannot extend absolute expiry; a fourth session
  revokes the least recently active session.
- Every unsafe browser request requires a session-bound CSRF token in a custom
  header and exact Origin validation against `http://127.0.0.1:3000`.
- Persist login failures and use D-020's bounded exponential backoff. Apply the
  accepted general, expensive-operation, initialization, and synchronization
  request limits without permanent account lockout.
- Account creation endpoints MUST become unavailable after initialization.
- M1 authentication uses the owner password as its only application-level
  factor; Fedora OS access remains part of the local trust boundary.
- TOTP is future-compatible but MUST NOT be implemented, configured,
  advertised, generated, or enabled in M1. First-run setup creates no TOTP
  secret or recovery code, and M1 exposes no MFA route or UI.
- Password recovery MUST be available only through a dedicated local CLI, never
  through the frontend or HTTP. It MUST use hidden double-entry, the first-run
  password policy, atomic hash replacement, all-session invalidation, and a
  redacted security event and MUST work when no TOTP configuration exists.

See [Security and Compliance](SECURITY_AND_COMPLIANCE.md).

### 4.2 Candidate record

- The owner can maintain structured history, skills, languages, desired roles,
  experience level, employment types, locations, remote preferences, and other
  application-relevant facts.
- The owner can upload and version multiple resumes.
- Extraction, parsing, import, inference, and owner entry create unverified
  candidates or matching signals. Only an explicit owner action verifies a fact.

Candidate facts have stable semantic identities and immutable versions. Each
version records semantic key/scope, typed value, lifecycle state, source and
version, evidence citation, extraction method/confidence, confirmation,
creation/supersession/revocation times and reasons, sensitivity,
reconfirmation policy, and an integrity hash where appropriate.

Lifecycle states are `unverified`, `verified`, `stale`, `conflicted`, and
`revoked`. Editing creates a new unverified version. Only explicit owner
confirmation moves unverified or stale information to verified. Revocation
blocks all future use immediately but does not rewrite history. Source changes
never silently change verified values.

Reconfirmation policy:

- Completed education, prior employment, completed certifications, and
  completed projects do not expire automatically, but become stale after
  source change, owner edit, or revocation.
- Current contact/location/role, portfolio links, and active preferences require
  confirmation every 90 days.
- Work authorization, sponsorship, notice period, availability, relocation,
  and compensation expectations require confirmation every 30 days and again
  for an application that requests an attestation.
- Legal declarations, conflicts of interest, background-check consent, and
  personal certifications require confirmation for every exact payload.
- Voluntary demographic, disability, accommodation, veteran status, gender,
  ethnicity, and similar answers are never inferred/generated/reused, require
  confirmation per destination and attempt, and are not retained by default.

Reconfirmation is audited without rewriting earlier history. Absence of
evidence never becomes a negative fact.

Conflicting active values with the same semantic key and overlapping scope are
marked conflicted and blocked. Confidence, recency, majority agreement, and
model judgment cannot resolve them. The UI shows competing values, provenance,
dates, and affected drafts. Only the owner may select/reconfirm a value, provide
a corrected value, define non-overlapping scopes, or revoke obsolete versions;
the reason and result are audited.

Resume ingestion uses protected local storage outside Git. M1/M2 accepts only
PDF, DOCX, and UTF-8 plain text under D-024's tested safety limits. Originals
and resume versions are immutable; duplicate content preserves separate
provenance. Extraction is deterministic, cited, and never runs OCR or active
content. Any structured extraction is an **Unverified candidate**. Accepting it
creates an ordinary unverified fact, after which the separate explicit owner
verification workflow is still required. Authorized downloads use opaque IDs;
paths and public document URLs are prohibited.

### 4.3 Job discovery

The implemented catalog stores immutable provider payload versions separately
from normalized canonical-job versions, retains every provenance link, and uses
only owner-triggered bounded backend synchronization. Manual entry never fetches
its URLs. Until D-019 matching is implemented against persisted requirements,
catalog results display **Not evaluated** rather than fixture match values.

- Retrieve jobs only through approved, legally and technically supported
  sources.
- M1 approved read-only sources are Greenhouse Job Board API, Lever Postings
  API, Ashby Public Job Posting API, and Remotive Public Jobs API.
- Discover India-based roles, international remote work, overseas hybrid/on-site
  roles, relocation and sponsorship opportunities, internships, part-time,
  contract, and full-time roles. Never impose an India-only filter.
- Normalize source fields without losing original data or attribution.
- Deduplicate likely identical listings while retaining every source record.
- Display complete available details, source, original URL, retrieval time,
  and freshness state.
- Surface removed, stale, conflicting, and incomplete source data.
- Structure country, region, city, timezone, remote status, relocation
  requirements, work authorization, sponsorship, employment type,
  compensation/currency, language requirements, and employer/destination
  jurisdiction separately from the owner's operating jurisdiction.
- Preserve original URL, source, location, remote classification, employer, and
  all available eligibility language for every source listing.

The owner can select worldwide search; include/exclude/prefer countries and
cities; choose remote-only or remote-preferred; record relocation willingness,
acceptable timezones, sponsorship needs, employment types, minimum compensation
per currency, and language requirements.

Greenhouse, Lever, and Ashby retrieve only published jobs from explicitly
configured, owner-reviewed employer boards/slugs. The owner can add, inspect,
test, disable, and remove registry entries. ApplyPilot never crawls for boards
or trusts an ATS-looking URL alone. Invalid, redirected, repurposed, or
employer/domain-mismatched entries are disabled.

Each source record preserves source and posting ID, source URL, canonical
application URL when supplied, employer, board slug, retrieval/publication/
update timestamps, original location and remote classification, attribution,
raw-payload version/hash, and adapter version. Displayed jobs link to the source
or canonical employer destination and never identify ApplyPilot as publisher.
Remotive listings always show **Source: Remotive** and link to Remotive's URL;
they are not redistributed to publishing destinations.

LinkedIn, Indeed, Glassdoor, Naukri, Wellfound, Google Jobs results, social
media, arbitrary search results, and sites without an approved public API/feed
or permission are unsupported automated sources. Do not scrape, crawl,
reverse-engineer, replay browser calls, use authenticated cookies for mass
retrieval, or bypass login, CAPTCHA, robots, anti-bot, rate, paywall, or access
controls. A visible webpage is not approval.

The owner may manually enter URL, title, employer, location, description, and
other details. Display **Manually entered — source not automatically verified**.
Do not scrape its URL. Manual records can later reconcile with approved records
and participate in deduplication while retaining distinct provenance.

### 4.4 Matching

Matching is deterministic, explainable, versioned, and reproducible. An LLM may
extract structured requirements with source citations, but cannot assign the
final score, blocker, or eligibility state. Every contribution traces to an
exact cited job requirement, eligible verified fact version, scoring-rule
version, and weight-set version. Match output never predicts hiring, interview,
recruiter interest, candidate quality, or job performance; UI language uses
**match** or **alignment**, never “chance of being hired.”

Each match displays capability alignment (0–100), preference compatibility
(0–100), eligibility (`compatible`, `unclear`, or `blocked`), evidence coverage
(0–100), extraction confidence (`high`, `medium`, or `low`), and separate lists
of verified matches, partial matches, missing evidence, verified gaps,
uncertainties, confirmed blockers, and owner actions. A distinct overall
ranking score is used only for ordering and its derivation is visible.

Accepted capability weights are technical skills 35, experience/seniority 25,
role/responsibility 15, domain experience 10, and education/certifications 10.
These 95 relative points normalize into 85% of combined alignment. Preference
weights are employment type 4, location/workplace 4, compensation 4, and
timezone 3, totaling the remaining 15%.

Within each dimension, a full verified match is 1.0, verified partial match is
0.5, and verified contradiction/gap is 0.0. Unknown or insufficient evidence
is excluded from both alignment numerator and denominator and instead reduces
weighted evidence coverage. Absence from a profile or resume is never a
contradiction. Capability alignment uses only evaluable requirements;
preference compatibility uses the same known/unknown separation.

Combined alignment is `0.85 * normalized capability alignment + 0.15 *
preference compatibility`. Ranking uses `combined_alignment * (0.50 + 0.50 *
evidence_coverage)`, using fractional inputs. Combined alignment and coverage
are displayed separately. Below 40% capability evidence coverage, display
**Insufficient evidence** and missing facts instead of a precise combined
percentage. Display whole-number scores while retaining component precision and
the exact formula version.

Requirements retain type, mandatory/preferred/descriptive classification,
citation, extraction confidence, normalized concept, dimension, and weight.
Mandatory items receive three times preferred weight. Substantive descriptive
responsibilities may receive half preferred weight; marketing language,
benefits, equal-opportunity text, company descriptions, boilerplate, and generic
personality adjectives receive zero. Preferred wording cannot become mandatory.
Mandatory classification requires explicit cited language; low-confidence
classification is unclear pending owner review and cannot create a blocker.

Eligibility is separate from numerical alignment. Potential blocker dimensions
are authorization, sponsorship, mandatory location/presence, working language,
legal license, security clearance, employment type, and timezone/hours. A
confirmed blocker requires a cited explicit mandatory posting requirement,
sufficient extraction confidence or owner review, and a current verified fact
that directly contradicts it, with both citations. Missing facts, ambiguity,
inference, and preferred requirements cannot create blockers. Blocked jobs stay
searchable and show capability, exact evidence, and possible owner action.
Overrides preserve the original result plus reason, time, and view preference.

Inferred signals may improve discovery recall and appear only as **Possible
relevance**. They never contribute to verified capability, satisfy a
requirement, establish or clear a blocker, or enter application content. The
owner may confirm a candidate through D-015, creating a verified fact.

Extraction confidence describes parsing confidence only. High means explicit
unambiguous text, medium means some ambiguity, and low produces a warning and
cannot create a blocker without owner review. Preserve source text and
rationale. Changed job content invalidates affected requirements and produces a
new match version.

Never score or rank on protected traits or proxies, including name, photograph,
age/birth date, gender, sexual orientation, race, ethnicity, caste, religion,
family/marital/pregnancy status, disability/medical data, veteran status,
political beliefs, genetic/biometric data, inferred nationality, socioeconomic
proxies, address prestige, employer prestige, school prestige, or protected-
trait proxies. Citizenship/nationality are not proxies; confirmed authorization
and sponsorship affect only eligibility. Graduation year is not an age proxy;
employment gaps and career changes receive no generic penalty. Compensation
affects preferences only. Source identity and employer/university prestige add
no score. M1 never learns weights from application outcomes.

The UI never reduces a job to one unexplained percentage. Every component
expands to evidence and distinguishes verified gap, unknown, inferred
possibility, and confirmed blocker. It explains ranking differences and offers
an audited owner correction path that creates a new match version. Score-only
celebratory or discouraging language is prohibited.

The accepted defaults are immutable configuration versions. The owner may
later adjust preference weights only within documented limits; capability
weights cannot be silently changed by an AI. Every change creates a new weight
set, older-version status is displayed, recalculation appends a match version,
and application history retains the match shown at approval and submission.

### 4.5 Generated materials

- Generate cover-letter drafts, application-email drafts, resume suggestions,
  and form-answer drafts only from verified candidate facts.
- Cite or internally link each factual claim to supporting fact records.
- Omit unsupported claims or present them as unresolved draft issues. Inferred
  information never appears in resumes, letters, emails, form answers,
  certifications, or submissions.
- Mark unanswered questions and uncertain mappings for owner input.
- Preserve provider/model, prompt-template, input-fact, and output versions.

### 4.6 Review, approval, and submission

- Present the complete destination, fields, answers, documents, and required
  consents before approval.
- Final Apply MUST be an explicit action separate from saving or generating.
- Store an immutable canonical snapshot and digest of the approved payload and
  destination.
- Bind approval to the exact payload, supporting fact-version IDs, destination,
  and attempt, and preserve application-time fact snapshots with history.
- Before Final Apply, validate every claim and answer against eligible verified
  versions and display supporting facts and provenance. Block approval for any
  required unsupported, stale, conflicted, revoked, or unverified answer.
- Reject submission if the current payload or destination differs materially
  from the approved snapshot.
- Invalidate approval when a supporting fact changes, becomes stale,
  conflicted, or revoked, or when conflict resolution affects the payload.
- Record every attempt, including validation failure, cancellation, timeout,
  ambiguous outcome, source rejection, and success.
- Never retry a submission automatically under an earlier approval unless the
  retry semantics are explicitly accepted later.
- M1 source approval covers discovery only. “Apply” opens the controlled
  Application Studio to prepare a package; it does not submit through any source
  API. Never show submission success without a destination receipt or an
  owner-confirmed outcome.

### 4.7 Tracking

- Show application history and status changes with timestamps and origins.
- Preserve owner-entered, source-reported, and submission-derived events as
  distinguishable evidence.

### 4.8 Backup and restoration

- Create versioned backup bundles encrypted with age public-key encryption.
- Include a consistent PostgreSQL dump, required owner/generated documents,
  and a versioned manifest with inventory, sizes, timestamps, and checksums.
- Exclude sessions, tokens, temporary files, caches, logs, plaintext secrets,
  environment files, and unnecessary artifacts.
- Preserve credential state, profile data, job provenance, application history,
  approvals, submission attempts, and audit events.
- Write backups outside the repository and live database/document storage. M1
  performs no cloud upload; encrypted copies may be placed on an external drive
  or in an owner-configured OneDrive-synced folder.
- Restore only through a confirmed local-shell operation with services stopped,
  isolated validation, all-or-nothing database/document replacement, session
  revocation, and a redacted post-start restore event.

### 4.9 Retention, export, and deletion

Default live-data retention is:

- active profile, current resumes/preferences/facts: while active, until
  superseded, revoked, or owner-deleted;
- superseded fact/resume versions: 24 months, except while referenced by an
  application, approval, generated claim, conflict, or audit event;
- unsaved/unacted jobs: 180 days after last observation;
- saved jobs without applications: two years after closure/last observation,
  unless pinned or owner-deleted;
- abandoned unsubmitted drafts: 180 days after last modification and warning;
- submitted application payloads, fact snapshots, receipts, and status: five
  years after final status, with owner extension, export, or deletion available;
- security/administrative audits: one year, except while linked to an unresolved
  incident, restore investigation, or application-integrity issue;
- operational logs: at most 30 days with secrets/personal content redacted;
- temporary parsing/generation/upload data: immediate success/failure cleanup;
- inferred signals: until their source is deleted or they are replaced.

Source terms may shorten these defaults. The stricter source/destination rule
wins and cannot silently extend owner-selected retention. Timers use explicit
timestamps and auditable jobs, never startup or page visits.

Unsubmitted per-attempt sensitive answers are removed within 30 days of draft
abandonment. Submitted sensitive answers remain visibly marked within the exact
payload and follow application retention. Do not collect them speculatively.

The owner can preview dependencies, export, trash, or permanently delete jobs,
drafts, documents, facts/signals, generated artifacts, applications/payloads,
and eligible audit data. Default trash is recoverable for 30 days; sensitive
data may be permanently deleted immediately. Permanent deletion covers live
records, files, indexes, caches, derived values, and orphaned artifacts and
leaves only a minimal redacted tombstone.

Deleting a reusable fact never corrupts a submitted application: the owner
chooses to retain its application-local immutable snapshot or delete the whole
application and snapshots. Restores reapply newer tombstones before serving.
Existing encrypted backups expire under D-014 and need not be surgically edited;
the UI explains this bounded residual and offers export before destruction.

## 5. Quality requirements

- Private data is protected at rest, in transit between local components, in
  logs, and in backups as defined in
  [Security and Compliance](SECURITY_AND_COMPLIANCE.md).
- Critical state changes are transactional and recoverable.
- Accessibility target is WCAG 2.2 AA for primary workflows.
- Dates are stored in UTC and displayed with an explicit local timezone.
- Failures are visible and actionable; ambiguous submission results are never
  reported as success.

## 6. Milestone-one acceptance criteria

Documentation is complete when all eight planned files exist, cross-reference
the permanent invariants, label unresolved choices, pass `git diff --check`,
and contain no accidental additional-account or hosted-service assumptions.

The first executable milestone, once separately approved, will be accepted
when automated tests demonstrate:

- 100% of 20 concurrent first-run attempts result in exactly one owner row.
- No account-creation route is usable after setup.
- Valid login, invalid login, throttling, CSRF rejection, logout, idle expiry,
  and absolute expiry paths pass.
- First-run and recovery tests confirm that no TOTP secret or recovery-code
  material is generated.
- Route and UI inventories confirm that no MFA enrollment, verification,
  reset, recovery, advertisement, or capability claim is exposed.
- No state-changing endpoint accepts a missing or invalid CSRF token.
- A changed field, document, or destination causes approved submission to be
  rejected in every test case.
- Every attempted submission creates one durable attempt record with a result.
- Generated factual sentences used in an application trace to verified facts;
  unsupported-fact test cases are blocked.
- Lifecycle, expiry, attestation, conflict, revocation, inference-separation,
  sensitive-answer, and approval-invalidation test matrices pass in every
  specified case.
- Each displayed job links to at least one retained source record.
- The application binds only to configured loopback addresses.
- Canonical setup, development, test, migration, backup, and recovery commands
  execute through Docker Compose.
- PostgreSQL data survives container recreation through a named volume, and
  private documents persist in protected local storage or a dedicated volume.
- Health checks and readiness ordering prevent dependent services from being
  treated as ready prematurely.
- Backup/restore tests verify age encryption, manifest checksums, excluded
  session/secret data, required history, failure rollback, and retention of 7
  daily, 4 weekly, and 6 monthly verified backups without deleting the last
  known-good bundle.
- One documented isolated backup-and-restore drill succeeds before M1
  acceptance and is repeated after material schema or backup-format changes.
- Retention tests cover every deadline, pin/dependency, source cap, trash or
  permanent path, export, atomic database/file cleanup, redacted audit, and
  submitted-application protection.
- Restore tests prove tombstones newer than the backup prevent deleted data from
  being resurrected before requests are served.

Later milestone criteria are in
[Development Roadmap](DEVELOPMENT_ROADMAP.md).

## 7. Unresolved decisions

- Whether the initial product stops at an application package or directly
  submits to any destinations.
- Direct-submission destinations, retry semantics, and approval lifetime.
- Additional sensitive fields, beyond D-015's named categories, that require
  confirmation for every application.
- AI provider, data-retention terms, and permitted data disclosure.
- Application-status sources and retention periods.

## 8. Deferred capabilities

- Remote access or public hosting
- Browser extension
- Redis-backed task processing
- S3-compatible object storage
- Podman, Kubernetes, and cloud deployment
- TOTP/MFA implementation and activation
- Direct submissions not individually approved as supported integrations
- Adzuna, pending an API account, current terms/attribution/country/quota/
  caching/retention review, India and target-country coverage tests, and source
  contract tests
- Arbeitnow, pending recorded API-use and attribution rules for its focused
  Germany/visa/relocation use case
- USAJOBS, pending a separate federal-opportunity evaluation
- Automated follow-up sending

A free API key does not approve a source. Every future source requires a new
accepted decision and adapter-specific compliance profile.
