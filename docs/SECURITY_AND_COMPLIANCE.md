# Security and Compliance

## 1. Security posture

ApplyPilot protects highly sensitive employment, identity, credential, and
document data even though its initial deployment is loopback-only. Local
operation reduces network exposure but does not make local processes, browser
extensions, malware, backups, logs, or supply-chain dependencies trustworthy.

The permanent safety invariants in [Product Requirements](PRODUCT_REQUIREMENTS.md)
are security boundaries, not optional UX behavior.

## 1.1 Legal scope assumption

Initial operation is in India because the owner and local Fedora runtime are in
India. Job discovery is worldwide, while use remains personal/domestic. This
engineering assumption is not legal advice or
a certification of compliance with every Indian law, GDPR/UK GDPR, destination
employment law, job-source term, or employer requirement.

Foreign-destination applications do not make ApplyPilot public, but their forms,
declarations, transfers, and platform terms still apply. Source/destination
restrictions override defaults when stricter. D-018 and each adapter's recorded
compliance profile govern source API, license, attribution, storage, and
retention terms.

Reopen legal scope before public, multi-user, commercial, remote/non-loopback,
employer/recruiter, multi-person analytics, high-volume automated use, or
processing another person's profile.

Worldwide discovery does not establish worldwide eligibility. Never infer
citizenship, nationality, visa status, work authorization, protected
characteristics, or relocation willingness. Posting requirements may be quoted
or explained with provenance, but uncertain immigration or authorization cases
remain labelled for owner verification; ApplyPilot does not determine legal
immigration eligibility.

International applications must respect destination forms/declarations and
data-transfer requirements, employer requirements, platform terms, and
applicable authorization/immigration rules. The stricter applicable restriction
wins. This does not certify universal legal, employment, immigration, privacy,
or platform compliance.

## 2. Data classification

- **Secrets:** owner password verifier, session tokens, CSRF secrets,
  encryption keys, OAuth tokens, and API credentials. Future TOTP secrets and
  recovery codes join this class if TOTP is later activated; none exist in M1.
- **Highly sensitive private data:** resumes, application answers, contact
  details, work authorization, demographic or accommodation information,
  submitted payloads, generated documents.
- **Private operational data:** profile facts, preferences, matches, job notes,
  application status, audit events.
- **Source data:** job listings and provenance, subject to source-specific terms
  and retention rules.

Secrets never appear in Git, URLs, analytics, routine logs, or plaintext audit
metadata. Private owner data and real resumes never appear in repository
fixtures or snapshots.

## 3. Authentication and sessions

**Accepted decisions**

- First-run setup creates exactly one owner and is transactionally disabled
  afterward.
- Password hashing uses Argon2id. Parameters are stored with the verifier and
  upgraded after successful authentication when policy changes.
- Sessions use cryptographically secure opaque tokens with at least 256 bits of
  entropy. The raw token goes only to the browser; PostgreSQL stores only a
  cryptographic hash. JWT browser authentication is prohibited.
- The cookie is named `applypilot_session` and uses `HttpOnly=true`,
  `SameSite=Strict`, `Path=/`, and no `Domain` attribute. M1 permits
  `Secure=false` only for loopback HTTP; future HTTPS/non-loopback operation
  requires `Secure=true`. Cookie lifetime never exceeds absolute server expiry.
- Session tokens never appear in `localStorage`, `sessionStorage`, URLs, or
  application logs.
- Every state-changing request requires a session-bound custom-header CSRF
  token with at least 256 bits of secure entropy plus exact Origin validation.
  SameSite is defense in depth, not a replacement.
- Login uses persistent D-020 exponential backoff and generic failures without
  permanent account lockout.
- Logout revokes the server session. Idle and absolute expiration are enforced
  server-side.
- Password changes revoke existing sessions. Future TOTP changes must do so if
  TOTP is later activated.

**Accepted M1 session parameters**

- Idle expiry is 60 minutes and absolute expiry is 12 hours from authentication.
  Activity extends only idle expiry. M1 has no Remember me.
