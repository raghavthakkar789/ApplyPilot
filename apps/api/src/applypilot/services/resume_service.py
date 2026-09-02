import secrets
from datetime import UTC, datetime, timedelta
from pathlib import Path

from fastapi import HTTPException, UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from applypilot.core.config import get_settings
from applypilot.domain.documents.extraction_result import EvidenceSegment
from applypilot.models.resume import (
    DocumentExtraction,
    DocumentLifecycleEvent,
    Resume,
    ResumeFactCandidate,
    ResumeVersion,
    StoredDocument,
)
from applypilot.parsers.base import DocumentParseError
from applypilot.repositories.resume_repository import ResumeRepository
from applypilot.repositories.security_repository import SecurityRepository
from applypilot.services.document_extraction_service import DocumentExtractionService
from applypilot.services.document_storage_service import (
    DocumentStorageService,
    UploadTooLargeError,
)
from applypilot.services.document_validation_service import DocumentValidationService


class ResumeService:
    def __init__(self, database: Session) -> None:
        self.database = database
        self.repository = ResumeRepository(database)
        self.storage = DocumentStorageService(get_settings().document_storage_root)
        self.events = SecurityRepository(database)

    async def create(self, display_name: str, purpose: str | None, upload: UploadFile) -> Resume:
        now = datetime.now(UTC)
        resume = Resume(
            owner_id=1,
            display_name=display_name.strip(),
            purpose=purpose.strip() if purpose else None,
            archived=False,
            created_at=now,
        )
        self.database.add(resume)
        self.database.flush()
        await self._add_version(resume, upload, now)
        self.events.record("resume_created", {"resume_id": resume.id})
        self.database.commit()
        return resume

    async def add_version(self, resume_id: str, upload: UploadFile) -> Resume:
        resume = self.repository.resume(resume_id, lock=True)
        if resume is None:
            raise HTTPException(404, "Resume not found.")
        if resume.trashed_at is not None:
            raise HTTPException(409, "Restore this resume before adding a version.")
        await self._add_version(resume, upload, datetime.now(UTC))
        self.database.commit()
        return resume

    async def _add_version(self, resume: Resume, upload: UploadFile, now: datetime) -> None:
        try:
            staged = await self.storage.stage(upload)
        except UploadTooLargeError as error:
            self.database.rollback()
            self.events.record("document_validation_failed", {"failure_category": "size_limit"})
            self.database.commit()
            raise HTTPException(413, str(error)) from error
        finalized: Path | None = None
        try:
            validated = DocumentValidationService().validate(
                staged.path, upload.filename, upload.content_type
            )
            self._lifecycle(resume.id, None, "document_validation_passed", "success", now)
            result = DocumentExtractionService().extract(staged.path, validated.document_format)
            duplicate = self.repository.document_by_digest(staged.sha256, staged.byte_length)
            if duplicate is None:
                storage_key = f"{secrets.token_hex(24)}.{validated.document_format.value}"
                finalized = self.storage.finalize(staged.path, storage_key)
                document = StoredDocument(
                    storage_key=storage_key,
                    sha256=staged.sha256,
                    byte_length=staged.byte_length,
                    detected_media_type=validated.media_type,
                    document_format=validated.document_format.value,
                    integrity_state="verified",
                    created_at=now,
                )
                self.database.add(document)
                self.database.flush()
            else:
                document = duplicate
                self.storage.discard(staged.path)
                self.events.record("resume_duplicate_detected", {"resume_id": resume.id})
                self._lifecycle(resume.id, None, "document_duplicate_detected", "success", now)
            versions = self.repository.versions(resume.id)
            number = versions[0].version_number + 1 if versions else 1
            if versions and versions[0].superseded_at is None:
                versions[0].superseded_at = now
            version = ResumeVersion(
                resume_id=resume.id,
                version_number=number,
                document_id=document.id,
                original_filename=validated.display_filename,
                declared_media_type=validated.media_type,
                parser_name=validated.parser_name,
                parser_version=validated.parser_version,
                extraction_status="succeeded",
                created_at=now,
            )
            self.database.add(version)
            self.database.flush()
            resume.current_version_id = version.id
            extraction = DocumentExtraction(
                resume_version_id=version.id,
                extracted_text=result.text,
                page_count=result.page_count,
                paragraph_count=result.paragraph_count,
                segments=[
                    {"citation": segment.citation, "text": segment.text}
                    for segment in result.segments
                ],
                warnings=list(result.warnings),
                parser_result="succeeded",
                extracted_at=now,
                integrity_hash=DocumentExtractionService.integrity_hash(result.text),
            )
            self.database.add(extraction)
            self._create_candidates(version.id, result.segments, now)
            self._lifecycle(resume.id, version.id, "document_extraction_succeeded", "success", now)
            self._lifecycle(resume.id, version.id, "resume_version_uploaded", "success", now)
            self.events.record(
                "resume_version_uploaded",
                {"resume_id": resume.id, "resume_version_id": version.id},
            )
        except (DocumentParseError, ValueError) as error:
            self.storage.discard(staged.path)
            self.database.rollback()
            self.events.record(
                "document_validation_failed", {"failure_category": "invalid_document"}
            )
            self.database.commit()
            raise HTTPException(422, str(error)) from error
        except IntegrityError as error:
            self.storage.discard(staged.path)
            if finalized is not None:
                finalized.unlink(missing_ok=True)
            self.database.rollback()
            raise HTTPException(409, "The resume changed concurrently. Please retry.") from error
        except Exception:
            self.storage.discard(staged.path)
            if finalized is not None:
                finalized.unlink(missing_ok=True)
            self.database.rollback()
            raise

    def trash(self, resume_id: str) -> Resume:
        resume = self._resume_for_change(resume_id)
        if resume.trashed_at is not None:
            raise HTTPException(409, "Resume is already in trash.")
        now = datetime.now(UTC)
        resume.trashed_at = now
        resume.purge_after = now + timedelta(days=30)
        self._lifecycle(resume.id, None, "resume_trashed", "success", now)
        self.events.record("resume_moved_to_trash", {"resume_id": resume.id})
        self.database.commit()
        return resume

    def restore(self, resume_id: str) -> Resume:
        resume = self._resume_for_change(resume_id)
        if resume.trashed_at is None:
            raise HTTPException(409, "Resume is not in trash.")
        resume.trashed_at = None
        resume.purge_after = None
        now = datetime.now(UTC)
        self._lifecycle(resume.id, None, "resume_restored", "success", now)
        self.events.record("resume_restored", {"resume_id": resume.id})
        self.database.commit()
        return resume

    def permanently_delete(self, resume_id: str) -> None:
        resume = self._resume_for_change(resume_id)
        if resume.trashed_at is None:
            raise HTTPException(409, "Move the resume to trash before permanent deletion.")
        versions = self.repository.versions(resume.id)
        for version in versions:
            if any(
                item.review_status == "accepted" for item in self.repository.candidates(version.id)
            ):
                raise HTTPException(
                    409, "An accepted fact candidate depends on this resume version."
                )
        now = datetime.now(UTC)
        resume.display_name = "Permanently deleted resume"
        resume.purpose = None
        resume.archived = True
        resume.current_version_id = None
        for version in versions:
            version.permanently_deleted_at = now
            extraction = self.repository.extraction(version.id)
            if extraction is not None:
                extraction.extracted_text = None
            document = self.repository.document(version.document_id)
            if document is not None and self.repository.document_reference_count(document.id) <= 1:
                self.storage.permanently_delete(document.storage_key)
                document.deleted_at = now
        self._lifecycle(resume.id, None, "resume_permanently_deleted", "success", now)
        self.events.record("resume_permanently_deleted", {"resume_id": resume.id})
        self.database.commit()

    def _resume_for_change(self, resume_id: str) -> Resume:
        resume = self.repository.resume(resume_id, lock=True)
        if resume is None:
            raise HTTPException(404, "Resume not found.")
        return resume

    def _create_candidates(
        self, version_id: str, segments: tuple[EvidenceSegment, ...], now: datetime
    ) -> None:
        for segment in segments:
            text = segment.text.strip()
            citation = segment.citation
            lowered = text.lower()
            mapping = (("skill:", "skill"), ("language:", "language"))
            for prefix, fact_type in mapping:
                if not lowered.startswith(prefix):
                    continue
                value = text[len(prefix) :].strip()
                if not value or len(value) > 120:
                    continue
                semantic = f"{fact_type}.{value.casefold().replace(' ', '_')}"
                candidate = ResumeFactCandidate(
                    resume_version_id=version_id,
                    fact_type=fact_type,
                    semantic_key=semantic,
                    proposed_value=value,
                    evidence_citation=citation,
                    extraction_method="deterministic_label_v1",
                    confidence="high",
                    review_status="pending",
                    created_at=now,
                )
                self.database.add(candidate)
                self.database.flush()
                self.events.record("resume_candidate_created", {"candidate_id": candidate.id})

    def _lifecycle(
        self,
        resume_id: str,
        version_id: str | None,
        event_type: str,
        outcome: str,
        now: datetime,
    ) -> None:
        self.database.add(
            DocumentLifecycleEvent(
                resume_id=resume_id,
                resume_version_id=version_id,
                event_type=event_type,
                outcome=outcome,
                metadata_json={},
                created_at=now,
            )
        )
