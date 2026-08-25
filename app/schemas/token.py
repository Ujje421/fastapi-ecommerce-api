from pydantic import BaseModel

class Token(BaseModel):
    """JWT Token response schema."""
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    """Payload contained inside the JWT."""
    sub: str | None = None
