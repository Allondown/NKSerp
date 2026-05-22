from datetime import date, datetime

from pydantic import BaseModel


class PostProcessSendUpdate(BaseModel):
    """后工序内联更新送出日期/数量。"""
    send_qty: int = 0
    send_date: str | None = None


class PostProcessCreate(BaseModel):
    received_date: date
    product_code: str
    product_name: str
    received_qty: int  # 送入数量
    shift: str
    operator: str
    send_date: date | None = None  # 后工序完成送出日期
    send_qty: int = 0  # 送出数量
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
