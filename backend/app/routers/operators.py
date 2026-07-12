from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from app.database import get_db
from app.middleware import require_role
from app.schemas.basic import OperatorCreate, OperatorResponse

router = APIRouter(prefix="/api/v1/operators", tags=["班组人员"])


@router.get("")
async def list_operators(current=Depends(require_role("admin", "viewer"))):
    db = get_db()
    cursor = db.operators.find().sort("name", 1)
    records = await cursor.to_list(length=500)
    for r in records:
        r["id"] = str(r.pop("_id"))
    return records


@router.post("")
async def create_operator(data: OperatorCreate,
                          current=Depends(require_role("admin"))):
    db = get_db()
    exists = await db.operators.find_one({"name": data.name})
    if exists:
        raise HTTPException(status_code=400, detail="该人员已存在")
    await db.operators.insert_one(data.model_dump())
    return {"message": "ok"}


@router.put("/{operator_id}")
async def update_operator(operator_id: str, data: OperatorCreate,
                          current=Depends(require_role("admin"))):
    db = get_db()
    result = await db.operators.update_one(
        {"_id": ObjectId(operator_id)},
        {"$set": data.model_dump()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="未找到该人员")
    return {"message": "ok"}


@router.delete("/{operator_id}")
async def delete_operator(operator_id: str,
                          current=Depends(require_role("admin"))):
    db = get_db()
    result = await db.operators.delete_one({"_id": ObjectId(operator_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="未找到该人员")
    return {"message": "ok"}