- Allow three active sessions. Creating a fourth revokes the least recently
  active. The owner can inspect non-invasive labels/times and revoke one or all
  other sessions.
- When practical, warn five minutes before idle expiry. Expiration returns to
  login without putting sensitive form state in browser storage or URLs;
  authenticated backend drafts preserve unsaved application work.
- Raw session and CSRF values never enter Web Storage, URLs, JavaScript-readable
  state, application logs, audit payloads, or full browser fingerprints.

**Implemented password parameters:** D-023 accepts Argon2id with 65,536 KiB
memory, time cost 8, parallelism 2, 32-byte hash, and 16-byte salt. The
Docker-based benchmark averaged approximately 289 ms on the owner's Fedora
machine. Password input is length-focused: 12–1024 characters, no composition
rule, no truncation, and double entry during initialization and recovery.
Verifier comparison uses the Argon2 library's safe verification path.

### Login and request throttling

PostgreSQL tracks consecutive failures for the owner and loopback source
context. Failures 5–10 impose 30, 60, 120, 240, 480, and then at most 900
seconds; later failures remain capped at 900 seconds. Success resets the count.
Local-shell recovery remains usable while HTTP login is throttled and does not
erase security history.

Authenticated APIs allow 300 requests per rolling five minutes per session.
Expensive owner operations allow 10 per minute per session. Initialization
allows three attempts per five minutes and becomes permanently unavailable
after success. Only one source synchronization per adapter runs; repeats
coalesce or report the existing job. Authentication uses its separate backoff.
Rate-limit responses use HTTP 429 and safe `Retry-After` without private state.
Generation limits remain under U-008; external-submission limits remain under
U-002. Minimal liveness may be unauthenticated, but administrative health data
cannot bypass authentication.

Create a session only after successful authentication. Rotate the CSRF token
when replacing a session. Password change, local recovery, restore, any future
factor change, and suspected compromise revoke or replace affected sessions.
Possession of a cookie never overrides server expiry, revocation, or credential
version. Session activity writes occur at most once per five minutes while the
effective idle deadline is enforced on every request.

Security events distinguish successful, failed, and throttled login; logout;
expiry; manual revocation; global invalidation; and credential-version
invalidation. They contain no submitted password, session/CSRF value, or
unnecessary private state. Generic failures do not reveal setup, password,
session, or throttle state.

## 3.1 Milestone 1 transport policy

Milestone 1 uses plain HTTP strictly over loopback. Only Next.js publishes by
default, at host `127.0.0.1:3000`; it proxies same-origin `/api` requests to
FastAPI through the private Docker network. FastAPI, PostgreSQL, and the worker
have no default host publication. Container-internal listeners may use
`0.0.0.0` for private-network communication; host publication on `0.0.0.0`, a
LAN address, or a public interface is prohibited. A FastAPI host port exists
only in an explicit loopback debugging profile.

The sole browser-visible origin is `http://127.0.0.1:3000`. Host and Origin
validation, cookies, and CSRF rules use that exact origin. LAN access, public
ingress, ordinary port forwarding, and remote access are prohibited.

Any future non-loopback configuration requires HTTPS and `Secure=true` session
cookies. Configuration validation MUST fail closed before serving requests if
either condition is missing. Locally trusted HTTPS is deferred until remote or
non-loopback access is intentionally introduced and receives a new security
review.

## 3.2 Local-shell password recovery

**Accepted decision:** password recovery exists only as a dedicated CLI command
run from the local ApplyPilot project/runtime environment. The authorized
recovery principal is the person who controls the local Fedora OS account and
has authorized access to the ApplyPilot runtime and database. There is no
forgot-password page or HTTP endpoint and no email, SMS, security-question, or
remote recovery flow.

The command MUST:

- read the new password twice through hidden input and require an exact match;
- enforce the same password policy as first-run setup;
- atomically replace the Argon2id hash, revoke every active session, and append
  a security event;
