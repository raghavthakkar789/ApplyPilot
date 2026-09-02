from sqlalchemy import select
from sqlalchemy.orm import Session

from applypilot.models.installation import Installation
from applypilot.models.owner_account import OwnerAccount


class OwnerRepository:
    def __init__(self, database: Session) -> None:
        self.database = database

    def installation(self) -> Installation | None:
        return self.database.get(Installation, 1)

    def owner(self) -> OwnerAccount | None:
        return self.database.scalar(select(OwnerAccount).limit(1))
