from pydantic import BaseModel


class MaterialCreate(BaseModel):
    material_spec: str
    unit: str = "kg"
    standard_price: float = 0


class MaterialResponse(MaterialCreate):
    pass


class MachineCreate(BaseModel):
    machine_name: str


class MachineResponse(MachineCreate):
    pass


class UserCreate(BaseModel):
    username: str
    real_name: str
    password: str = "123456"
    shift: str | None = None
    role: str = "operator"


class UserResponse(BaseModel):
    username: str
    real_name: str
    shift: str | None = None
    role: str


class ProductCreate(BaseModel):
    product_code: str
    product_name: str
    material_spec: str
    monthly_plan: int = 0
    cycle_sec: float = 0
    work_time_sec: float = 0
    loss_remark: str = ""
    month: str


class ProductResponse(ProductCreate):
    pass
