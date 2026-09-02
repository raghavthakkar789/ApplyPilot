from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from applypilot.api.dependencies.authentication import require_authentication
from applypilot.api.dependencies.csrf import require_csrf
from applypilot.repositories.database import get_database_session
from applypilot.repositories.source_registry_repository import SourceRegistryRepository
from applypilot.schemas.job import RegistryInput, RegistryResponse
from applypilot.services.source_registry_service import SourceRegistryService

router = APIRouter(prefix="/source-registry", tags=["source-registry"])


def response(item: object) -> RegistryResponse:
    return RegistryResponse.model_validate(item, from_attributes=True)


@router.get(
    "", response_model=list[RegistryResponse], dependencies=[Depends(require_authentication)]
)
def list_registry(database: Session = Depends(get_database_session)) -> list[RegistryResponse]:
    return [response(item) for item in SourceRegistryRepository(database).entries()]


@router.post("", response_model=RegistryResponse)
async def create_registry(
    value: RegistryInput,
    _context: object = Depends(require_csrf),
    database: Session = Depends(get_database_session),
) -> RegistryResponse:
    return response(await SourceRegistryService(database).create_and_validate(value))


@router.post("/{entry_id}/enabled", response_model=RegistryResponse)
def set_enabled(
    entry_id: str,
    enabled: bool,
    _context: object = Depends(require_csrf),
    database: Session = Depends(get_database_session),
) -> RegistryResponse:
    return response(SourceRegistryService(database).set_enabled(entry_id, enabled))
