from pydantic import BaseModel, EmailStr

from app.schemas.user import User


class Token(BaseModel):
    """JWT token response schema."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """JWT token payload schema."""

    sub: str | None = None


class LoginRequest(BaseModel):
    """Login request schema."""

    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Login response schema with user info and token."""

    user: User
    access_token: str
    token_type: str = "bearer"


class SignupRequest(BaseModel):
    """Signup request schema."""

    email: EmailStr
    password: str
    full_name: str | None = None


class SignupResponse(BaseModel):
    """Signup response schema."""

    user: User
    message: str = "User created successfully"


