from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProfileSections(BaseModel):
    model_config = ConfigDict(extra="forbid")

    identity: dict[str, object] = Field(default_factory=dict)
    contact: dict[str, object] = Field(default_factory=dict)
    current_location: dict[str, object] = Field(default_factory=dict)
    professional_summary: dict[str, object] = Field(default_factory=dict)
    desired_roles: list[dict[str, object]] = Field(default_factory=list)
    skills: list[dict[str, object]] = Field(default_factory=list)
    employment_history: list[dict[str, object]] = Field(default_factory=list)
    education: list[dict[str, object]] = Field(default_factory=list)
    projects: list[dict[str, object]] = Field(default_factory=list)
    certifications: list[dict[str, object]] = Field(default_factory=list)
    languages: list[dict[str, object]] = Field(default_factory=list)
    portfolio_links: list[dict[str, object]] = Field(default_factory=list)
    work_preferences: dict[str, object] = Field(default_factory=dict)
    availability: dict[str, object] = Field(default_factory=dict)
    compensation: dict[str, object] = Field(default_factory=dict)
    relocation: dict[str, object] = Field(default_factory=dict)
    work_authorization: dict[str, object] = Field(default_factory=dict)


class ProfileResponse(BaseModel):
    sections: ProfileSections
    created_at: datetime | None
    updated_at: datetime | None
