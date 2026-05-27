"""
One-off migration: convert existing post_process documents from flat
send_date/send_qty fields to the new sends[] array format.

Usage:
  python backend/migrate_post_process_sends.py
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/nkserp")


async def migrate():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client.get_database()

    cursor = db.post_process.find({})
    count = 0
    async for doc in cursor:
        if "sends" in doc:
            continue

        send_qty = doc.get("send_qty", 0) or 0
        send_date = doc.get("send_date")

        sends = []
        if send_qty > 0 or send_date:
            sends.append({
                "send_date": send_date,
                "send_qty": send_qty,
            })

        await db.post_process.update_one(
            {"_id": doc["_id"]},
            {"$set": {"sends": sends}}
        )
        count += 1

    print(f"Migrated {count} documents.")
    client.close()


if __name__ == "__main__":
    asyncio.run(migrate())
