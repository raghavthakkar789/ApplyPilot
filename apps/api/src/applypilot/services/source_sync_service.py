import hashlib
import json
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from applypilot.adapters.jobs import ADAPTERS
from applypilot.adapters.jobs.base import AdapterError
from applypilot.domain.jobs.job import SourceJob
from applypilot.domain.jobs.normalization import normalized_key
from applypilot.models.job import (
    CanonicalJob,
    CanonicalJobVersion,
    JobSourceLink,
    RawJobRecord,
    RawJobRecordVersion,
    SourceSyncRun,
)
from applypilot.repositories.job_repository import JobRepository
from applypilot.repositories.security_repository import SecurityRepository
from applypilot.repositories.source_registry_repository import SourceRegistryRepository
from applypilot.services.job_deduplication_service import JobDeduplicationService


class SourceSyncService:
    def __init__(self, database: Session) -> None:
        self.database = database
        self.registry = SourceRegistryRepository(database)
        self.jobs = JobRepository(database)
        self.events = SecurityRepository(database)

    async def synchronize(self, provider: str, entry_id: str | None) -> SourceSyncRun:
        if provider not in ADAPTERS:
            raise HTTPException(404, "Source adapter not found.")
        self.database.execute(
            text("SELECT pg_advisory_xact_lock(hashtext(:sync_key))"),
            {"sync_key": f"source-sync:{provider}"},
        )
        active = self.registry.active_run(provider)
        if active:
            return active
        now = datetime.now(UTC)
        recent = (
            self.database.scalar(
                select(func.count(SourceSyncRun.id)).where(
                    SourceSyncRun.started_at >= now - timedelta(minutes=1)
                )
            )
            or 0
        )
        if recent >= 10:
            raise HTTPException(
                429, "Expensive-operation limit reached.", headers={"Retry-After": "60"}
            )
        identifier = None
        employer = "Remotive"
        entry = None
        if provider != "remotive":
            if (
                not entry_id
                or (entry := self.registry.entry(entry_id, lock=True)) is None
                or entry.provider != provider
                or not entry.enabled
            ):
                raise HTTPException(409, "An enabled validated registry entry is required.")
            identifier, employer = entry.board_identifier, entry.employer_name
        run = SourceSyncRun(
            provider=provider, registry_entry_id=entry_id, status="running", started_at=now
        )
        self.database.add(run)
        self.database.commit()
        self.events.record("source_sync_started", {"sync_id": run.id, "provider": provider})
        self.database.commit()
        try:
            source_jobs = await ADAPTERS[provider].retrieve(identifier, employer)
            changed = sum(self._ingest(provider, identifier, item, now) for item in source_jobs)
            changed += self._mark_missing(
                provider,
                identifier,
                {item.source_record_id for item in source_jobs},
                now,
            )
            run.status = "succeeded"
            run.records_seen = len(source_jobs)
            run.records_changed = changed
            run.finished_at = datetime.now(UTC)
            if entry:
                entry.last_success_at = run.finished_at
                entry.last_failure_category = None
            success_metadata: dict[str, str] = {
                "sync_id": run.id,
                "provider": provider,
                "records_seen": str(len(source_jobs)),
            }
            self.events.record("source_sync_succeeded", success_metadata)
        except AdapterError:
            self.database.rollback()
            loaded_run = self.database.get(SourceSyncRun, run.id)
            assert loaded_run is not None
            run = loaded_run
            run.status = "failed"
            run.safe_failure_category = "source_unavailable"
            run.finished_at = datetime.now(UTC)
            if entry:
                entry.last_failure_category = "source_unavailable"
            self.events.record(
                "source_sync_failed",
                {"sync_id": run.id, "provider": provider, "failure_category": "source_unavailable"},
            )
        self.database.commit()
        return run

    def _mark_missing(
        self,
        provider: str,
        board: str | None,
        seen_ids: set[str],
        now: datetime,
    ) -> int:
        records = self.database.scalars(
            select(RawJobRecord).where(
                RawJobRecord.provider == provider,
                RawJobRecord.board_identifier == board,
            )
        )
        changed = 0
        for raw in records:
            if raw.source_record_id in seen_ids or raw.canonical_job_id is None:
                continue
            raw.missing_observations += 1
            if self.database.scalar(
                select(RawJobRecord.id).where(
                    RawJobRecord.canonical_job_id == raw.canonical_job_id,
                    RawJobRecord.missing_observations == 0,
                )
            ):
                continue
            job = self.database.get(CanonicalJob, raw.canonical_job_id)
            current = self.jobs.version(job.current_version_id) if job else None
            if job is None or current is None:
                continue
            state = "closed" if raw.missing_observations >= 2 else "closure_suspected"
            if current.freshness_state == state:
                continue
            version = CanonicalJobVersion(
                canonical_job_id=job.id,
                version_number=current.version_number + 1,
                title=current.title,
                employer=current.employer,
                description_text=current.description_text,
                normalized_data=current.normalized_data,
                normalization_warnings=current.normalization_warnings,
                content_hash=current.content_hash,
                freshness_state=state,
                created_at=now,
            )
            self.database.add(version)
            self.database.flush()
            job.current_version_id = version.id
            changed += 1
            if state == "closed":
                self.events.record("job_closure_confirmed", {"job_id": job.id})
        return changed

    def _ingest(self, provider: str, board: str | None, item: SourceJob, now: datetime) -> int:
        payload_hash = hashlib.sha256(json.dumps(item.raw, sort_keys=True).encode()).hexdigest()
        raw = self.jobs.raw(provider, board, item.source_record_id)
        if raw is None:
            raw = RawJobRecord(
                provider=provider,
                board_identifier=board,
                source_record_id=item.source_record_id,
                created_at=now,
                last_seen_at=now,
            )
            self.database.add(raw)
            self.database.flush()
        else:
            raw.last_seen_at = now
            raw.missing_observations = 0
        exists = self.database.scalar(
            select(RawJobRecordVersion).where(
                RawJobRecordVersion.raw_job_record_id == raw.id,
                RawJobRecordVersion.payload_hash == payload_hash,
            )
        )
        if exists:
            return 0
        count = (
            self.database.scalar(
                select(func.count(RawJobRecordVersion.id)).where(
                    RawJobRecordVersion.raw_job_record_id == raw.id
                )
            )
            or 0
        )
        self.database.add(
            RawJobRecordVersion(
                raw_job_record_id=raw.id,
                version_number=count + 1,
                payload=item.raw,
                payload_hash=payload_hash,
                adapter_version=ADAPTERS[provider].adapter_version,
                retrieved_at=now,
            )
        )
        if raw.canonical_job_id is None:
            canonical = None
            if item.application_url:
                existing_link = self.database.scalar(
                    select(JobSourceLink).where(
                        JobSourceLink.application_url == item.application_url
                    )
                )
                if existing_link:
                    canonical = self.database.get(CanonicalJob, existing_link.canonical_job_id)
            if canonical is None:
                canonical = CanonicalJob(saved=False, created_at=now)
                self.database.add(canonical)
                self.database.flush()
            raw.canonical_job_id = canonical.id
        else:
            loaded_job = self.database.get(CanonicalJob, raw.canonical_job_id)
            assert loaded_job is not None
            canonical = loaded_job
        current = self.jobs.version(canonical.current_version_id)
        version_number = (current.version_number + 1) if current else 1
        normalized = {
            "location": item.original_location,
            "work_mode": item.remote_classification,
            "employment_type": item.employment_type,
            "publication_time": item.published_at.isoformat() if item.published_at else None,
            "provider_update_time": item.updated_at.isoformat() if item.updated_at else None,
            "retrieval_time": now.isoformat(),
            "application_url": item.application_url,
            "deduplication_key": normalized_key(item.employer, item.title, item.original_location),
        }
        content_hash = hashlib.sha256(
            json.dumps(
                {
                    "title": item.title,
                    "employer": item.employer,
                    "description": item.description_text,
                    **normalized,
                },
                sort_keys=True,
            ).encode()
        ).hexdigest()
        version = CanonicalJobVersion(
            canonical_job_id=canonical.id,
            version_number=version_number,
            title=item.title,
            employer=item.employer,
            description_text=item.description_text,
            normalized_data=normalized,
            normalization_warnings=["Location remains unnormalized."]
            if item.original_location
            else [],
            content_hash=content_hash,
            freshness_state="changed" if current else "fresh",
            created_at=now,
        )
        self.database.add(version)
        self.database.flush()
        canonical.current_version_id = version.id
        if not self.database.scalar(
            select(JobSourceLink).where(
                JobSourceLink.canonical_job_id == canonical.id,
                JobSourceLink.raw_job_record_id == raw.id,
            )
        ):
            self.database.add(
                JobSourceLink(
                    canonical_job_id=canonical.id,
                    raw_job_record_id=raw.id,
                    source_url=item.source_url,
                    application_url=item.application_url,
                    attribution=item.attribution,
                    linked_reason="exact_source_identity",
                    created_at=now,
                )
            )
        JobDeduplicationService(self.database).detect_candidates(canonical)
        return 1
