from enum import Enum
from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime, timezone

class Role(str, Enum):
    ADMIN = "admin"
    STAFF = "staff"

class User(Document):
    username: Indexed(str, unique=True)
    email: Indexed(str, unique=True)
    rut: Indexed(str, unique=True) = ""
    first_name: str = ""
    last_name: str = ""
    hashed_password: str
    role: Role = Role.STAFF
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "users"
