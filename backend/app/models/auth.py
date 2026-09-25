from typing import Optional

from pydantic import BaseModel, EmailStr


class UserProfile(BaseModel):
    """User profile information."""

    id: str
    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None


class TokenResponse(BaseModel):
    """OAuth token response."""

    access_token: str
    token_type: str
