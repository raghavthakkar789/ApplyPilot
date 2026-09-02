from pathlib import Path
from typing import cast

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from applypilot.api.dependencies.authentication import require_authentication
from applypilot.api.dependencies.csrf import require_csrf
from applypilot.core.config import get_settings
from applypilot.models.resume import Resume, ResumeVersion, StoredDocument
from applypilot.repositories.database import get_database_session
from applypilot.repositories.resume_repository import ResumeRepository
from applypilot.schemas.resume import (
    ExtractionResponse,
    ResumeDetailResponse,
    ResumeListResponse,
    ResumeMutationResponse,
    ResumeResponse,
    ResumeVersionResponse,
)
from applypilot.services.document_storage_service import DocumentStorageService
from applypilot.services.resume_service import ResumeService

router = APIRouter(prefix="/resumes", tags=["resumes"])


def version_response(
    version: ResumeVersion, document: StoredDocument, current_id: str | None
) -> ResumeVersionResponse:
    return ResumeVersionResponse(
        id=version.id,
        version_number=version.version_number,
        filename=version.original_filename,
        media_type=document.detected_media_type,
        format=document.document_format,
        byte_length=document.byte_length,
        sha256=document.sha256,
        parser=version.parser_name,
        parser_version=version.parser_version,
        extraction_status=version.extraction_status,
        integrity_state=document.integrity_state,
        created_at=version.created_at,
        superseded_at=version.superseded_at,
        current=version.id == current_id,
    )


def resume_response(resume: Resume, repository: ResumeRepository) -> ResumeResponse:
    current = repository.version(resume.current_version_id) if resume.current_version_id else None
    current_response = None
    if current is not None:
        document = repository.document(current.document_id)
        if document is not None:
            current_response = version_response(current, document, resume.current_version_id)
    return ResumeResponse(
        id=resume.id,
        display_name=resume.display_name,
        purpose=resume.purpose,
        created_at=resume.created_at,
        trashed_at=resume.trashed_at,
        purge_after=resume.purge_after,
        current_version=current_response,
    )


@router.get("", response_model=ResumeListResponse, dependencies=[Depends(require_authentication)])
def list_resumes(database: Session = Depends(get_database_session)) -> ResumeListResponse:
    repository = ResumeRepository(database)
    return ResumeListResponse(
        resumes=[resume_response(item, repository) for item in repository.list_resumes()]
    )


@router.post("", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def create_resume(
    display_name: str = Form(min_length=1, max_length=160),
    purpose: str | None = Form(default=None, max_length=160),
    file: UploadFile = File(),
    _context: object = Depends(require_csrf),
    database: Session = Depends(get_database_session),
) -> ResumeResponse:
    resume = await ResumeService(database).create(display_name, purpose, file)
    return resume_response(resume, ResumeRepository(database))


@router.get(
    "/{resume_id}",
    response_model=ResumeDetailResponse,
    dependencies=[Depends(require_authentication)],
)
def read_resume(
    resume_id: str, database: Session = Depends(get_database_session)
) -> ResumeDetailResponse:
    repository = ResumeRepository(database)
    resume = repository.resume(resume_id)
    if resume is None:
        raise HTTPException(404, "Resume not found.")
    base = resume_response(resume, repository)
    versions = []
    for version in repository.versions(resume.id):
        document = repository.document(version.document_id)
        if document is not None:
            versions.append(version_response(version, document, resume.current_version_id))
    return ResumeDetailResponse(**base.model_dump(), versions=versions)


@router.post("/{resume_id}/versions", response_model=ResumeResponse)
async def add_resume_version(
    resume_id: str,
    file: UploadFile = File(),
    _context: object = Depends(require_csrf),
    database: Session = Depends(get_database_session),
) -> ResumeResponse:
    resume = await ResumeService(database).add_version(resume_id, file)
    return resume_response(resume, ResumeRepository(database))


@router.get(
    "/versions/{version_id}/extraction",
    response_model=ExtractionResponse,
    dependencies=[Depends(require_authentication)],
)
def read_extraction(
    version_id: str, database: Session = Depends(get_database_session)
) -> ExtractionResponse:
    repository = ResumeRepository(database)
    version = repository.version(version_id)
    if version is None:
        raise HTTPException(404, "Resume version not found.")
    extraction = repository.extraction(version.id)
    if extraction is None:
        return ExtractionResponse(status=version.extraction_status)
    return ExtractionResponse(
        status=version.extraction_status,
        text=extraction.extracted_text,
        page_count=extraction.page_count,
        paragraph_count=extraction.paragraph_count,
        segments=cast(list[dict[str, str]], extraction.segments),
        warnings=cast(list[str], extraction.warnings),
        extracted_at=extraction.extracted_at,
        failure_category=extraction.failure_category,
    )


@router.get("/versions/{version_id}/download", dependencies=[Depends(require_authentication)])
def download_resume(
    version_id: str, database: Session = Depends(get_database_session)
) -> FileResponse:
    repository = ResumeRepository(database)
    version = repository.version(version_id)
    if version is None or version.permanently_deleted_at is not None:
        raise HTTPException(404, "Resume version not found.")
    document = repository.document(version.document_id)
    if document is None or document.deleted_at is not None:
        raise HTTPException(404, "Document not found.")
    path = DocumentStorageService(get_settings().document_storage_root).original_path(
        document.storage_key
    )
    if not path.is_file() or path.is_symlink():
        raise HTTPException(404, "Document is unavailable.")
    return FileResponse(
        Path(path),
        media_type=document.detected_media_type,
        filename=version.original_filename,
        headers={
            "Cache-Control": "no-store, private",
            "X-Content-Type-Options": "nosniff",
            "Content-Security-Policy": "default-src 'none'; sandbox",
        },
    )


@router.post("/{resume_id}/trash", response_model=ResumeMutationResponse)
def trash_resume(
    resume_id: str,
    _context: object = Depends(require_csrf),
    database: Session = Depends(get_database_session),
) -> ResumeMutationResponse:
    ResumeService(database).trash(resume_id)
    return ResumeMutationResponse(id=resume_id, status="trashed")


@router.post("/{resume_id}/restore", response_model=ResumeMutationResponse)
def restore_resume(
    resume_id: str,
    _context: object = Depends(require_csrf),
    database: Session = Depends(get_database_session),
) -> ResumeMutationResponse:
    ResumeService(database).restore(resume_id)
    return ResumeMutationResponse(id=resume_id, status="active")


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(
    resume_id: str,
    _context: object = Depends(require_csrf),
    database: Session = Depends(get_database_session),
) -> Response:
    ResumeService(database).permanently_delete(resume_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
