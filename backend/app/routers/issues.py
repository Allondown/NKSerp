from datetime import datetime

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File

from app.database import get_db
from app.middleware import require_role
from app.schemas.business import IssueCreate
from app.services.inventory_service import (reverse_inventory_after_issue,
                                             update_inventory_after_issue)

router = APIRouter(prefix="/api/v1/issues", tags=["领用出库"])


@router.post("")
async def create_issue(data: IssueCreate,
                       current=Depends(require_role("admin"))):
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
                      current=Depends(require_role("admin", "viewer"))):
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


@router.post("/import")
async def import_issues(file: UploadFile = File(...),
                        current=Depends(require_role("admin"))):
    """从 Excel 文件批量导入领用出库记录。
    表头：日期 | 工作机器 | 产品编号 | 产品名称 | 材料材质及规格 | 钢材重量 | 领用人
    """
    import openpyxl
    from io import BytesIO

    db = get_db()
    contents = await file.read()
    wb = openpyxl.load_workbook(BytesIO(contents))
    ws = wb.active

    rows = list(ws.iter_rows(min_row=2, values_only=True))  # skip header
    if not rows:
        raise HTTPException(status_code=400, detail="Excel 文件中没有数据行")

    created = 0
    errors = []
    for i, row in enumerate(rows, start=2):
        if not row or all(v is None for v in row):
            continue
        try:
            date_val = row[0]
            machine = str(row[1] or "").strip()
            product_code = str(row[2] or "").strip()
            product_name = str(row[3] or "").strip()
            material_spec = str(row[4] or "").strip()
            weight = float(row[5] or 0)
            operator = str(row[6] or "").strip()

            # 解析日期
            if isinstance(date_val, datetime):
                issue_date = date_val
            elif isinstance(date_val, str):
                issue_date = datetime.strptime(date_val.strip(), "%Y-%m-%d")
            else:
                errors.append(f"第{i}行：日期格式错误")
                continue

            if not all([machine, product_code, material_spec, operator]):
                errors.append(f"第{i}行：缺少必填字段")
                continue
            if weight <= 0:
                errors.append(f"第{i}行：钢材重量必须大于0")
                continue

            # 计算库存成本
            try:
                total_cost = await update_inventory_after_issue(material_spec, weight)
                total_cost = round(total_cost, 2)
            except ValueError as e:
                errors.append(f"第{i}行：{e}")
                continue

            inv = await db.inventory_snapshot.find_one({"material_spec": material_spec})
            unit_cost = inv["avg_price"] if inv else 0

            record = {
                "issue_date": issue_date if isinstance(issue_date, datetime)
                              else datetime.combine(issue_date, datetime.min.time()),
                "machine": machine,
                "product_code": product_code,
                "product_name": product_name,
                "material_spec": material_spec,
                "issue_rods": 0,
                "issue_weight_kg": weight,
                "operator": operator,
                "remark": "",
                "unit_cost": round(unit_cost, 4),
                "total_cost": total_cost,
                "created_at": datetime.utcnow(),
            }
            await db.issue_records.insert_one(record)
            created += 1
        except Exception as e:
            errors.append(f"第{i}行：{str(e)}")

    return {"message": f"成功导入 {created} 条记录", "created": created, "errors": errors}


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
