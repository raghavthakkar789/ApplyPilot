from pydantic import BaseModel, Field


class InitializationStatus(BaseModel):
    required: bool


class InitializationRequest(BaseModel):
    password: str = Field(min_length=1, max_length=1024)
    password_confirmation: str = Field(min_length=1, max_length=1024)
