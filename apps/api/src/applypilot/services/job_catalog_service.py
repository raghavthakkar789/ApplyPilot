import hashlib
import json
from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from applypilot.domain.jobs.normalization import normalized_key, safe_external_url, safe_text
from applypilot.models.job import (
    CanonicalJob,
    CanonicalJobVersion,
    JobSourceLink,
    ManualJobRecord,
    RawJobRecord,
    RawJobRecordVersion,
)
from applypilot.repositories.job_repository import JobRepository
from applypilot.repositories.security_repository import SecurityRepository
from applypilot.schemas.job import ManualJobInput
from applypilot.services.job_deduplication_service import JobDeduplicationService


class JobCatalogService:
    def __init__(self, database: Session) -> None:
        self.database = database
        self.repository = JobRepository(database)
        self.events = SecurityRepository(database)

    def create_manual(self, value: ManualJobInput) -> CanonicalJob:
        now = datetime.now(UTC)
        data = value.model_dump(mode="json")
        data["source_url"] = safe_external_url(str(value.source_url)) if value.source_url else None
        data["application_url"] = (
            safe_external_url(str(value.application_url)) if value.application_url else None
        )
        description = safe_text(value.description)
        job = CanonicalJob(created_at=now, saved=False)
        self.database.add(job)
        self.database.flush()
        self._version(job, value.title, value.employer, description, data, "manually_entered", now)
        self.database.add(
            ManualJobRecord(
                canonical_job_id=job.id, version_number=1, owner_input=data, created_at=now
            )
        )
        raw = RawJobRecord(
            provider="manual",
            board_identifier=None,
            source_record_id=job.id,
            canonical_job_id=job.id,
            created_at=now,
            last_seen_at=now,
        )
        self.database.add(raw)
        self.database.flush()
        payload_hash = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
        self.database.add(
            RawJobRecordVersion(
                raw_job_record_id=raw.id,
                version_number=1,
                payload=data,
                payload_hash=payload_hash,
                adapter_version="manual-1",
                retrieved_at=now,
            )
        )
        self.database.add(
            JobSourceLink(
                canonical_job_id=job.id,
                raw_job_record_id=raw.id,
                source_url=data["source_url"] or "manual-entry",
                application_url=data["application_url"],
                attribution="Manually entered — source not automatically verified",
                linked_reason="manual_identity",
                created_at=now,
            )
        )
        self.events.record("manual_job_created", {"job_id": job.id})
        JobDeduplicationService(self.database).detect_candidates(job)
        self.database.commit()
        return job

    def set_saved(self, job_id: str, saved: bool) -> CanonicalJob:
        job = self.repository.job(job_id, lock=True)
        if job is None:
            raise HTTPException(404, "Job not found.")
        job.saved = saved
        self.events.record("job_saved" if saved else "job_unsaved", {"job_id": job.id})
        self.database.commit()
        return job

    def _version(
        self,
        job: CanonicalJob,
        title: str,
        employer: str,
        description: str,
        data: dict[str, object],
        freshness: str,
        now: datetime,
    ) -> CanonicalJobVersion:
        content = {"title": title, "employer": employer, "description": description, **data}
        digest = hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()
        raw_location = data.get("location")
        location = raw_location if isinstance(raw_location, str) else None
        version = CanonicalJobVersion(
            canonical_job_id=job.id,
            version_number=1,
            title=title,
            employer=employer,
            description_text=description,
            normalized_data={
                **data,
                "deduplication_key": normalized_key(
                    employer,
                    title,
                    location,
                ),
            },
            normalization_warnings=[],
            content_hash=digest,
            freshness_state=freshness,
            created_at=now,
        )
        self.database.add(version)
        self.database.flush()
        job.current_version_id = version.id
        return version
