# Database Schema

## 1. Modeling principles

PostgreSQL is the system of record. The schema models one owner directly; it
does not add generic account ownership columns to domain tables. Historical
truth uses immutable versions and append-oriented events. Files are stored
outside the database under protected local storage, with metadata and
cryptographic digests stored here.

Most of this document remains the forward-looking logical schema. Section 2's
M1 authentication subset is implemented by Alembic revision
`20260902_0001_owner_authentication`; later records remain subject to review.
See [Architecture](ARCHITECTURE.md).

## 2. Security and setup records

| Record | Purpose and key constraints |
| --- | --- |
| `installation` | Exactly one row; setup state, schema/application version, initialization timestamp. |
| `owner_account` | At most one row; login identifier, Argon2id hash, credential version, created/changed timestamps, disabled state. Credential version changes on password reset. |
| `sessions` | Cryptographic hash of an opaque token with at least 256 bits of source entropy; creation, last activity, idle/absolute expiry, revocation time/reason, credential version, and optional non-sensitive local client label. Raw tokens and full fingerprints are prohibited. Supports authoritative expiry, individual/global revocation, and the three-session cap. |
| `session_csrf_tokens` | Session-bound cryptographic token hash or equivalent verifier, creation/rotation/expiry metadata; at least 256 bits of source entropy and no raw token in audit data. |
| `totp_credentials` | Future optional design: encrypted TOTP secret, enrollment and confirmation timestamps. Not created or populated in M1. |
| `totp_recovery_codes` | Future optional design: individually hashed one-use codes, consumption time, and invalidation time/reason. Not created or populated in M1. |
| `login_rate_limits` | Durable singleton owner/loopback-context consecutive-failure count, last failure, blocked-until time, and reset metadata implementing D-020's capped exponential backoff across restarts. |
| `request_rate_limits` | Deferred logical record for general/expensive-operation and adapter throttles when those operations exist; not created by the authentication migration. |
| `security_events` | Append-only successful/failed/throttled login, logout, expiry, manual revocation, global invalidation, credential-version invalidation, setup, recovery, credential, and future-TOTP events. Contains time, outcome, reason class, and minimal non-secret metadata; never a password, hash, session/CSRF token, recovery secret, or unnecessary personal data. |

The one-owner rule MUST have a database-enforced singleton constraint and a
transactional initialization path; application checks alone are insufficient.

Local password recovery MUST replace the password hash, increment the
credential version, revoke every session, and append the redacted
`security_events` record in one transaction. Any failure rolls back the entire
transaction and MUST not require a TOTP record to exist. M1 contains no TOTP
configuration or reset behavior. In a future TOTP-enabled migration, a separate
confirmed reset transaction must invalidate the TOTP credential, all TOTP
recovery codes, and every session and append its own redacted event. Password
reset alone never changes TOTP state.

TOTP-compatible tables may be deferred to the future migration that activates
the feature. If their definitions exist earlier, they must remain optional and
empty and must not cause dormant routes or behavior to exist.

The implemented singleton constraints require `installation.id = 1` and
`owner_account.id = 1`; primary keys and check constraints therefore enforce
exactly one installation row and at most one owner row. Initialization also
locks the singleton transaction and takes a PostgreSQL transaction-scoped
advisory lock, so concurrent requests cannot create a second owner. Unique
indexes cover session and CSRF token hashes. Session foreign keys cascade CSRF
verifier cleanup, while owner deletion is restricted. Security events expose
no application update/delete path and are append-only in service behavior.

Session creation occurs only after successful authentication. Database/service
constraints enforce 60-minute idle and 12-hour absolute expiry, credential-
version validity, and at most three active sessions; a fourth creation revokes
the least recently active session transactionally. Activity may extend only the
idle deadline. Last-activity persistence is coalesced to no more than once per
five minutes without weakening effective expiry checks. Password change,
recovery, restore, future factor change, and suspected compromise invalidate
the applicable sessions.

## 2.1 Backup and restore classification

The consistent database dump MUST include `installation`, `owner_account`,
candidate/profile/preferences records, document metadata, job sources and
provenance, matching/generation history needed by retained applications,
application payloads and approvals, submission attempts/fields/documents/events,
status events, audit events, and other durable configuration required to
interpret them.

The dump MUST exclude `sessions`, session-token material, temporary work claims,
cache tables, and runtime-only state. Login-rate-limit state may be reset rather
than restored. Plaintext secrets and environment configuration are never stored
in the dump. Necessary credential state means the Argon2id verifier and its
parameters/version, not plaintext credentials.

