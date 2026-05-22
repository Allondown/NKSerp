from datetime import datetime

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from app.database import get_db
from app.middleware import require_role
from app.schemas.business import IssueCreate
from app.services.inventory_service import (reverse_inventory_after_issue,
                                             update_inventory_after_issue)

router = APIRouter(prefix="/api/v1/issues", tags=["领用出库"])


@router.post("")
async def create_issue(data: IssueCreate,
                       current=Depends(require_role("admin", "warehouse"))):
    db = get_db()
    try:
        total_cost = await update_inventory_after_issue(data.material_spec,
                                                        data.issue_weight_kg)
        total_cost = round(total_cost, 2)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    inv = await db.inventory_snapshot.find_one({"material_spec": data.material_spec})
    unit_cost = inv["avg_price"] if inv else 0

    record = {
        **data.model_dump(),
        "issue_date": datetime.combine(data.issue_date, datetime.min.time()),
        "unit_cost": round(unit_cost, 4),
        "total_cost": total_cost,
        "created_at": datetime.utcnow()
    }
    result = await db.issue_records.insert_one(record)
    return {"message": "ok", "id": str(result.inserted_id)}


@router.get("")
async def list_issues(material_spec: str | None = None,
                      start_date: str | None = None,
                      end_date: str | None = None,
                      page: int = 1, page_size: int = 50,
                      current=Depends(require_role("admin", "warehouse", "workshop", "viewer"))):
    db = get_db()
    q = {}
    if material_spec:
        q["material_spec"] = material_spec
    if start_date or end_date:
        q["issue_date"] = {}
        if start_date:
            q["issue_date"]["$gte"] = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            q["issue_date"]["$lte"] = datetime.strptime(end_date, "%Y-%m-%d")
    cursor = db.issue_records.find(q).sort("issue_date", -1)
    total = await db.issue_records.count_documents(q)
    records = await cursor.skip((page - 1) * page_size).limit(page_size).to_list(length=page_size)
    for r in records:
        r["id"] = str(r.pop("_id"))
    return {"total": total, "items": records, "page": page, "page_size": page_size}


@router.delete("/{record_id}")
async def delete_issue(record_id: str,
                       current=Depends(require_role("admin"))):
    db = get_db()
    record = await db.issue_records.find_one({"_id": ObjectId(record_id)})
    if not record:
        raise HTTPException(status_code=404, detail="未找到该记录")
    await reverse_inventory_after_issue(
        record["material_spec"], record["issue_weight_kg"], record["total_cost"]
    )
    await db.issue_records.delete_one({"_id": ObjectId(record_id)})
    return {"message": "ok"}
