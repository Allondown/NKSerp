from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.database import get_db
from app.middleware import require_role

router = APIRouter(prefix="/api/v1/reports", tags=["统计报表"])


@router.get("/cost")
async def report_cost(year: int, month: int,
                      current=Depends(require_role("admin", "workshop", "warehouse", "viewer"))):
    """月度成本报表：按材料规格统计期初/采购/领用/期末。"""
    db = get_db()
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)

    # 本月采购聚合
    purchase_pipeline = [
        {"$match": {"arrival_date": {"$gte": start_date, "$lt": end_date}}},
        {"$group": {
            "_id": "$material_spec",
            "purchase_qty": {"$sum": "$weight_kg"},
            "purchase_amount": {"$sum": "$total_price"}
        }}
    ]
    purchases = await db.purchase_records.aggregate(purchase_pipeline).to_list(length=500)

    # 本月领用聚合
    issue_pipeline = [
        {"$match": {"issue_date": {"$gte": start_date, "$lt": end_date}}},
        {"$group": {
            "_id": "$material_spec",
            "issue_qty": {"$sum": "$issue_weight_kg"},
            "issue_cost": {"$sum": "$total_cost"}
        }}
    ]
    issues = await db.issue_records.aggregate(issue_pipeline).to_list(length=500)

    p_map = {p["_id"]: p for p in purchases}
    i_map = {i["_id"]: i for i in issues}

    # 所有有活动的材料 + 有库存的材料
    specs = set(list(p_map.keys()) + list(i_map.keys()))
    inventory_items = await db.inventory_snapshot.find().to_list(length=500)
    for inv in inventory_items:
        specs.add(inv["material_spec"])

    details = []
    total_purchase_amount = 0
    total_issue_cost = 0
    total_inventory_amount = 0

    for spec in sorted(specs):
        p = p_map.get(spec, {})
        i = i_map.get(spec, {})
        inv = next((x for x in inventory_items if x["material_spec"] == spec), None)

        purchase_qty = p.get("purchase_qty", 0) or 0
        purchase_amount = p.get("purchase_amount", 0) or 0
        issue_qty = i.get("issue_qty", 0) or 0
        issue_cost = i.get("issue_cost", 0) or 0
        end_qty = inv["total_qty_kg"] if inv else 0
        end_amount = inv["total_amount"] if inv else 0
        begin_qty = end_qty + issue_qty - purchase_qty
        begin_amount = end_amount + issue_cost - purchase_amount

        total_purchase_amount += purchase_amount
        total_issue_cost += issue_cost
        total_inventory_amount += end_amount

        details.append({
            "material_spec": spec,
            "begin_qty": round(begin_qty, 2), "begin_amount": round(begin_amount, 2),
            "purchase_qty": round(purchase_qty, 2), "purchase_amount": round(purchase_amount, 2),
            "issue_qty": round(issue_qty, 2), "issue_cost": round(issue_cost, 2),
            "end_qty": round(end_qty, 2), "end_amount": round(end_amount, 2),
        })

    return {
        "year": year, "month": month,
        "details": details,
        "summary": {
            "total_purchase_amount": round(total_purchase_amount, 2),
            "total_issue_cost": round(total_issue_cost, 2),
            "total_inventory_amount": round(total_inventory_amount, 2),
        }
    }


