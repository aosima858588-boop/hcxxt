from typing import List, Optional
from pydantic import BaseModel

class ProductOut(BaseModel):
    name: str
    amount: float
    start: Optional[str]
    end: Optional[str]
    daily_return: Optional[float]
    status: Optional[str]
    extra: Optional[float]

class UserOut(BaseModel):
    phone: str
    address: Optional[str]
    product_count: int
    total_subscribed: float
    total_refunded: float = 0.0
    due_not_refunded: float
    not_due_total: float
    products: List[ProductOut]
