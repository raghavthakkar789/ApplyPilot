from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from applypilot.api.dependencies.authentication import require_authentication
from applypilot.api.dependencies.csrf import require_csrf
from applypilot.models.job import SourceSyncRun
from applypilot.repositories.database import get_database_session
from applypilot.schemas.job import SyncResponse
from applypilot.services.source_sync_service import SourceSyncService

router = APIRouter(prefix="/source-sync", tags=["source-sync"])


def response(item: SourceSyncRun) -> SyncResponse:
    return SyncResponse.model_validate(item, from_attributes=True)


@router.get("", response_model=list[SyncResponse], dependencies=[Depends(require_authentication)])
def list_syncs(database: Session = Depends(get_database_session)) -> list[SyncResponse]:
    items = database.scalars(
        select(SourceSyncRun).order_by(SourceSyncRun.started_at.desc()).limit(100)
    )
    return [response(item) for item in items]


@router.post("/{provider}", response_model=SyncResponse)
async def synchronize(
    provider: str,
    entry_id: str | None = None,
    _context: object = Depends(require_csrf),
    database: Session = Depends(get_database_session),
) -> SyncResponse:
    return response(await SourceSyncService(database).synchronize(provider, entry_id))


@router.get(
    "/{sync_id}", response_model=SyncResponse, dependencies=[Depends(require_authentication)]
)
def read_sync(sync_id: str, database: Session = Depends(get_database_session)) -> SyncResponse:
    item = database.get(SourceSyncRun, sync_id)
    if item is None:
        from fastapi import HTTPException

        raise HTTPException(404, "Synchronization not found.")
    return response(item)