- keep the existing hash and all sessions unchanged on any validation,
  database, or audit-write failure;
- use generic failure messages and never emit a password, hash, token, recovery
  secret, or unnecessary personal data; and
- avoid accepting the password through command arguments, environment
  variables, files, URLs, or other observable channels.

M1 password recovery requires no TOTP record and exposes no TOTP reset option.
If TOTP is activated later, password reset still must not implicitly reset it.
A future TOTP reset requires a separate explicit option, a high-visibility
warning, and an additional confirmation; success invalidates the TOTP
credential, every recovery code, and every active session and creates its own
redacted security event.

Backups are not a password-recovery mechanism. They follow the accepted
encrypted backup and isolated restoration policy below; password reset remains
the only recovery path for a lost owner password.

## 4. Deferred TOTP design

TOTP is designed for future compatibility but is not implemented, configured,
advertised, generated, or enabled in M1. The owner password is the only
application-level authentication factor; Fedora OS access remains part of the
local trust boundary. First-run setup and password recovery generate no TOTP
secret or recovery code. M1 includes no MFA enrollment, verification, reset, or
recovery UI or HTTP route, including dormant or unreachable placeholders, and
must not claim MFA support.

Future activation requires a documented threat-model review; enrollment and
verification workflows; encrypted secret storage; high-entropy, single-use
hashed recovery codes; reset and disable procedures; session invalidation;
migration and rollback procedures; and dedicated tests. Any future non-loopback
or remote-access proposal must reopen this decision before implementation.

Future enrollment must require recent password authentication, show a secret
only as required for enrollment, and activate only after verification. Future
reset remains a separate explicit action and invalidates sessions and recovery
codes. Current service and schema boundaries may preserve a clean migration
path but cannot require TOTP records to exist.

## 4.1 Source-access boundary

D-018 approves discovery through only the documented public Greenhouse Job
Board, Lever Postings, Ashby Public Job Posting, and Remotive Jobs interfaces.
Adapters are read-only: they cannot authenticate as the owner, create candidate
records, submit applications, or call employer-side, partner, administrative,
candidate, private, or undocumented APIs. Greenhouse Harvest and Candidate
Ingestion, Lever Data and candidate APIs, and authenticated Ashby APIs are
outside the M1 boundary.

LinkedIn, Indeed, Glassdoor, Naukri, Wellfound, Google Jobs results, social
media, arbitrary search results, and any site lacking an approved public
API/feed or explicit permission are unsupported automated sources. ApplyPilot
must not scrape, crawl, reverse-engineer, replay copied browser endpoints, use
owner cookies for bulk retrieval, or bypass authentication, CAPTCHA, robots,
anti-bot controls, rate limits, paywalls, consent, or access restrictions.

Greenhouse, Lever, and Ashby access is limited to explicitly configured,
owner-reviewed boards in the employer-board registry. A board is disabled if
its verified company domain, employer, redirect behavior, or identifier no
longer matches. Remotive-derived views must show “Source: Remotive,” preserve
its supplied URL, and must not redistribute the listing to another publishing
destination. Manual records remain visibly unverified and their URLs are never
fetched automatically.

Per-source documented terms, attribution, rate, caching, refresh, storage, and
retention restrictions are recorded in a versioned compliance profile and
override general defaults when stricter. Future credentials remain outside Git.
Adding a source requires a new decision, current terms review, and
adapter-contract tests; public visibility or a free API key alone is not
approval.

## 4.2 Matching integrity and fairness

D-019 makes scoring deterministic domain logic. An LLM may extract cited job
requirements but cannot determine final scores, eligibility, or blockers.
Unknown profile data is never converted to a contradiction. A blocker requires
a cited mandatory requirement and a directly contradictory current verified
fact; ambiguity, low-confidence unreviewed extraction, missing data, preference,
or inference cannot create one.

