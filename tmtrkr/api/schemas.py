"""API data schemas."""
import re
import time
from typing import List, Optional

from pydantic import BaseModel, model_validator, field_validator


class User(BaseModel):
    """User model."""

    id: int
    name: str


class UserList(BaseModel):
    """User list model."""

    users: List[User]


class Record(BaseModel):
    """Record base model."""

    start: Optional[int] = None
    end: Optional[int] = None
    name: str
    tags: Optional[str] = None


class RecordInput(Record):
    """Record input model (for POST/PUT requests)."""

    @field_validator("name")
    def name_length(cls, v):
        """Record name must be not empty."""
        if not v or len(str(v).strip()) == 0:
            raise ValueError("Empty name")
        return str(v).strip()

    @field_validator("start")
    def start_exists(cls, v):
        """Start must be defined."""
        if not v:
            raise ValueError("Empty start")
        return v

    @model_validator(mode="after")
    def start_end_sanity(self):
        """Start must be before the End (if defined)."""
        if self.start is not None and self.end is not None and self.end < self.start:
            raise ValueError("End < Start")
        return self

    @field_validator("tags")
    def tags_clean(cls, v):
        """Split the tags line."""
        if v:
            vs = re.split(r"\s+", re.sub(r"[^a-zA-Z0-9\s]", "", str(v).strip().lower()))
            v = " ".join(vs)
        return v


class RecordOutput(Record):
    """Record output model (for listing/details requests)."""

    id: int
    duration: Optional[float] = None
    is_deleted: Optional[bool] = None
    user_id: Optional[int] = None


class RecordsOutputList(BaseModel):
    """Records list model."""

    records: List[RecordOutput]
    count: int
    duration: Optional[float] = None
    start_min: Optional[int] = None
    start_max: Optional[int] = None
    end_min: Optional[int] = None
    end_max: Optional[int] = None
    query_start_min: Optional[int] = None
    query_start_max: Optional[int] = None
    user: Optional[User] = None


class TokenData(BaseModel):
    """Access token data."""

    username: str
    userid: Optional[int]
    expire: int = int(time.time() + 60 * 60)

    @field_validator("username")
    def name_not_empty(cls, v):
        """User name must be not empty."""
        if not v or len(str(v).strip()) == 0:
            raise ValueError("empty username")
        return str(v).strip()

    @field_validator("expire")
    def not_expired(cls, v):
        """Must be not expired."""
        if int(v) < int(time.time()):
            raise ValueError("token expired")
        return v


class TokenResponse(BaseModel):
    """JWT token encoded."""

    token: str
