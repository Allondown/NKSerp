from datetime import datetime

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.database import get_db
from app.middleware import require_role
from app.schemas.business import PostProcessCreate, PostProcessSendUpdate

router = APIRouter(prefix="/api/v1/post-process", tags=["后工序管理"])


@router.post("")
async def create_record(data: PostProcessCreate,
                        current=Depends(require_role("admin", "workshop"))):
    db = get_db()
    record = {
        **data.model_dump(),
        "received_date": datetime.combine(data.received_date, datetime.min.time()),
        "send_date": datetime.combine(data.send_date, datetime.min.time()) if data.send_date else None,
        "created_at": datetime.utcnow()
    }
    result = await db.post_process.insert_one(record)
    return {"message": "ok", "id": str(result.inserted_id)}


@router.get("")
async def list_records(start_date: str | None = None,
                       end_date: str | None = None,
                       product_code: str | None = None,
                       page: int = 1, page_size: int = 100,
                       current=Depends(require_role("admin", "workshop", "warehouse", "viewer"))):
    db = get_db()
    q = {}
    if start_date or end_date:
        q["received_date"] = {}
        if start_date:
            q["received_date"]["$gte"] = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            q["received_date"]["$lte"] = datetime.strptime(end_date, "%Y-%m-%d")
    if product_code:
        q["product_code"] = {"$regex": product_code, "$options": "i"}

    cursor = db.post_process.find(q).sort("received_date", -1)
    total = await db.post_process.count_documents(q)
    records = await cursor.skip((page - 1) * page_size).limit(page_size).to_list(length=page_size)
    for r in records:
        r["id"] = str(r.pop("_id"))
    return {"total": total, "items": records, "page": page, "page_size": page_size}


@router.put("/{record_id}")
async def update_record(record_id: str, data: PostProcessCreate,
                        current=Depends(require_role("admin", "workshop"))):
    db = get_db()
    update_data = {
        **data.model_dump(),
        "received_date": datetime.combine(data.received_date, datetime.min.time()),
    }
    if data.send_date:
        update_data["send_date"] = datetime.combine(data.send_date, datetime.min.time())
    else:
        update_data["send_date"] = None

    result = await db.post_process.update_one(
        {"_id": ObjectId(record_id)},
        {"$set": update_data}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="未找到该记录")
    return {"message": "ok"}


@router.put("/{record_id}/send")
async def update_send(record_id: str, data: PostProcessSendUpdate,
                      current=Depends(require_role("admin", "workshop"))):
    db = get_db()
    record = await db.post_process.find_one({"_id": ObjectId(record_id)})
    if not record:
        raise HTTPException(status_code=404, detail="未找到该记录")

    update = {"send_qty": data.send_qty}
    if data.send_date:
        update["send_date"] = datetime.strptime(data.send_date, "%Y-%m-%d")

    result = await db.post_process.update_one(
        {"_id": ObjectId(record_id)},
        {"$set": update}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="更新失败")
    return {"message": "ok"}


@router.get("/export")
async def export_records(start_date: str | None = None,
                          end_date: str | None = None,
                          product_code: str | None = None,
                          current=Depends(require_role("admin", "workshop", "warehouse", "viewer"))):
    """导出后工序登记记录为 Excel。"""
    from io import BytesIO
    import openpyxl
    from openpyxl.utils import get_column_letter

    db = get_db()
    q = {}
    if start_date or end_date:
        q["received_date"] = {}
        if start_date:
            q["received_date"]["$gte"] = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            q["received_date"]["$lte"] = datetime.strptime(end_date, "%Y-%m-%d")
    if product_code:
        q["product_code"] = {"$regex": product_code, "$options": "i"}

    records = await db.post_process.find(q).sort("received_date", -1).to_list(length=10000)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "后工序登记"
    headers = ["机加送入日期", "产品编号", "产品名称", "送入数量",
                "操作员", "班组", "后工序完成送出日期", "送出数量", "未完成数量"]
    ws.append(headers)

    for r in records:
        received = r.get("received_qty", 0) or 0
        send = r.get("send_qty", 0) or 0
        ws.append([
            r.get("received_date").strftime("%Y-%m-%d") if r.get("received_date") else "",
            r.get("product_code", ""),
            r.get("product_name", ""),
            received,
            r.get("operator", ""),
            r.get("shift", ""),
            r.get("send_date").strftime("%Y-%m-%d") if r.get("send_date") else "",
            send,
            max(received - send, 0),
        ])

    for col in range(1, len(headers) + 1):
        ws.column_dimensions[get_column_letter(col)].width = 18

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=post_process.xlsx"}
    )


@router.delete("/{record_id}")
async def delete_record(record_id: str,
                        current=Depends(require_role("admin"))):
    db = get_db()
    result = await db.post_process.delete_one({"_id": ObjectId(record_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="未找到该记录")
    return {"message": "ok"}
