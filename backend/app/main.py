from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS
from app.database import close_db, connect_db
from app.routers import (auth, inventory, issues, machines, materials,
                         operators, post_process, products, production,
                         purchases, reports, tool_purchase, users,
                         warehouse_entry)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()


app = FastAPI(
    title="机加工车间物料与生产管理系统",
    description="NKSerp - 物料出入库、生产成本核算、生产日报与质量统计分析",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ORIGINS] if CORS_ORIGINS != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(materials.router)
app.include_router(machines.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(purchases.router)
app.include_router(issues.router)
app.include_router(inventory.router)
app.include_router(production.router)
app.include_router(post_process.router)
app.include_router(reports.router)
app.include_router(operators.router)
app.include_router(tool_purchase.router)
app.include_router(warehouse_entry.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
