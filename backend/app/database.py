from motor.motor_asyncio import AsyncIOMotorClient

from app.config import MONGO_URI

client: AsyncIOMotorClient | None = None
db = None


async def connect_db():
    global client, db
    client = AsyncIOMotorClient(MONGO_URI)
    db = client.get_database()
    # 预热连接池，避免首次请求阻塞
    await client.admin.command("ping")
    await _ensure_indexes()


async def close_db():
    global client
    if client:
        client.close()


def get_db():
    return db


async def _ensure_indexes():
    # 并行创建所有索引
    import asyncio
    await asyncio.gather(
        db.materials.create_index("material_spec", unique=True),
        db.machines.create_index("machine_name", unique=True),
        db.users.create_index("username", unique=True),
        db.product_master.create_index([("product_code", 1), ("month", 1)], unique=True),
        db.inventory_snapshot.create_index("material_spec", unique=True),
        db.purchase_records.create_index("arrival_date"),
        db.issue_records.create_index("issue_date"),
        db.daily_production.create_index([("production_date", 1), ("machine", 1)]),
        db.post_process.create_index("received_date"),
        db.operators.create_index("name", unique=True),
        db.tool_purchases.create_index("order_date"),
        db.warehouse_entry.create_index("entry_date"),
    )