Matching and ranking cannot consume name, photograph, birth date/age,
graduation year as an age proxy, gender/identity, sexual orientation, race,
ethnicity, caste, religion, marital/family/pregnancy status, disability/medical
data, veteran status, political belief, genetic/biometric data, inferred
nationality, socioeconomic or protected-trait proxies, address/employer/school
prestige, employment gaps, or generic career-change penalties. Missing
demographics never reduce a score. Confirmed work authorization and sponsorship
are restricted to eligibility; compensation is restricted to preferences;
source identity does not confer quality.

Prohibited-feature and perturbation tests must prove that changing or removing
protected fields, names, photographs, dates of birth, graduation years,
addresses, or demographics leaves every match and ranking output unchanged.
Authorization changes may alter only explained eligibility; compensation only
preferences; source changes alone cannot alter results for identical normalized
content. M1 never learns weights from employer outcomes.

## 5. Storage, secrets, and logging

**Recommended MVP defaults**

- Store documents outside the repository in an owner-only directory using
  unpredictable internal identifiers and restrictive permissions.
- Validate content type, size, extension, and parser behavior; never execute
  document content or trust supplied filenames.
- Store document digests and scan/extraction state in PostgreSQL.
- Keep secrets in owner-protected ignored files or Docker secret mounts.
- Redact authorization headers, cookies, tokens, passwords, full application
  answers, and document content from logs.
- Use synthetic test data and run secret scanning before commits.

### Backup encryption and key handling

Every final backup is a versioned bundle encrypted using age public-key
encryption. An unencrypted final backup is prohibited. Restrict permissions on
temporary plaintext staging and remove it on both success and failure. Never
pass a private key or passphrase through command-line arguments, logs, Git
configuration, committed files, or other observable channels.

The age private identity remains outside Git, the repository, application
database, backup bundle, and backup destination. The owner maintains an offline
copy. Loss of the identity makes encrypted backups unrestorable; the system and
documentation must state this plainly.

### Backup location and retention

Write encrypted bundles only to a configurable path outside the repository,
live PostgreSQL storage, and live document storage. ApplyPilot performs no M1
cloud upload. The owner may copy encrypted bundles to an external drive or a
OneDrive-synced folder, and at least one copy should be physically distinct from
live data.

Retain 7 daily, 4 weekly, and 6 monthly verified bundles. Never delete the last
known-good bundle. Cleanup runs only after successful creation, encryption,
manifest/checksum verification, and destination persistence of a new bundle.
A verified backup is required before any data-altering schema migration.

Individual records need not be rewritten inside existing encrypted backups.
Deleted content may remain inaccessible there only until D-014 rotation expires;
the deletion UI discloses this. Restore reapplies newer tombstones before
serving so an older bundle cannot resurrect permanently deleted content.

### Restore controls

Restore is a local-shell-only administrative action through Docker Compose; it
is not password recovery and has no HTTP/UI entry point. Stop application
services, display the selected backup timestamp and target, and require explicit
confirmation. Decrypt into a restrictive isolated target; verify manifest,
checksums, format/schema compatibility, database readability, and document
consistency before replacement.

Replace database and documents only as one unit and preserve the previous live
state until validation passes. A failed restore leaves that state recoverable.
Discard/revoke every session before serving the restored application, then
append a redacted restore security event after successful startup. Complete and
document one isolated drill before M1 acceptance and repeat it after material
backup-format or schema changes.

## 6. External providers and source compliance

Every adapter requires a documented authorization basis, supported access
method, terms review, attribution rules, permitted retention, rate limits,
credential method, and shutdown behavior before enablement. For future approved
authenticated integrations, prefer official APIs or OAuth over storing
third-party passwords. D-018 discovery uses only its documented public
interfaces and never owner-authenticated browser sessions or cookies.

ApplyPilot MUST stop and require owner action when faced with a CAPTCHA,
anti-bot control, new authentication or consent prompt, unsupported workflow,
or terms conflict. It must not disguise automation, rotate identities to evade
limits, or replay consent. Source and destination identifiers remain attached
to all resulting records.

AI providers receive the minimum necessary verified facts. Provider selection,
retention/training terms, regional processing, and permission to disclose
candidate data are unresolved.

