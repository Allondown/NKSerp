from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from app.database import get_db
from app.middleware import require_role
from app.schemas.basic import MachineCreate, MachineResponse

router = APIRouter(prefix="/api/v1/machines", tags=["机器管理"])


@router.get("", response_model=list[MachineResponse])
async def list_machines(current=Depends(require_role("admin", "viewer"))):
    db = get_db()
    cursor = db.machines.find().sort("machine_name", 1)
    return await cursor.to_list(length=100)


@router.post("")
async def create_machine(data: MachineCreate,
                         current=Depends(require_role("admin"))):
    db = get_db()
    exists = await db.machines.find_one({"machine_name": data.machine_name})
    if exists:
        raise HTTPException(status_code=400, detail="机器已存在")
    await db.machines.insert_one(data.model_dump())
    return {"message": "ok"}


@router.delete("/{machine_name}")
async def delete_machine(machine_name: str,
                         current=Depends(require_role("admin"))):
    db = get_db()
    result = await db.machines.delete_one({"machine_name": machine_name})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="未找到该机器")
    return {"message": "ok"}
