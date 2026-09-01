# ApplyPilot Repository Instructions

## Purpose and scope

ApplyPilot is permanently a single-owner personal job-discovery and application
tool. It initially runs locally on the owner's Fedora computer and listens only
on loopback interfaces. Do not introduce public registration or features for
additional accounts, tenants, teams, organizations, invitations, roles,
subscriptions, or billing.

These instructions apply to the entire repository.

## Required reading

Before making any architectural or application-workflow change, read all of:

- `docs/PRODUCT_REQUIREMENTS.md`
- `docs/ARCHITECTURE.md`
- `docs/SECURITY_AND_COMPLIANCE.md`
- `docs/DECISIONS.md`
- `docs/PROGRESS.md`

Also read `docs/DATABASE_SCHEMA.md` before changing persistence and
`docs/DEVELOPMENT_ROADMAP.md` before changing milestone scope. If documents
conflict, stop and record the conflict in `docs/DECISIONS.md`; do not silently
choose an interpretation.

## Permanent invariants

- Nothing is submitted without the owner's explicit Final Apply approval.
- Approval is bound to one exact payload and destination. A material payload or
  destination change invalidates it.
- Generated content may use only verified candidate facts and may not invent or
  embellish facts. Unknown facts remain unknown.
- Extraction, parsing, import, inference, agreement among sources, and owner
  entry never verify a fact. Only an explicit owner confirmation does so.
- Candidate fact versions are immutable. Unverified, stale, conflicted, or
  revoked versions cannot support generated or submitted content. Inferred
  signals are separate and may influence only clearly labelled matching.
- Application payloads bind exact fact-version IDs and preserve submitted fact
  snapshots. Supporting-fact changes or conflict resolution invalidate affected
  Final Apply approvals without rewriting historical applications.
- Every job retains source provenance.
- Every submission attempt, exact submitted content, document, timestamp,
  destination, source URL, result, and later status update is auditable.
- Never bypass CAPTCHAs, anti-bot or authentication controls, consent
  requirements, rate limits, or third-party terms.
- Never commit passwords, tokens, secrets, resumes, generated application
  documents, personal data, local databases, backups, or production logs.

## Engineering rules

- Keep the Next.js/TypeScript frontend, Python/FastAPI backend, PostgreSQL
  system of record, and Docker Compose local environment consistent with
  `docs/ARCHITECTURE.md`.
- Docker Compose is the only supported and acceptance-tested Milestone 1
  runtime and the canonical interface for setup, development, tests,
  migrations, backup, and recovery. Native Fedora commands are debugging aids
  only. Do not introduce Podman, Kubernetes, cloud, hosted, or remote runtime
  paths during Milestone 1.
- For Milestone 1, bind both frontend and backend host endpoints to
  `127.0.0.1`, use plain HTTP only in that explicitly configured loopback
  environment, and keep PostgreSQL private to Docker. Fail closed if a
  non-loopback configuration lacks HTTPS and `Secure=true` session cookies.
- Use protected local file storage for the MVP unless an accepted decision
  changes it. Redis and S3-compatible storage are deferred until justified.
- Enforce security and Final Apply rules in the backend, not only in UI code.
- Password recovery is local-shell only: never add a forgot-password UI or HTTP
  endpoint. A successful password reset atomically replaces the hash, revokes
  every session, and writes a redacted security event.
- Do not implement, configure, advertise, generate, or enable TOTP/MFA in M1.
  Do not create TOTP secrets, recovery codes, routes, UI, or dormant handlers.
  Preserve only clean future-compatible boundaries. Any future TOTP reset must
  be separately invoked and confirmed and must invalidate sessions and recovery
  codes.
- Pin runtime/toolchain versions, use non-root containers where practical,
  preserve Fedora file ownership for bind mounts, add health/readiness checks,
  and keep secrets in ignored local files or an equivalent local mechanism.
  Committed environment examples contain safe names and placeholders only.
- Backups are versioned bundles encrypted with an age public key and written
  outside the repository and live storage. Never create an unencrypted final
  backup, include sessions or secrets, or treat backups as password recovery.
  Restore is local-shell only, uses Docker Compose, validates in isolation,
  replaces database and documents atomically as one unit, revokes all sessions,
  and preserves the previous live state until validation succeeds.
- Treat India/personal domestic use as an engineering scope assumption, never a
  legal certification or legal advice. Respect destination-specific and source
  rules; the stricter applicable restriction wins. D-018 governs M1 sources.
- India is the owner/runtime jurisdiction, not a job-location filter. Discovery
  is worldwide. Keep owner jurisdiction, job location, and employer/destination
  jurisdiction separate; never infer citizenship, nationality, visa/work
  authorization, protected traits, or relocation willingness.
- Implement retention from explicit timestamps and auditable jobs. Deletion is
  owner-controlled, dependency-aware, exportable first, recoverable for 30 days
  by default, and immediately permanent for sensitive data on request. Minimal
  tombstones must be reapplied after older-backup restore to prevent resurrection.
- Do not add application code until the documentation milestone is approved.
- Use synthetic, non-identifying fixtures. Redact sensitive values from logs
  and test output.
- For any future approved authenticated integration, prefer official APIs or
  OAuth over storing third-party passwords. D-018 does not permit authenticated
  browser sessions or owner cookies for M1 job discovery.
- Treat external-source integration as prohibited until its authorization,
  terms, rate limits, attribution, and failure behavior are documented.
- M1 discovery adapters are read-only Greenhouse Job Board, Lever Postings,
  Ashby Public Job Posting, and Remotive public APIs only. Never add submission,
  private/employer/candidate APIs, automated board discovery, unsupported-site
  scraping, authenticated-cookie collection, or undocumented endpoints.
- Greenhouse/Lever/Ashby boards require an owner-reviewed registry. Remotive
  listings visibly retain “Source: Remotive” and its supplied URL. Manual jobs
  are labelled unverified and never trigger URL scraping.
- D-019 matching is deterministic and versioned. An LLM may extract cited
  requirements but never sets final scores, eligibility, or blockers. Unknowns
  are not gaps; inference cannot score or affect blockers; protected traits and
  proxies never affect any match output. Preserve immutable rule, weight,
  requirement, match, correction, and application-time snapshot history.
- Add proportionate tests for every change. Security and approval-boundary
  changes require negative-path and concurrency tests.
- Update `docs/DECISIONS.md` for accepted or superseded decisions and
  `docs/PROGRESS.md` when work state changes.

## Change discipline

Preserve the labels **Accepted decision**, **Recommended default**,
**Unresolved decision**, and **Deferred capability**. Recommendations do not
become accepted merely through implementation. Do not resolve an unresolved
product question without owner approval.
