from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from applypilot.api.dependencies.csrf import require_csrf
from applypilot.api.routes.jobs import job_response
from applypilot.repositories.database import get_database_session
from applypilot.repositories.job_repository import JobRepository
from applypilot.schemas.job import JobResponse, ManualJobInput
from applypilot.services.job_catalog_service import JobCatalogService

router = APIRouter(prefix="/manual-jobs", tags=["manual-jobs"])


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_manual_job(
    value: ManualJobInput,
    _context: object = Depends(require_csrf),
    database: Session = Depends(get_database_session),
) -> JobResponse:
    job = JobCatalogService(database).create_manual(value)
    return job_response(job, JobRepository(database))
