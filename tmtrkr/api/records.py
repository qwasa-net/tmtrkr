"""API for the records (GET/POST/UPADTE/DELETE)."""
from fastapi import APIRouter, Depends, HTTPException

import tmtrkr.api.schemas as schemas
import tmtrkr.models as models
from tmtrkr.api.users import get_user

api = APIRouter()

LIMIT_MAX = 1000


@api.get("/", response_model=schemas.RecordsOutputList)
def get_records(
    start_min: int = None,
    start_max: int = None,
    limit: int = 1000,
    offset: int = 0,
    user=Depends(get_user),
    db=Depends(models.get_db),
) -> schemas.RecordsOutputList:
    """Get list of records."""
    limit = max(LIMIT_MAX, min(limit, 1))

    # query records
    records = models.Record.query(db, user=user)
    records = records.filter(models.Record.is_deleted.isnot(True))
    if start_min:
        records = records.filter(models.Record.start >= start_min)
    if start_max:
        records = records.filter(models.Record.start <= start_max)
    records = records.order_by(models.Record.start.desc())
    if limit or offset:
        records = records.limit(limit).offset(offset)

    # build response
    rsp = {"records": [], "count": 0}
    for record in records:
        rsp["records"].append(record.as_dict())
    rsp["count"] = len(rsp["records"])
    rsp["duration"] = sum(filter(None, (r["duration"] for r in rsp["records"])))
    starts = list(filter(None, (r.get("start") for r in rsp["records"])))
    ends = list(filter(None, (r.get("start") for r in rsp["records"])))
    if starts:
        rsp["start_min"], rsp["start_max"] = min(starts), max(starts)
    if ends:
        rsp["end_min"], rsp["end_max"] = min(ends), max(ends)
    if start_min:
        rsp["query_start_min"] = start_min
    if start_max:
        rsp["query_start_max"] = start_max

    return rsp


@api.get("/{record_id}", response_model=schemas.Record)
def get_record(record_id: int, user=Depends(get_user), db=Depends(models.get_db)):
    """Get record by ID."""
    record = models.Record.first(db, id=record_id, user=user)
    if not record:
        raise HTTPException(404)
    return record.as_dict()


@api.post("/")
def create_record(data: schemas.RecordInput, user=Depends(get_user), db=Depends(models.get_db)):
    """Create a new record."""
    record = models.Record(user=user, **data.dict())
    record.save(db)
    return record


@api.patch("/{record_id}")
def update_record(
    record_id: int,
    data: schemas.RecordInput,
    user=Depends(get_user),
    db=Depends(models.get_db),
):
    """Update record."""
    record = models.Record.first(db, id=record_id, user=user)
    if not record:
        raise HTTPException(404)
    record.update(**data.dict())
    record.save(db)
    return record


@api.delete("/{record_id}")
def delete_record(record_id: int, user=Depends(get_user), db=Depends(models.get_db)) -> schemas.Record:
    """Mark record as deleted."""
    record = models.Record.first(db, id=record_id, user=user)
    if not record:
        raise HTTPException(404)
    record.is_deleted = True
    record.save(db)
    return record
