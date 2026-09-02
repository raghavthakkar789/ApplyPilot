from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from applypilot.models.job import CanonicalJob, JobDeduplicationCandidate, RawJobRecord
from applypilot.repositories.job_repository import JobRepository
from applypilot.repositories.security_repository import SecurityRepository


class JobDeduplicationService:
    def __init__(self, database: Session) -> None:
        self.database = database
        self.jobs = JobRepository(database)
        self.events = SecurityRepository(database)

    def detect_candidates(self, job: CanonicalJob) -> None:
        version = self.jobs.version(job.current_version_id)
        if version is None:
            return
        key = version.normalized_data.get("deduplication_key")
        if not isinstance(key, str):
            return
        for other in self.jobs.jobs():
            if other.id == job.id or other.archived_at is not None:
                continue
            other_version = self.jobs.version(other.current_version_id)
            if (
                other_version is None
                or other_version.normalized_data.get("deduplication_key") != key
            ):
                continue
            left, right = sorted((job.id, other.id))
            exists = self.database.scalar(
                select(JobDeduplicationCandidate).where(
                    JobDeduplicationCandidate.left_job_id == left,
                    JobDeduplicationCandidate.right_job_id == right,
                )
            )
            if exists is None:
                candidate = JobDeduplicationCandidate(
                    left_job_id=left,
                    right_job_id=right,
                    reasons=["same normalized employer, title, and location"],
                    status="pending",
                    created_at=datetime.now(UTC),
                )
                self.database.add(candidate)
                self.database.flush()
                self.events.record(
                    "job_duplicate_candidate_created",
                    {"deduplication_candidate_id": candidate.id},
                )

    def resolve(self, candidate_id: str, merge: bool, reason: str) -> JobDeduplicationCandidate:
        candidate = self.database.scalar(
            select(JobDeduplicationCandidate)
            .where(JobDeduplicationCandidate.id == candidate_id)
            .with_for_update()
        )
        if candidate is None:
            raise HTTPException(404, "Deduplication candidate not found.")
        if candidate.status != "pending":
            raise HTTPException(409, "This deduplication candidate is already resolved.")
        if merge:
            left = self.jobs.job(candidate.left_job_id, lock=True)
            right = self.jobs.job(candidate.right_job_id, lock=True)
            if left is None or right is None:
                raise HTTPException(409, "A referenced job is unavailable.")
            for link in self.jobs.links(right.id):
                link.canonical_job_id = left.id
                raw = self.database.get(RawJobRecord, link.raw_job_record_id)
                if raw is not None:
                    raw.canonical_job_id = left.id
            right.archived_at = datetime.now(UTC)
            candidate.status = "merged"
        else:
            candidate.status = "kept_separate"
        candidate.owner_reason = reason
        candidate.resolved_at = datetime.now(UTC)
        self.events.record(
            "job_duplicate_merged" if merge else "job_duplicate_split",
            {"deduplication_candidate_id": candidate.id},
        )
        self.database.commit()
        return candidate
