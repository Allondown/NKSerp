from datetime import date, datetime

from pydantic import BaseModel


class SendEntry(BaseModel):
    send_date: date | None = None
    send_qty: int = 0


class WarehouseEntryCreate(BaseModel):
    entry_date: date          # 入仓日期
    product_code: str         # 产品编号
    product_name: str         # 产品名称
    entry_qty: int            # 入仓数量
    material_code: str = ""   # 物料编码


class PostProcessCreate(BaseModel):
    received_date: date
    product_code: str
    product_name: str
    received_qty: int  # 送入数量
    shift: str
    operator: str
    sends: list[SendEntry] = []  # 后工序完成送出记录（多次）
    remark: str = ""


class PurchaseCreate(BaseModel):
    arrival_date: date
    machine: str
    product: str
    product_code: str
    material_spec: str
    quantity_rods: float
    weight_kg: float
    unit_price: float
    remark: str = ""


class PurchaseResponse(PurchaseCreate):
    id: str
    total_price: float
    created_at: datetime


class IssueCreate(BaseModel):
    issue_date: date
    machine: str
    product_code: str
    material_spec: str
    issue_rods: float
    issue_weight_kg: float
    operator: str
    remark: str = ""


class IssueResponse(IssueCreate):
    id: str
    unit_cost: float
    total_cost: float
    created_at: datetime


class DailyProductionCreate(BaseModel):
    production_date: date
    machine: str
    product_name: str
    product_code: str
    material_spec: str
    cycle_sec: float
    work_time_sec: float
    good_qty: int
    actual_qty: int
    loss_time_min: int = 0
    shift: str
    operator: str
    plan_qty: int = 0
    remark: str = ""


class DailyCombinedCreate(BaseModel):
    """AB班合并录入。"""
    production_date: date
    machine: str
    product_name: str
    product_code: str
    material_spec: str
    cycle_sec: float = 0
    work_time_sec: float = 0  # 总生产时间（备选）
    a_cycle_sec: float = 0
    a_work_time_sec: float = 0
    b_cycle_sec: float = 0
    b_work_time_sec: float = 0
    plan_qty: int = 0
    loss_time_min: int = 0
    remark: str = ""
    a_actual_qty: int = 0
    a_good_qty: int = 0
    a_operator: str = ""
    a_loss_remark: str = ""
    b_actual_qty: int = 0
    b_good_qty: int = 0
    b_operator: str = ""
    b_loss_remark: str = ""


class ToolPurchaseCreate(BaseModel):
    name: str               # 品名
    spec: str               # 规格
    quantity: float         # 数量
    unit_price: float       # 单价（不含税）
    processed_product: str  # 加工产品
    supplier: str           # 供应商
    material_origin: str    # 原料产地
    order_date: date        # 下单日期
    quotation: str = ""     # 报价
    arrival_date: date | None = None  # 到货日期
    remark: str = ""


class LossRemarkUpdate(BaseModel):
    """内联编辑损失备注。"""
    production_date: str
    machine: str
    product_code: str
    shift: str
    loss_remark: str = ""


class DailyProductionResponse(DailyProductionCreate):
    id: str
    theoretical_qty: float
    bad_qty: int
    qualified_rate: float
    created_at: datetime