Document metadata and every history record that references a document version
must remain consistent with the bundle's file inventory and checksum. Restore
validation rejects missing, additional where prohibited, or digest-mismatched
required files. Database and document data form one restore unit.

After restore, no pre-backup session may be usable. The restore process starts
with an empty `sessions` set (or transactionally revokes any reconstructed
session state) and increments or otherwise enforces a global session-validity
boundary before serving authenticated requests. Once startup succeeds, a
redacted `security_events` restore event records backup timestamp,
backup-format/schema versions, outcome, and non-secret correlation metadata.

## 3. Candidate facts and documents

| Record | Purpose and key constraints |
| --- | --- |
| `candidate_profiles` | Implemented singleton structured profile; section updates are timestamped and audited. Application-time snapshots remain future work. |
| `candidate_fact_identities` | Implemented canonical identity with owner, fact type, semantic key, scope, and creation time; unique owner/key/scope and no factual value. |
| `candidate_fact_versions` | Implemented unique identity/version rows with typed value, lifecycle projection, provenance, extraction metadata, confirmation/supersession/revocation data, sensitivity, reconfirmation policy/due time, and integrity hash. A trigger prevents in-place value/identity/version/hash changes. |
| `candidate_preferences_versions` | Worldwide mode; included/excluded/preferred countries/cities; remote mode; relocation; timezones; sponsorship; employment types; minimum compensation by currency; language requirements; desired roles/skills/seniority. |
| `resumes` | Implemented owner resume identity, display label/purpose, current-version pointer, archive/trash/purge state, and creation time. |
| `stored_documents` | Implemented random protected-storage key, detected media type/format, byte size, SHA-256 content identity, integrity state, and deletion time. Paths are never API values. |
| `resume_versions` | Implemented immutable resume/version allocation and document reference with sanitized filename, parser/version, extraction state, and lifecycle timestamps. Unique `(resume_id, version_number)` and a trigger protect history. |
| `document_extractions` | Implemented protected text, statistics, warnings, result/failure class, extraction time, and integrity digest for one exact resume version. |
| `resume_fact_candidates` | Implemented deterministic unverified proposal, exact version citation, method/confidence, review state/time, and resulting unverified fact reference after acceptance. |
| `document_lifecycle_events` | Implemented append-oriented validation, extraction, duplicate, review, trash, restore, and deletion events with redacted metadata. |
| `candidate_fact_evidence` | Implemented links from exact fact versions to source identifiers/versions and citations. Evidence never verifies a fact. |
| `candidate_fact_confirmations` | Implemented owner verification/reconfirmation/conflict-resolution action, exact version, owner, and time. |
| `candidate_fact_lifecycle_events` | Implemented append-only transition history with event, reason, and time. |
| `candidate_fact_conflicts` | Implemented same-key overlapping-scope conflict, detection/status, and owner resolution time/reason. |
| `candidate_fact_conflict_members` | Implemented exact competing version membership without destructive cascades. |
| `inferred_matching_signals` | Separate labelled inference, evidence, method/model, confidence, and validity; never a candidate fact or submission input. |

States are `unverified`, `verified`, `stale`, `conflicted`, and `revoked`.
Database transition constraints and service authorization permit only explicit
owner confirmation to produce `verified`. Editing produces a new unverified
version. Typed values and identity/version/hash fields are never updated.
Lifecycle projections change only alongside append-only confirmation or
lifecycle records. Confirmation, reconfirmation, staleness, conflict,
supersession, and revocation append events.
The effective state is derived or transactionally projected from that event
history while the immutable version and every prior transition remain intact.

Eligibility queries reject every state except currently verified and enforce
90-day, 30-day, attestation, and per-payload policies. Conflict detection uses
semantic key plus overlapping scope. Resolution never uses confidence, recency,
majority agreement, or a model; it records the owner's selected/corrected/scoped
or revoked result and reason.

Resume values and originals are immutable after successful ingestion. Duplicate
bytes may support distinct versions without losing separate provenance. Row
locking plus the unique version constraint protects allocation. An accepted
candidate blocks destruction of its evidence; bytes are removed only after the
last retained version releases them. Candidate acceptance creates a normal
unverified candidate-fact version and cannot call verification.

## 4. Jobs and provenance

Revision `20260902_0004` implements `ats_registry_entries`, `source_sync_runs`,
immutable `raw_job_records`/`raw_job_record_versions`, versioned
`canonical_jobs`/`canonical_job_versions`, `job_source_links`, versioned
`manual_job_records`, and `job_deduplication_candidates`. Unique source and
version constraints prevent identity/history rewriting; restricted foreign keys
preserve provenance. Canonical merging never deletes source links. Manual input
retains visibly unverified provenance and never causes URL retrieval.