@router.get("/product-achieve")
async def report_product_achieve(year: int, month: int,
                                 current=Depends(require_role("admin", "workshop", "warehouse", "viewer"))):
    """产品质量达成率报表：按产品+机器+班组。"""
    db = get_db()
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)

    pipeline = [
        {"$match": {"production_date": {"$gte": start_date, "$lt": end_date}}},
        {"$group": {
            "_id": {"product": "$product_name", "machine": "$machine"},
            "theoretical_qty": {"$sum": "$theoretical_qty"},
            "actual_qty": {"$sum": "$actual_qty"},
            "good_qty": {"$sum": "$good_qty"},
            "avg_qualified_rate": {"$avg": "$qualified_rate"},
        }},
        {"$sort": {"_id.product": 1, "_id.machine": 1}}
    ]
    rows = await db.daily_production.aggregate(pipeline).to_list(length=1000)

    result = []
    for r in rows:
        g = r["_id"]
        theo = r["theoretical_qty"] or 0
        actual = r["actual_qty"] or 0
        good = r["good_qty"] or 0
        result.append({
            "product": g["product"],
            "machine": g["machine"],
            "theoretical_qty": round(theo * 2, 2),  # AB两班分别理论产量合计
            "actual_qty": actual,
            "good_qty": good,
            "bad_qty": max(actual - good, 0),
            "achieve_rate": round(actual / (theo * 2), 4) if theo > 0 else 0,
            "qualified_rate": round(r.get("avg_qualified_rate", 0), 4),
        })
    return result


@router.get("/team-achieve")
async def report_team_achieve(year: int, month: int,
                              current=Depends(require_role("admin", "workshop", "warehouse", "viewer"))):
    """班组达成率汇总。"""
    db = get_db()
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)

    pipeline = [
        {"$match": {"production_date": {"$gte": start_date, "$lt": end_date}}},
        {"$group": {
            "_id": "$shift",
            "theoretical_qty": {"$sum": "$theoretical_qty"},
            "actual_qty": {"$sum": "$actual_qty"},
            "good_qty": {"$sum": "$good_qty"},
            "avg_qualified_rate": {"$avg": "$qualified_rate"},
        }}
    ]
    rows = await db.daily_production.aggregate(pipeline).to_list(length=10)
    result = []
    for r in rows:
        theo = r["theoretical_qty"] or 0
        actual = r["actual_qty"] or 0
        good = r["good_qty"] or 0
        result.append({
            "shift": r["_id"],
            "theoretical_qty": round(theo * 2, 2),
            "actual_qty": actual,
            "good_qty": good,
            "achieve_rate": round(actual / (theo * 2), 4) if theo > 0 else 0,
            "qualified_rate": round(r.get("avg_qualified_rate", 0), 4),
        })
    return result


@router.get("/employee")
async def report_employee(year: int, month: int,
                          current=Depends(require_role("admin", "workshop", "warehouse", "viewer"))):
    """员工绩效报表。"""
    db = get_db()
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)

    pipeline = [
        {"$match": {"production_date": {"$gte": start_date, "$lt": end_date}}},
        {"$group": {
            "_id": {"operator": "$operator", "product": "$product_name"},
            "theoretical_qty": {"$sum": "$theoretical_qty"},
            "actual_qty": {"$sum": "$actual_qty"},
            "good_qty": {"$sum": "$good_qty"},
            "avg_qualified_rate": {"$avg": "$qualified_rate"},
        }},
        {"$sort": {"_id.operator": 1}}
    ]
    rows = await db.daily_production.aggregate(pipeline).to_list(length=1000)

    result = []
    for r in rows:
        g = r["_id"]
        theo = r["theoretical_qty"] or 0
        actual = r["actual_qty"] or 0
        good = r["good_qty"] or 0
        result.append({
            "operator": g["operator"],
            "product": g["product"],
            "theoretical_qty": round(theo * 2, 2),
            "actual_qty": actual,
            "good_qty": good,
            "achieve_rate": round(actual / (theo * 2), 4) if theo > 0 else 0,
            "qualified_rate": round(r.get("avg_qualified_rate", 0), 4),
        })
    return result


