from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from applypilot.api.dependencies.authentication import require_authentication
from applypilot.api.dependencies.csrf import require_csrf
from applypilot.models.job import CanonicalJob, RawJobRecord, SourceSyncRun
from applypilot.repositories.database import get_database_session
from applypilot.repositories.job_repository import JobRepository
from applypilot.schemas.job import (
    JobListResponse,
    JobResponse,
    JobSourceResponse,
    JobVersionResponse,
)
from applypilot.services.job_catalog_service import JobCatalogService

router = APIRouter(prefix="/jobs", tags=["jobs"])


def job_response(job: CanonicalJob, repository: JobRepository) -> JobResponse:
    version = repository.version(job.current_version_id)
    if version is None:
        raise HTTPException(500, "Job version unavailable.")
    sources = []
    for link in repository.links(job.id):
        raw = repository.database.get(RawJobRecord, link.raw_job_record_id)
        retrieved = raw.last_seen_at if raw else version.created_at
        sources.append(
            JobSourceResponse(
                provider=raw.provider if raw else "unknown",
                source_url=link.source_url,
                application_url=link.application_url,
                attribution=link.attribution,
                retrieved_at=retrieved,
            )
        )
    data = version.normalized_data

    def optional_text(key: str) -> str | None:
        value = data.get(key)
        return value if isinstance(value, str) else None

    return JobResponse(
        id=job.id,
        title=version.title,
        employer=version.employer,
        description=version.description_text,
        location=optional_text("location"),
        work_mode=optional_text("work_mode"),
        employment_type=optional_text("employment_type"),
        freshness_state=version.freshness_state,
        saved=job.saved,
        version_number=version.version_number,
        created_at=version.created_at,
        sources=sources,
    )


@router.get("", response_model=JobListResponse, dependencies=[Depends(require_authentication)])
def list_jobs(
    q: str | None = Query(default=None, max_length=200),
    source: str | None = None,
    database: Session = Depends(get_database_session),
) -> JobListResponse:
    repository = JobRepository(database)
    jobs = [job_response(item, repository) for item in repository.jobs()]
    if q:
        jobs = [
            item
            for item in jobs
            if q.casefold() in f"{item.title} {item.employer} {item.description}".casefold()
        ]
    if source:
        jobs = [item for item in jobs if any(link.provider == source for link in item.sources)]
    failed = list(
        database.scalars(
            select(SourceSyncRun)
            .where(SourceSyncRun.status == "failed")
            .order_by(SourceSyncRun.started_at.desc())
            .limit(4)
        )
    )
    return JobListResponse(
        jobs=jobs,
        partial_failures=[f"{item.provider} source is temporarily unavailable" for item in failed],
    )


@router.get("/{job_id}", response_model=JobResponse, dependencies=[Depends(require_authentication)])
def read_job(job_id: str, database: Session = Depends(get_database_session)) -> JobResponse:
    repository = JobRepository(database)
    job = repository.job(job_id)
    if job is None:
        raise HTTPException(404, "Job not found.")
    return job_response(job, repository)


@router.get(
    "/{job_id}/versions",
    response_model=list[JobVersionResponse],
    dependencies=[Depends(require_authentication)],
)
def read_job_versions(
    job_id: str, database: Session = Depends(get_database_session)
) -> list[JobVersionResponse]:
    repository = JobRepository(database)
    if repository.job(job_id) is None:
        raise HTTPException(404, "Job not found.")
    return [
        JobVersionResponse.model_validate(item, from_attributes=True)
        for item in repository.versions(job_id)
    ]


@router.post("/{job_id}/save", response_model=JobResponse)
def save_job(
    job_id: str,
    _context: object = Depends(require_csrf),
    database: Session = Depends(get_database_session),
) -> JobResponse:
    job = JobCatalogService(database).set_saved(job_id, True)
    return job_response(job, JobRepository(database))


@router.delete("/{job_id}/save", response_model=JobResponse)
def unsave_job(
    job_id: str,
    _context: object = Depends(require_csrf),
    database: Session = Depends(get_database_session),
) -> JobResponse:
    job = JobCatalogService(database).set_saved(job_id, False)
    return job_response(job, JobRepository(database))
