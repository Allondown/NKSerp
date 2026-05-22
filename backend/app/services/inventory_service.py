from app.database import get_db


async def update_inventory_after_purchase(material_spec: str, weight_kg: float,
                                          total_price: float):
    """采购入库后更新库存（移动加权平均）。"""
    db = get_db()
    inv = await db.inventory_snapshot.find_one({"material_spec": material_spec})

    if inv:
        new_qty = inv["total_qty_kg"] + weight_kg
        new_amount = inv["total_amount"] + total_price
        new_avg = new_amount / new_qty if new_qty else 0
        await db.inventory_snapshot.update_one(
            {"material_spec": material_spec},
            {"$set": {
                "total_qty_kg": new_qty,
                "total_amount": new_amount,
                "avg_price": new_avg,
                "last_updated": __import__("datetime").datetime.utcnow()
            }}
        )
    else:
        await db.inventory_snapshot.insert_one({
            "material_spec": material_spec,
            "total_qty_kg": weight_kg,
            "total_amount": total_price,
            "avg_price": total_price / weight_kg if weight_kg else 0,
            "last_updated": __import__("datetime").datetime.utcnow()
        })


async def update_inventory_after_issue(material_spec: str, issue_weight_kg: float) -> float:
    """领用出库：扣减库存，返回本次领用成本。"""
    db = get_db()
    inv = await db.inventory_snapshot.find_one({"material_spec": material_spec})
    if not inv:
        raise ValueError(f"材料 {material_spec} 无库存记录")

    if inv["total_qty_kg"] < issue_weight_kg:
        raise ValueError(f"库存不足：当前 {material_spec} 库存 {inv['total_qty_kg']:.2f}kg，"
                         f"需领用 {issue_weight_kg:.2f}kg")

    avg_price = inv["avg_price"]
    total_cost = issue_weight_kg * avg_price
    new_qty = inv["total_qty_kg"] - issue_weight_kg
    new_amount = inv["total_amount"] - total_cost
    new_avg = new_amount / new_qty if new_qty else 0

    result = await db.inventory_snapshot.update_one(
        {"material_spec": material_spec, "total_qty_kg": {"$gte": issue_weight_kg}},
        {"$set": {
            "total_qty_kg": new_qty,
            "total_amount": new_amount,
            "avg_price": new_avg,
            "last_updated": __import__("datetime").datetime.utcnow()
        }}
    )
    if result.modified_count == 0:
        raise ValueError(f"库存不足或并发冲突，材料：{material_spec}")

    return total_cost


async def reverse_inventory_after_purchase(material_spec: str, weight_kg: float,
                                            total_price: float):
    """删除采购记录后回滚库存。"""
    db = get_db()
    inv = await db.inventory_snapshot.find_one({"material_spec": material_spec})
    if not inv:
        return
    new_qty = max(0, inv["total_qty_kg"] - weight_kg)
    new_amount = max(0, inv["total_amount"] - total_price)
    new_avg = new_amount / new_qty if new_qty else 0
    await db.inventory_snapshot.update_one(
        {"material_spec": material_spec},
        {"$set": {
            "total_qty_kg": new_qty,
            "total_amount": new_amount,
            "avg_price": new_avg,
            "last_updated": __import__("datetime").datetime.utcnow()
        }}
    )


async def reverse_inventory_after_issue(material_spec: str, issue_weight_kg: float,
                                         total_cost: float):
    """删除领用记录后回滚库存。"""
    db = get_db()
    inv = await db.inventory_snapshot.find_one({"material_spec": material_spec})
    if not inv:
        return
    new_qty = inv["total_qty_kg"] + issue_weight_kg
    new_amount = inv["total_amount"] + total_cost
    new_avg = new_amount / new_qty if new_qty else 0
    await db.inventory_snapshot.update_one(
        {"material_spec": material_spec},
        {"$set": {
            "total_qty_kg": new_qty,
            "total_amount": new_amount,
            "avg_price": new_avg,
            "last_updated": __import__("datetime").datetime.utcnow()
        }}
    )


async def get_current_inventory(material_spec: str | None = None) -> list:
    """查询当前库存。"""
    db = get_db()
    if material_spec:
        inv = await db.inventory_snapshot.find_one({"material_spec": material_spec})
        return [inv] if inv else []
    cursor = db.inventory_snapshot.find()
    return await cursor.to_list(length=1000)
