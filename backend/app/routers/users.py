from fastapi import APIRouter, Depends, HTTPException

from app.database import get_db
from app.middleware import hash_password, require_role
from app.schemas.basic import UserCreate, UserResponse

router = APIRouter(prefix="/api/v1/users", tags=["用户管理"])


@router.get("", response_model=list[UserResponse])
async def list_users(shift: str | None = None,
                     current=Depends(require_role("admin", "viewer"))):
    db = get_db()
    q = {}
    if shift:
        q["shift"] = shift
    cursor = db.users.find(q, {"password_hash": 0}).sort("real_name", 1)
    return await cursor.to_list(length=200)


@router.post("")
async def create_user(data: UserCreate,
                      current=Depends(require_role("admin"))):
    db = get_db()
    exists = await db.users.find_one({"username": data.username})
    if exists:
        raise HTTPException(status_code=400, detail="用户名已存在")
    await db.users.insert_one({
        "username": data.username,
        "real_name": data.real_name,
        "shift": data.shift,
        "role": data.role,
        "password_hash": hash_password(data.password)
    })
    return {"message": "ok"}


@router.put("/{username}")
async def update_user(username: str, data: UserCreate,
                      current=Depends(require_role("admin"))):
    db = get_db()
    update_data = {
        "real_name": data.real_name,
        "shift": data.shift,
        "role": data.role,
    }
    result = await db.users.update_one(
        {"username": username},
        {"$set": update_data}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="未找到该用户")
    return {"message": "ok"}


@router.delete("/{username}")
async def delete_user(username: str,
                      current=Depends(require_role("admin"))):
    db = get_db()
    result = await db.users.delete_one({"username": username})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="未找到该用户")
    return {"message": "ok"}


@router.put("/{username}/password")
async def change_password(username: str, password: str,
                          current=Depends(require_role("admin"))):
    """管理账户修改指定用户的登录密码。"""
    db = get_db()
    result = await db.users.update_one(
        {"username": username},
        {"$set": {"password_hash": hash_password(password)}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="未找到该用户")
    return {"message": "ok"}
