from datetime import datetime

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from app.database import get_db
from app.middleware import require_role
from app.schemas.business import PurchaseCreate
from app.services.inventory_service import (reverse_inventory_after_purchase,
                                             update_inventory_after_purchase)

router = APIRouter(prefix="/api/v1/purchases", tags=["采购入库"])


@router.post("")
async def create_purchase(data: PurchaseCreate,
                          current=Depends(require_role("admin", "warehouse"))):
    db = get_db()
    total_price = round(data.weight_kg * data.unit_price, 2)
    record = {
        **data.model_dump(),
        "arrival_date": datetime.combine(data.arrival_date, datetime.min.time()),
        "total_price": total_price,
        "created_at": datetime.utcnow()
    }
    result = await db.purchase_records.insert_one(record)

    await update_inventory_after_purchase(data.material_spec, data.weight_kg, total_price)

    record["_id"] = str(result.inserted_id)
    return {"message": "ok", "id": str(result.inserted_id)}


@router.get("")
async def list_purchases(material_spec: str | None = None,
                         start_date: str | None = None,
                         end_date: str | None = None,
                         page: int = 1, page_size: int = 50,
                         current=Depends(require_role("admin", "warehouse", "workshop", "viewer"))):
    db = get_db()
    q = {}
    if material_spec:
        q["material_spec"] = material_spec
    if start_date or end_date:
        q["arrival_date"] = {}
        if start_date:
            q["arrival_date"]["$gte"] = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            q["arrival_date"]["$lte"] = datetime.strptime(end_date, "%Y-%m-%d")
    cursor = db.purchase_records.find(q).sort("arrival_date", -1)
    total = await db.purchase_records.count_documents(q)
    records = await cursor.skip((page - 1) * page_size).limit(page_size).to_list(length=page_size)
    for r in records:
        r["id"] = str(r.pop("_id"))
    return {"total": total, "items": records, "page": page, "page_size": page_size}


@router.delete("/{record_id}")
async def delete_purchase(record_id: str,
                          current=Depends(require_role("admin"))):
    db = get_db()
    record = await db.purchase_records.find_one({"_id": ObjectId(record_id)})
    if not record:
        raise HTTPException(status_code=404, detail="未找到该记录")
    await reverse_inventory_after_purchase(
        record["material_spec"], record["weight_kg"], record["total_price"]
    )
    await db.purchase_records.delete_one({"_id": ObjectId(record_id)})
    return {"message": "ok"}


@router.put("/{record_id}")
async def update_purchase(record_id: str, data: PurchaseCreate,
                          current=Depends(require_role("admin", "warehouse"))):
    """编辑采购记录：回滚旧库存影响后应用新数据。"""
    db = get_db()
    old = await db.purchase_records.find_one({"_id": ObjectId(record_id)})
    if not old:
        raise HTTPException(status_code=404, detail="未找到该记录")

    await reverse_inventory_after_purchase(
        old["material_spec"], old["weight_kg"], old["total_price"]
    )

    total_price = round(data.weight_kg * data.unit_price, 2)
    await db.purchase_records.update_one(
        {"_id": ObjectId(record_id)},
        {"$set": {
            **data.model_dump(),
            "arrival_date": datetime.combine(data.arrival_date, datetime.min.time()),
            "total_price": total_price,
        }}
    )

    await update_inventory_after_purchase(data.material_spec, data.weight_kg, total_price)
    return {"message": "ok"}
