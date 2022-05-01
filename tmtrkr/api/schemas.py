"""API data schemas."""
import re
from typing import List, Optional

from pydantic import BaseModel, root_validator, validator


class User(BaseModel):
    """User model."""

    id: int
    name: str


class Record(BaseModel):
    """Record base model."""

    start: Optional[int]
    end: Optional[int]
    name: str
    tags: Optional[str]


class RecordInput(Record):
    """Record input model (for POST/PUT requests)."""

    @validator("name")
    def name_length(cls, v):
        """Record name must be not empty."""
        if not v or len(str(v).strip()) == 0:
            raise ValueError("Empty name")
        return str(v).strip()

    @validator("start")
    def start_exists(cls, v):
        """Start must be defined."""
        if not v:
            raise ValueError("Empty start")
        return v

    @root_validator
    def start_end_sanity(cls, values):
        """Start must be before the End (if defined)."""
        start, end = values.get("start"), values.get("end")
        if start is not None and end is not None and end < start:
            raise ValueError("End < Start")
        return values

    @validator("tags")
    def tags_clean(cls, v):
        """Split the tags line."""
        if v:
            vs = re.split(r"\s+", re.sub(r"[^a-zA-Z0-9\s]", "", str(v).strip().lower()))
            v = " ".join(vs)
        return v


class RecordOutput(Record):
    """Record output model (for listing/details requests)."""

    id: Optional[int]
    duration: Optional[float]
    is_deleted: Optional[bool]
    user_id: Optional[int]
    user: Optional[User]


class RecordsOutputList(BaseModel):
    """Records list model."""

    records: List[RecordOutput]
    count: int
    duration: Optional[float]
    start_min: Optional[int]
    start_max: Optional[int]
    end_min: Optional[int]
    end_max: Optional[int]
    query_start_min: Optional[int]
    query_start_max: Optional[int]
