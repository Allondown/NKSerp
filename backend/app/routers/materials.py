from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from app.database import get_db
from app.middleware import require_role
from app.schemas.basic import MaterialCreate, MaterialResponse

router = APIRouter(prefix="/api/v1/materials", tags=["材料规格"])


@router.get("", response_model=list[MaterialResponse])
async def list_materials(current=Depends(require_role("admin", "warehouse", "workshop", "viewer"))):
    db = get_db()
    cursor = db.materials.find().sort("material_spec", 1)
    return await cursor.to_list(length=500)


@router.post("")
async def create_material(data: MaterialCreate,
                          current=Depends(require_role("admin", "warehouse"))):
    db = get_db()
    exists = await db.materials.find_one({"material_spec": data.material_spec})
    if exists:
        raise HTTPException(status_code=400, detail="材料规格已存在")
    await db.materials.insert_one(data.model_dump())
    return {"message": "ok"}


@router.put("/{material_spec}")
async def update_material(material_spec: str, data: MaterialCreate,
                          current=Depends(require_role("admin", "warehouse"))):
    db = get_db()
    result = await db.materials.update_one(
        {"material_spec": material_spec},
        {"$set": data.model_dump()}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="未找到该材料")
    return {"message": "ok"}


@router.delete("/{material_spec}")
async def delete_material(material_spec: str,
                          current=Depends(require_role("admin"))):
    db = get_db()
    result = await db.materials.delete_one({"material_spec": material_spec})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="未找到该材料")
    return {"message": "ok"}