### Verified-fact and sensitive-answer controls

Only an explicit authenticated owner action can verify or reconfirm a fact.
Extraction/import/inference services have no permission to perform that
transition. Owner-entered values begin unverified. Multiple agreeing sources do
not change this rule, and absence of evidence never becomes a negative fact.

Generation receives only eligible exact verified versions. Inferred matching
signals are labelled and isolated from generation/submission paths. Conflict
resolution cannot use confidence, newest source, majority agreement, or model
judgment. Stale, conflicted, revoked, and unverified data is fail-closed.

Voluntary demographic, disability, accommodation, veteran-status, gender,
ethnicity, and similar answers are never inferred or generated from resumes,
never automatically reused, and require explicit confirmation per destination
and attempt. They are not retained by default. Unsubmitted answers are removed
within 30 days after draft abandonment; submitted answers follow the five-year
application default, remain visibly marked, and can be owner-deleted with
displayed integrity dependencies. Never collect them speculatively.

### Retention and deletion safety

Automatic cleanup begins with a dry-run report, preserves pins/holds and stricter
source obligations, runs transactionally where possible, prevents file/database
divergence, and writes a redacted event. It cannot delete an in-window submitted
application without explicit owner action. Policy changes are prospective absent
an explicitly approved migration plan.

Default deletion uses 30-day trash; sensitive data supports explicit immediate
permanent deletion. Permanent deletion covers records, files, search indexes,
caches, derived data, and orphaned generated content and retains only a minimal
redacted tombstone. Export is available before destruction. Tombstones contain
no deleted content and survive or are merged across restore boundaries.

## 7. Submission control and audit integrity

The backend canonicalizes and hashes the complete payload and destination.
Final Apply records that exact snapshot. Immediately before external action,
the backend verifies authentication, CSRF, approval validity, destination, and
payload digest, including exact eligible supporting fact versions. Supporting
fact edits, staleness, conflicts, revocation, or conflict resolution invalidate
affected approval and require review and new approval.

An attempt record is durably created before external interaction. Responses,
timeouts, and ambiguous outcomes append evidence. Logs may be redacted, but the
protected audit record must preserve the exact submitted values or protected
references needed to reconstruct them. Retry authorization remains unresolved
and defaults to new approval.

## 8. Local deployment controls

- Docker Compose is the sole supported and acceptance-tested Milestone 1
  runtime and canonical operational interface.
- For M1, publish only Next.js by default at host `127.0.0.1:3000`; proxy `/api`
  to FastAPI on the private network. Do not publish FastAPI except through an
  explicit loopback-only debugging profile.
- Do not publish PostgreSQL or worker ports. Container-internal `0.0.0.0`
  listeners are allowed when needed and are not public exposure.
- Keep service communication on a private Docker network.
- Pin Node.js, Python, PostgreSQL, toolchain, dependency, and image versions and
  perform vulnerability review before releases.
- Run application containers as non-root wherever practical. Map container
  identity and mount permissions so bind-mounted files do not become
  root-owned on Fedora.
- Persist PostgreSQL in a named volume and private documents in protected local
  storage or a dedicated volume with least privilege.
- Store secrets only in ignored local environment files or an equivalent local
  secret mechanism. A committed `.env.example` contains names and safe
  placeholders only.
- Require health checks and readiness-aware dependent startup.
- Document a secure update, backup, and restore process before relying on the
  system for irreplaceable records.

Native Fedora commands are debugging aids only. Podman, Kubernetes, cloud
deployment, public hosting, and remote access are deferred.

Remote access is deferred and cannot be enabled merely by changing a bind
address. It requires a new threat model, transport security, proxy/header
review, firewall configuration, and owner approval.

## 9. Compliance and privacy decisions still required

- Source-specific terms and permitted content storage
- AI/subprocessor choices and data-processing terms
- Handling of highly sensitive application questions
- Incident response and breach-notification procedure
- Whether audit evidence is encrypted field-by-field and how keys are recovered
