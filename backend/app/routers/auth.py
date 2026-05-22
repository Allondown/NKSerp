from fastapi import APIRouter, Depends, HTTPException

from app.database import get_db
from app.middleware import (create_access_token, get_current_user,
                            hash_password, verify_password)
from app.schemas.auth import LoginRequest, TokenResponse, UserInfo
from app.schemas.basic import UserCreate, UserResponse

router = APIRouter(prefix="/api/v1/auth", tags=["认证"])


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest):
    db = get_db()
    user = await db.users.find_one({"username": req.username})
    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = create_access_token({"sub": user["username"], "role": user["role"]})
    return TokenResponse(
        access_token=token, username=user["username"],
        role=user["role"], real_name=user["real_name"]
    )


@router.get("/me", response_model=UserInfo)
async def me(current=Depends(get_current_user)):
    db = get_db()
    user = await db.users.find_one({"username": current["username"]})
    return UserInfo(
        username=user["username"], real_name=user["real_name"],
        shift=user.get("shift"), role=user["role"]
    )


@router.post("/register")
async def register(req: UserCreate):
    db = get_db()
    exists = await db.users.find_one({"username": req.username})
    if exists:
        raise HTTPException(status_code=400, detail="用户名已存在")
    await db.users.insert_one({
        "username": req.username,
        "real_name": req.real_name,
        "shift": req.shift,
        "role": req.role,
        "password_hash": hash_password(req.password)
    })
    return {"message": "ok"}
