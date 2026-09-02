from sqlalchemy import func, select
from sqlalchemy.orm import Session

from applypilot.models.resume import (
    DocumentExtraction,
    Resume,
    ResumeFactCandidate,
    ResumeVersion,
    StoredDocument,
)


class ResumeRepository:
    def __init__(self, database: Session) -> None:
        self.database = database

    def list_resumes(self, include_trash: bool = True) -> list[Resume]:
        query = select(Resume).where(Resume.owner_id == 1)
        if not include_trash:
            query = query.where(Resume.trashed_at.is_(None))
        return list(self.database.scalars(query.order_by(Resume.created_at.desc())))

    def resume(self, resume_id: str, lock: bool = False) -> Resume | None:
        query = select(Resume).where(Resume.id == resume_id, Resume.owner_id == 1)
        if lock:
            query = query.with_for_update()
        return self.database.scalar(query)

    def versions(self, resume_id: str) -> list[ResumeVersion]:
        return list(
            self.database.scalars(
                select(ResumeVersion)
                .where(ResumeVersion.resume_id == resume_id)
                .order_by(ResumeVersion.version_number.desc())
            )
        )

    def version(self, version_id: str) -> ResumeVersion | None:
        return self.database.scalar(
            select(ResumeVersion)
            .join(Resume)
            .where(ResumeVersion.id == version_id, Resume.owner_id == 1)
        )

    def document(self, document_id: str) -> StoredDocument | None:
        return self.database.get(StoredDocument, document_id)

    def document_by_digest(self, digest: str, size: int) -> StoredDocument | None:
        return self.database.scalar(
            select(StoredDocument).where(
                StoredDocument.sha256 == digest,
                StoredDocument.byte_length == size,
                StoredDocument.deleted_at.is_(None),
            )
        )

    def document_reference_count(self, document_id: str) -> int:
        return int(
            self.database.scalar(
                select(func.count())
                .select_from(ResumeVersion)
                .where(
                    ResumeVersion.document_id == document_id,
                    ResumeVersion.permanently_deleted_at.is_(None),
                )
            )
            or 0
        )

    def extraction(self, version_id: str) -> DocumentExtraction | None:
        return self.database.scalar(
            select(DocumentExtraction).where(DocumentExtraction.resume_version_id == version_id)
        )

    def candidates(self, version_id: str) -> list[ResumeFactCandidate]:
        return list(
            self.database.scalars(
                select(ResumeFactCandidate)
                .where(ResumeFactCandidate.resume_version_id == version_id)
                .order_by(ResumeFactCandidate.created_at)
            )
        )

    def candidate(self, candidate_id: str, lock: bool = False) -> ResumeFactCandidate | None:
        query = (
            select(ResumeFactCandidate)
            .join(ResumeVersion)
            .join(Resume)
            .where(ResumeFactCandidate.id == candidate_id, Resume.owner_id == 1)
        )
        if lock:
            query = query.with_for_update()
        return self.database.scalar(query)
