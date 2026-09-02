from sqlalchemy import select
from sqlalchemy.orm import Session

from applypilot.models.job import (
    CanonicalJob,
    CanonicalJobVersion,
    JobDeduplicationCandidate,
    JobSourceLink,
    RawJobRecord,
)


class JobRepository:
    def __init__(self, database: Session) -> None:
        self.database = database

    def jobs(self) -> list[CanonicalJob]:
        return list(
            self.database.scalars(select(CanonicalJob).order_by(CanonicalJob.created_at.desc()))
        )

    def job(self, job_id: str, lock: bool = False) -> CanonicalJob | None:
        statement = select(CanonicalJob).where(CanonicalJob.id == job_id)
        return self.database.scalar(statement.with_for_update() if lock else statement)

    def version(self, version_id: str | None) -> CanonicalJobVersion | None:
        return self.database.get(CanonicalJobVersion, version_id) if version_id else None

    def links(self, job_id: str) -> list[JobSourceLink]:
        return list(
            self.database.scalars(
                select(JobSourceLink).where(JobSourceLink.canonical_job_id == job_id)
            )
        )

    def versions(self, job_id: str) -> list[CanonicalJobVersion]:
        return list(
            self.database.scalars(
                select(CanonicalJobVersion)
                .where(CanonicalJobVersion.canonical_job_id == job_id)
                .order_by(CanonicalJobVersion.version_number.desc())
            )
        )

    def deduplication_candidates(self) -> list[JobDeduplicationCandidate]:
        return list(
            self.database.scalars(
                select(JobDeduplicationCandidate).order_by(
                    JobDeduplicationCandidate.created_at.desc()
                )
            )
        )

    def raw(self, provider: str, board: str | None, record_id: str) -> RawJobRecord | None:
        return self.database.scalar(
            select(RawJobRecord).where(
                RawJobRecord.provider == provider,
                RawJobRecord.board_identifier == board,
                RawJobRecord.source_record_id == record_id,
            )
        )
