from sqlalchemy import select
from sqlalchemy.orm import Session

from applypilot.models.job import AtsRegistryEntry, SourceSyncRun


class SourceRegistryRepository:
    def __init__(self, database: Session) -> None:
        self.database = database

    def entries(self) -> list[AtsRegistryEntry]:
        return list(
            self.database.scalars(select(AtsRegistryEntry).order_by(AtsRegistryEntry.employer_name))
        )

    def entry(self, entry_id: str, lock: bool = False) -> AtsRegistryEntry | None:
        query = select(AtsRegistryEntry).where(AtsRegistryEntry.id == entry_id)
        return self.database.scalar(query.with_for_update() if lock else query)

    def active_run(self, provider: str) -> SourceSyncRun | None:
        return self.database.scalar(
            select(SourceSyncRun).where(
                SourceSyncRun.provider == provider, SourceSyncRun.status == "running"
            )
        )
