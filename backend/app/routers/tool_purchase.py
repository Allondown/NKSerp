from datetime import datetime

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from app.database import get_db
from app.middleware import require_role
from app.schemas.business import ToolPurchaseCreate

router = APIRouter(prefix="/api/v1/tool-purchases", tags=["刀具采购"])


@router.post("")
async def create_tool_purchase(data: ToolPurchaseCreate,
                               current=Depends(require_role("admin"))):
    db = get_db()
    total_amount = round(data.quantity * data.unit_price, 2)
    record = {
        **data.model_dump(),
        "order_date": datetime.combine(data.order_date, datetime.min.time()),
        "arrival_date": datetime.combine(data.arrival_date, datetime.min.time()) if data.arrival_date else None,
        "total_amount": total_amount,
        "created_at": datetime.utcnow(),
    }
    result = await db.tool_purchases.insert_one(record)
    return {"message": "ok", "id": str(result.inserted_id)}


@router.get("")
async def list_tool_purchases(year: int | None = None,
                              month: int | None = None,
                              status: str | None = None,
                              page: int = 1, page_size: int = 200,
                              current=Depends(require_role("admin", "viewer"))):
    db = get_db()
    q = {}
    if year and month:
        from calendar import monthrange
        last_day = monthrange(year, month)[1]
        q["order_date"] = {
            "$gte": datetime(year, month, 1),
            "$lte": datetime(year, month, last_day),
        }
    if status == "arrived":
        q["arrival_date"] = {"$ne": None}
    elif status == "pending":
        q["arrival_date"] = None

    cursor = db.tool_purchases.find(q).sort("order_date", -1)
    total = await db.tool_purchases.count_documents(q)
    records = await cursor.skip((page - 1) * page_size).limit(page_size).to_list(length=page_size)
    for r in records:
        r["id"] = str(r.pop("_id"))
    return {"total": total, "items": records, "page": page, "page_size": page_size}


@router.put("/{record_id}")
async def update_tool_purchase(record_id: str, data: ToolPurchaseCreate,
                               current=Depends(require_role("admin"))):
    db = get_db()
    total_amount = round(data.quantity * data.unit_price, 2)
    result = await db.tool_purchases.update_one(
        {"_id": ObjectId(record_id)},
        {"$set": {
            **data.model_dump(),
            "order_date": datetime.combine(data.order_date, datetime.min.time()),
            "arrival_date": datetime.combine(data.arrival_date, datetime.min.time()) if data.arrival_date else None,
            "total_amount": total_amount,
        }}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="未找到该记录")
    return {"message": "ok"}


@router.delete("/{record_id}")
async def delete_tool_purchase(record_id: str,
                               current=Depends(require_role("admin"))):
    db = get_db()
    result = await db.tool_purchases.delete_one({"_id": ObjectId(record_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="未找到该记录")
    return {"message": "ok"}
