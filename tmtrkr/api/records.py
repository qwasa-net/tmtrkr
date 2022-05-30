"""API for the records (GET/POST/UPADTE/DELETE)."""
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi import status as status_code
from tmtrkr import models, settings
from tmtrkr.api import schemas
from tmtrkr.api.users import get_user

__all__ = ["api"]

api = APIRouter()


class CommonQueryParams:
    """Common GET query paramters."""

    def __init__(
        self,
        queryset_type: Any,
        offset: int = 0,
        limit: int = settings.API_PAGE_SIZE_LIMIT,
    ):
        """."""
        self.queryset_type = queryset_type
        self.offset = offset
        self.limit = min(settings.API_PAGE_SIZE_LIMIT, max(limit, 1))

    def apply(self, queryset):
        """Apply common paramaters [offset, limit]."""
        if self.offset:
            queryset = queryset.offset(self.offset)
        if self.limit:
            queryset = queryset.limit(self.limit)
        return queryset


class RecordsQueryParams(CommonQueryParams):
    """Records specific filters."""

    def __init__(
        self,
        start_min: Optional[int] = None,
        start_max: Optional[int] = None,
        is_deleted: Optional[bool] = False,
        order_by: Optional[str] = None,
        offset: int = 0,
        limit: int = settings.API_PAGE_SIZE_LIMIT,
    ):
        """."""
        self.start_min = start_min
        self.start_max = start_max
        self.is_deleted = is_deleted
        self.order_by = order_by
        super().__init__(models.Record, offset, limit)

    def apply(self, queryset):
        """Apply records filtering (start interval)."""
        if self.start_min:
            queryset = queryset.filter(models.Record.start >= self.start_min)
        if self.start_max:
            queryset = queryset.filter(models.Record.start <= self.start_max)
        if self.is_deleted is not None:
            queryset = queryset.filter(models.Record.is_deleted.is_(self.is_deleted))
        if self.order_by is None:
            queryset = queryset.order_by(models.Record.start.desc())
        else:
            raise HTTPException(status_code=status_code.HTTP_501_NOT_IMPLEMENTED)
        return super().apply(queryset)


@api.get("/", response_model=schemas.RecordsOutputList)
def get_records(
    params: RecordsQueryParams = Depends(RecordsQueryParams),
    user=Depends(get_user),
    db=Depends(models.db_session),
) -> schemas.RecordsOutputList:
    """Get list of records."""

    # query records
    queryset = models.Record.query(db, user=user)
    records = params.apply(queryset)

    # build response
    rsp = {}
    rsp["records"] = [record.as_dict() for record in records]
    rsp["count"] = len(rsp["records"])
    rsp["duration"] = sum(filter(None, (r["duration"] for r in rsp["records"])))
    starts = list(filter(None, (r.get("start") for r in rsp["records"])))
    ends = list(filter(None, (r.get("start") for r in rsp["records"])))
    if starts:
        rsp["start_min"], rsp["start_max"] = min(starts), max(starts)
    if ends:
        rsp["end_min"], rsp["end_max"] = min(ends), max(ends)
    if params.start_min:
        rsp["query_start_min"] = params.start_min
    if params.start_max:
        rsp["query_start_max"] = params.start_max
    if user:
        rsp["user"] = user.as_dict()

    return rsp


@api.get("/{record_id}", response_model=schemas.RecordOutput)
def get_record(
    record_id: int,
    user=Depends(get_user),
    db=Depends(models.db_session),
) -> schemas.RecordOutput:
    """Get record by ID."""
    record = models.Record.first(db, id=record_id, user=user)
    if not record:
        raise HTTPException(status_code.HTTP_404_NOT_FOUND)
    return record.as_dict()


@api.post("/", response_model=schemas.RecordOutput, status_code=status_code.HTTP_201_CREATED)
def create_record(
    data: schemas.RecordInput,
    user=Depends(get_user),
    db=Depends(models.db_session),
) -> schemas.RecordOutput:
    """Create a new record."""
    record = models.Record(user=user, **data.dict())
    record.save(db)
    return record.as_dict()


@api.patch("/{record_id}", response_model=schemas.RecordOutput, status_code=status_code.HTTP_202_ACCEPTED)
def update_record(
    record_id: int,
    data: schemas.RecordInput,
    user=Depends(get_user),
    db=Depends(models.db_session),
) -> schemas.RecordOutput:
    """Update record."""
    record = models.Record.first(db, id=record_id, user=user)
    if not record:
        raise HTTPException(status_code.HTTP_404_NOT_FOUND)
    record.update(**data.dict())
    record.save(db)
    return record.as_dict()


@api.delete("/{record_id}", response_model=schemas.RecordOutput)
def delete_record(
    record_id: int,
    user=Depends(get_user),
    db=Depends(models.db_session),
) -> schemas.RecordOutput:
    """Mark record as deleted."""
    record = models.Record.first(db, id=record_id, user=user)
    if not record:
        raise HTTPException(status_code.HTTP_404_NOT_FOUND)
    record.is_deleted = True
    record.save(db)
    return record.as_dict()