@router.get("/progress")
async def report_progress(year: int, month: int,
                          product_code: str | None = None,
                          current=Depends(require_role("admin", "workshop", "warehouse", "viewer"))):
    """后工序完成进度报表：按产品+班组汇总送出数量。"""
    db = get_db()
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)

    match_filter = {"received_date": {"$gte": start_date, "$lt": end_date}}
    if product_code:
        match_filter["product_code"] = {"$regex": product_code, "$options": "i"}

    pipeline = [
        {"$match": match_filter},
        {"$group": {
            "_id": {"product_code": "$product_code", "product_name": "$product_name"},
            "a_send": {"$sum": {"$cond": [{"$eq": ["$shift", "A班"]}, "$send_qty", 0]}},
            "b_send": {"$sum": {"$cond": [{"$eq": ["$shift", "B班"]}, "$send_qty", 0]}},
            "total_received": {"$sum": "$received_qty"},
        }},
        {"$sort": {"_id.product_code": 1}}
    ]
    rows = await db.post_process.aggregate(pipeline).to_list(length=500)

    result = []
    for r in rows:
        g = r["_id"]
        a = r["a_send"] or 0
        b = r["b_send"] or 0
        received = r["total_received"] or 0
        uncompleted = max(received - (a + b), 0)
        result.append({
            "product_code": g["product_code"],
            "product_name": g["product_name"],
            "a_total": a,
            "b_total": b,
            "ab_total": a + b,
            "uncompleted": uncompleted,
        })
    return result


@router.get("/export/excel")
async def export_excel(report_type: str, year: int, month: int,
                       product_code: str | None = None,
                       current=Depends(require_role("admin", "workshop", "warehouse", "viewer"))):
    """导出报表为 Excel。"""
    from io import BytesIO
    import openpyxl
    from openpyxl.utils import get_column_letter

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"{report_type}-{year}-{month}"

    if report_type == "cost":
        data = await report_cost(year, month)
        headers = ["材料规格", "期初数量", "期初金额", "采购数量", "采购金额",
                    "领用数量", "领用成本", "期末数量", "期末金额"]
        ws.append(headers)
        for d in data["details"]:
            ws.append([d["material_spec"], d["begin_qty"], d["begin_amount"],
                       d["purchase_qty"], d["purchase_amount"],
                       d["issue_qty"], d["issue_cost"],
                       d["end_qty"], d["end_amount"]])
        ws.append([])
        s = data["summary"]
        ws.append(["合计", "", "", "", s["total_purchase_amount"],
                    "", s["total_issue_cost"], "", s["total_inventory_amount"]])
    elif report_type == "product-achieve":
        data = await report_product_achieve(year, month)
        headers = ["产品", "机器", "理论产量", "实绩数量", "良品数量",
                    "不良数量", "达成率", "合格率"]
        ws.append(headers)
        for d in data:
            ws.append([d["product"], d["machine"],
                       d["theoretical_qty"], d["actual_qty"], d["good_qty"],
                       d["bad_qty"], d["achieve_rate"], d["qualified_rate"]])
    elif report_type == "team-achieve":
        data = await report_team_achieve(year, month)
        headers = ["班组", "理论产量", "实绩数量", "良品数量", "达成率", "合格率"]
        ws.append(headers)
        for d in data:
            ws.append([d["shift"], d["theoretical_qty"], d["actual_qty"],
                       d["good_qty"], d["achieve_rate"], d["qualified_rate"]])
    elif report_type == "employee":
        data = await report_employee(year, month)
        headers = ["操作工", "产品", "理论产量", "实绩数量", "良品数量", "达成率", "合格率"]
        ws.append(headers)
        for d in data:
            ws.append([d["operator"], d["product"], d["theoretical_qty"],
                       d["actual_qty"], d["good_qty"],
                       d["achieve_rate"], d["qualified_rate"]])
    elif report_type == "progress":
        data = await report_progress(year, month, product_code)
        headers = ["产品编号", "产品名称", "A班总数", "B班总数", "AB班完成总数", "未完成总数"]
        ws.append(headers)
        for d in data:
            ws.append([d["product_code"], d["product_name"],
                       d["a_total"], d["b_total"], d["ab_total"], d["uncompleted"]])

    for col in range(1, len(headers) + 1):
        ws.column_dimensions[get_column_letter(col)].width = 16

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    filename = f"{report_type}_{year}_{month}.xlsx"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
