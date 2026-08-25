import uuid
from pydantic import BaseModel, ConfigDict, EmailStr

# Shared properties
class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None
    is_active: bool | None = True
    is_superuser: bool | None = False

# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str

# Properties to receive via API on update
class UserUpdate(UserBase):
    password: str | None = None

# Additional properties to return via API
class UserResponse(UserBase):
    id: uuid.UUID
    
    model_config = ConfigDict(from_attributes=True)