| Record | Purpose and key constraints |
| --- | --- |
| `job_sources` | Provider, read-only contract/policy version, attribution and retention profile, adapter version, enabled/health state. |
| `employer_board_registry` | Employer name, verified domain, ATS provider, public board ID/slug, career URL, active/disabled state, verification time/method/reason. |
| `source_retrievals` | Source/board, timing, pagination, permitted request metadata, adapter version, rate-limit observations, result, and health correlation. |
| `source_listings` | Source posting ID, source URL, canonical application URL, employer/board, first/last seen, freshness/closed/manual state. |
| `source_listing_versions` | Immutable raw or permitted payload, hash/version, retrieval and source publish/update times, original location/remote/eligibility values, attribution. |
| `normalized_job_derivations` | Normalized field, source version(s), derivation method/version, confidence, and unknown state; never overwrites source values. |
| `canonical_jobs` | Stable normalized job identity. |
| `canonical_job_versions` | Immutable title/employer/description/requirements; country/region/city; timezone; remote class; relocation; authorization/sponsorship and licensing language; employment type; compensation/currency; languages; employer/destination jurisdiction. |
| `job_source_links` | Versioned many-to-one/many-to-many association retaining deduplication confidence and rationale. |

Canonicalization never deletes source records. A displayed job MUST be
traceable to at least one source listing and URL.

`source_listings` preserves original location, remote classification, employer,
and eligibility language. Owner operating jurisdiction, job-location country,
and employer/destination jurisdiction are distinct fields. Missing eligibility
data is nullable/unknown, never synthesized.

Manual listings have a distinct source type and required label, “Manually
entered — source not automatically verified,” with owner-supplied fields and no
automated retrieval record. `job_source_links` supports multiple approved and
manual records per canonical job without losing provenance. Remotive attribution
and supplied URL are required constraints for Remotive-derived presentation.

## 5. Matching and generation

| Record | Purpose and key constraints |
| --- | --- |
| `job_requirement_sets` | Immutable extraction version tied to an exact source/canonical job version, extractor version, creation time, and invalidation/supersession metadata. |
| `job_requirements` | Immutable type, mandatory/preferred/descriptive class, exact source text/location citation, extraction rationale/confidence, normalized concept, dimension, within-dimension weight, and owner-review state. |
| `job_requirement_corrections` | Audited owner correction, prior requirement/version, corrected classification or concept, reason, timestamp, resulting requirement-set version, and match-recalculation correlation. |
| `matching_rule_versions` | Immutable scoring, eligibility, blocker, coverage, rounding, confidence, and fairness rules plus formula version. |
| `matching_weight_set_versions` | Immutable capability and preference weights, owner/config origin, creation time, documented limits, and supersession link. |
| `match_versions` | Immutable job/requirement/profile/preferences snapshot references; rule and weight versions; capability/preference/combined/ranking values at full precision; evidence coverage; extraction confidence; eligibility; insufficient-evidence state; timestamps. |
| `match_dimension_scores` | Per-version dimension, weighted numerator/denominator, alignment, coverage, contribution, and known/unknown counts. |
| `match_factors` | Exact match version and requirement; eligible verified fact version when evaluable; verified match/partial/gap, missing evidence, uncertainty, or owner-action class; exact rule, citations, value, weight, and contribution. Inferred signals cannot be referenced. |
| `match_blocker_determinations` | Original compatible/unclear/blocked determination, dimension, cited mandatory requirement, contradictory verified fact, confidence/review basis, explanation, and creation time. |
| `match_owner_overrides` | Original determination reference, owner reason, timestamp, and resulting view/filter preference; never rewrites the determination. |
| `match_score_diffs` | Old/new match and rule/weight versions with component diffs and reason. |
| `application_match_snapshots` | Immutable match output, formula/rule/weight references, factor/blocker evidence, and display state retained at approval and submission. |
| `generation_runs` | Artifact type, provider/model, prompt-template version, input digest, status, and timestamps. |
| `generation_fact_inputs` | Exact verified fact versions supplied to generation. |
| `generated_claims` | Claim text and supporting fact-version links; unsupported status blocks application use. |

`generation_fact_inputs` can reference only eligible verified fact versions.
`generated_claims` must support a query from claim to exact fact versions,
confirmation events, evidence, and provenance. Inferred signals may be read by
matching only and are structurally excluded from generation inputs.

