from pydantic import BaseModel, EmailStr, Field, field_validator
from beanie import PydanticObjectId
from app.users.model import Role
from app.shared.validators import is_valid_rut

class UserBase(BaseModel):
    username: str
    email: EmailStr
    rut: str
    first_name: str
    last_name: str
    role: Role = Role.STAFF
    is_active: bool = True

    @field_validator("rut")
    @classmethod
    def validate_user_rut(cls, v: str) -> str:
        if not is_valid_rut(v):
            raise ValueError("RUT no es válido")
        return v.strip().upper()

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    rut: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    password: str | None = Field(None, min_length=6)
    role: Role | None = None
    is_active: bool | None = None

    @field_validator("rut")
    @classmethod
    def validate_user_rut(cls, v: str | None) -> str | None:
        if v is not None:
            if not is_valid_rut(v):
                raise ValueError("RUT no es válido")
            return v.strip().upper()
        return v

class UserResponse(UserBase):
    id: PydanticObjectId
