from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from app.database import get_db
from app.middleware import require_role
from app.schemas.basic import SupplierCreate

router = APIRouter(prefix="/api/v1/suppliers", tags=["刀具供应商"])


@router.get("")
async def list_suppliers(current=Depends(require_role("admin", "viewer"))):
    db = get_db()
    cursor = db.suppliers.find().sort("name", 1)
    records = await cursor.to_list(length=500)
    for r in records:
        r["id"] = str(r.pop("_id"))
    return records


@router.post("")
async def create_supplier(data: SupplierCreate,
                          current=Depends(require_role("admin"))):
    db = get_db()
    exists = await db.suppliers.find_one({"name": data.name})
    if exists:
        raise HTTPException(status_code=400, detail="该供应商已存在")
    await db.suppliers.insert_one(data.model_dump())
    return {"message": "ok"}


@router.put("/{supplier_id}")
async def update_supplier(supplier_id: str, data: SupplierCreate,
                          current=Depends(require_role("admin"))):
    db = get_db()
    result = await db.suppliers.update_one(
        {"_id": ObjectId(supplier_id)},
        {"$set": data.model_dump()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="未找到该供应商")
    return {"message": "ok"}


@router.delete("/{supplier_id}")
async def delete_supplier(supplier_id: str,
                          current=Depends(require_role("admin"))):
    db = get_db()
    result = await db.suppliers.delete_one({"_id": ObjectId(supplier_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="未找到该供应商")
    return {"message": "ok"}
