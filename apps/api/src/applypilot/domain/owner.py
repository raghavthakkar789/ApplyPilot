from dataclasses import dataclass


@dataclass(frozen=True)
class AuthenticatedOwner:
    owner_id: int
    credential_version: int
