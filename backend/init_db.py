"""
数据库初始化脚本：创建索引、预置机器数据、默认管理员账号。
用法：python init_db.py
"""
import asyncio

from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext

MONGO_URI = "mongodb://localhost:27017/nkserp"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 16台预置机器
DEFAULT_MACHINES = [
    "走芯机1号", "走芯机2号", "走芯机3号", "走芯机4号",
    "走芯机5号", "走芯机6号", "走芯机7号", "走芯机8号",
    "走芯机9号", "走芯机10号", "走芯机11号", "走芯机12号",
    "马扎克", "兄弟1号", "兄弟2号", "兄弟3号",
]

# 默认管理员
DEFAULT_ADMIN = {
    "username": "admin",
    "real_name": "系统管理员",
    "shift": None,
    "role": "admin",
    "password": "admin123"
}


async def init():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client.get_database()

    # 创建索引
    await db.materials.create_index("material_spec", unique=True)
    await db.machines.create_index("machine_name", unique=True)
    await db.users.create_index("username", unique=True)
    await db.product_master.create_index([("product_code", 1), ("month", 1)], unique=True)
    await db.inventory_snapshot.create_index("material_spec", unique=True)
    await db.purchase_records.create_index("arrival_date")
    await db.issue_records.create_index("issue_date")
    await db.daily_production.create_index([("production_date", 1), ("machine", 1)])
    await db.post_process.create_index("registration_date")
    print("[OK] 索引已创建")

    # 预置机器
    for m in DEFAULT_MACHINES:
        await db.machines.update_one(
            {"machine_name": m},
            {"$setOnInsert": {"machine_name": m}},
            upsert=True
        )
    print(f"[OK] 已预置 {len(DEFAULT_MACHINES)} 台机器")

    # 默认管理员
    existing = await db.users.find_one({"username": DEFAULT_ADMIN["username"]})
    if not existing:
        await db.users.insert_one({
            "username": DEFAULT_ADMIN["username"],
            "real_name": DEFAULT_ADMIN["real_name"],
            "shift": DEFAULT_ADMIN["shift"],
            "role": DEFAULT_ADMIN["role"],
            "password_hash": pwd_context.hash(DEFAULT_ADMIN["password"])
        })
        print(f"[OK] 默认管理员已创建（admin / admin123）")
    else:
        print("[OK] 管理员账号已存在")

    # 示例操作工
    demo_operators = [
        ("zhangsan", "张三", "A班"),
        ("lisi", "李四", "A班"),
        ("wangwu", "王五", "B班"),
        ("zhaoliu", "赵六", "B班"),
    ]
    for username, real_name, shift in demo_operators:
        exists = await db.users.find_one({"username": username})
        if not exists:
            await db.users.insert_one({
                "username": username,
                "real_name": real_name,
                "shift": shift,
                "role": "operator",
                "password_hash": pwd_context.hash("123456")
            })
    print(f"[OK] 示例操作工已创建")

    client.close()
    print("[OK] 初始化完成")


if __name__ == "__main__":
    asyncio.run(init())
