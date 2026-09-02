from pydantic import BaseModel


class LoginRequest(BaseModel):
    password: str


class AuthenticationResponse(BaseModel):
    authenticated: bool
