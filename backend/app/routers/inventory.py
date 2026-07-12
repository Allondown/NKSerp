from fastapi import APIRouter, Depends

from app.database import get_db
from app.middleware import require_role
from app.services.inventory_service import get_current_inventory

router = APIRouter(prefix="/api/v1/inventory", tags=["库存查询"])


@router.get("/current")
async def inventory_current(material_spec: str | None = None,
                            current=Depends(require_role("admin", "viewer"))):
    result = await get_current_inventory(material_spec)
    for r in result:
        r["id"] = str(r.pop("_id"))
    return result
