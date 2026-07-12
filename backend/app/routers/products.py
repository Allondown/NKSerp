from fastapi import APIRouter, Depends, HTTPException

from app.database import get_db
from app.middleware import require_role
from app.schemas.basic import ProductCreate, ProductResponse

router = APIRouter(prefix="/api/v1/products", tags=["产品主数据"])


@router.get("", response_model=list[ProductResponse])
async def list_products(month: str | None = None,
                        product_code: str | None = None,
                        current=Depends(require_role("admin", "viewer"))):
    db = get_db()
    q = {}
    if month:
        q["month"] = month
    if product_code:
        q["product_code"] = {"$regex": product_code, "$options": "i"}
    cursor = db.product_master.find(q).sort("product_code", 1)
    return await cursor.to_list(length=500)


@router.get("/{product_code}")
async def get_product(product_code: str,
                      current=Depends(require_role("admin", "viewer"))):
    """按产品编号查询最近一条主数据，用于日报自动带出。"""
    db = get_db()
    record = await db.product_master.find_one(
        {"product_code": product_code},
        sort=[("month", -1)]
    )
    if not record:
        return None
    return {
        "product_name": record.get("product_name", ""),
        "material_spec": record.get("material_spec", ""),
        "cycle_sec": record.get("cycle_sec", 0),
        "work_time_sec": record.get("work_time_sec", 0),
        "monthly_plan": record.get("monthly_plan", 0),
        "loss_remark": record.get("loss_remark", ""),
    }


@router.post("")
async def create_product(data: ProductCreate,
                         current=Depends(require_role("admin"))):
    db = get_db()
    await db.product_master.update_one(
        {"product_code": data.product_code, "month": data.month},
        {"$set": data.model_dump()},
        upsert=True
    )
    return {"message": "ok"}


@router.put("")
async def update_product(data: ProductCreate,
                         original_code: str, original_month: str,
                         current=Depends(require_role("admin"))):
    """编辑产品主数据。"""
    db = get_db()
    result = await db.product_master.update_one(
        {"product_code": original_code, "month": original_month},
        {"$set": data.model_dump()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="未找到该产品")
    return {"message": "ok"}


@router.delete("/{product_code}/{month}")
async def delete_product(product_code: str, month: str,
                         current=Depends(require_role("admin"))):
    db = get_db()
    result = await db.product_master.delete_one(
        {"product_code": product_code, "month": month}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="未找到该产品")
    return {"message": "ok"}