Match constraints likewise exclude `inferred_matching_signals` from scored
factors and blocker evidence. Unknown requirements have no numerator or
denominator contribution but remain in evidence-coverage calculations. A
blocked determination requires both a sufficiently supported mandatory job
requirement and a contradictory currently eligible verified fact. Protected
and proxy fields have no permitted match-factor mapping. Recalculation and
owner correction append versions; application-time snapshots are immutable.

## 6. Review, approval, submission, and tracking

| Record | Purpose and key constraints |
| --- | --- |
| `application_drafts` | Target job version and lifecycle state. |
| `application_payload_snapshots` | Immutable canonical destination/attempt, fields, answers, consents, exact fact snapshots, document-version digests, source URL, and payload digest. |
| `application_payload_facts` | Exact fact-version ID, immutable submitted value snapshot, provenance snapshot, and claim/field use. |
| `final_apply_approvals` | Snapshot ID, destination identity/digest, approval timestamp, approving session, expiry/revocation state. |
| `submission_attempts` | Approval ID, snapshot ID, adapter/version, started/completed timestamps, idempotency key, outcome, and external reference. |
| `submission_field_records` | Exact field names/types/values or protected value references actually sent. |
| `submission_document_records` | Exact document versions and digests sent. |
| `submission_events` | Append-only validation, request, response, timeout, ambiguity, retry, cancellation, or completion evidence. |
| `application_status_events` | Status, occurrence/recording time, origin, evidence, and confidence. |
| `audit_events` | Append-oriented actor/action/object, timestamp, correlation ID, before/after digests, and redacted metadata. |

Submission is allowed only when the current canonical payload and destination
match the approval. Database constraints should prevent an attempt from
referencing an approval for a different snapshot; backend validation must also
recompute digests immediately before external interaction.

Approval eligibility depends on exact `application_payload_facts`. A supporting
version becoming stale/conflicted/revoked or being superseded by a material edit
revokes affected approvals. Historical payload facts remain unchanged.

Sensitive exact values require application-layer encryption or protected
references according to [Security and Compliance](SECURITY_AND_COMPLIANCE.md),
while still remaining reconstructable for the owner's audit needs.

## 7. Lifecycle and deletion

- Mutable presentation state may change; evidence and material history append
  new versions or events.
- File deletion must coordinate storage removal with a tombstone/audit record.
- Backup retention keeps 7 daily, 4 weekly, and 6 monthly verified bundles and
  never removes the last known-good bundle.
- Backup cleanup occurs only after successful creation and verification and
  must honor deletion tombstones.

| Record | Purpose and key constraints |
| --- | --- |
| `retention_policy_versions` | Immutable policy versions, effective time, prospective/migration mode, and owner approval. |
| `retention_schedules` | Object identity/type, explicit basis timestamp, deadline, source cap, owner extension, pin, dependency hold, and policy version. |
| `retention_runs` | Dry-run/execution identity, policy version, counts/storage, times, outcome, and audit correlation. |
| `trash_entries` | Object identity/type, scope, trashed time, purge-after time, sensitive/immediate flag, and restore state. |
| `deletion_dependencies` | Object-to-dependent record, integrity reason, and permitted resolution choices. |
| `deletion_requests` | Preview digest, scope, dependency resolutions, export reference, confirmation, execution state, and failure. |
| `deletion_tombstones` | Minimal stable object identity/hash, permanent deletion time, type, and backup cutoff; no deleted content. |
| `data_exports` | Requested scope, creation/expiry, checksum, status, and protected storage reference. |

Deadlines derive only from explicit timestamps. Schedules implement D-016 for
facts/resumes, source/saved jobs, drafts, applications, audits, logs, temporary
data, inferred signals, and sensitive answers. Submitted applications inside
five years require explicit owner deletion.

Permanent deletion coordinates records, documents, indexes, caches, and derived
content without partial divergence, appends a redacted event, and leaves a
minimal tombstone. Fact deletion records the owner's choice to retain immutable
application snapshots or delete the entire dependent application.

Before restoring an older backup, preserve the current tombstone ledger outside
the replacement unit, merge it into the candidate database, and apply it to
records/files/derived content. The application cannot serve until every
tombstone newer than the selected backup has been applied.

## 8. Open schema decisions

- Encryption fields and key-management mechanism
- Audit immutability mechanism and deletion reconciliation
- Canonical payload serialization and material-change taxonomy
- Approval expiry and retry representation
- Permitted storage of source raw content
- Status vocabulary and evidence confidence model
