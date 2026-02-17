from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    phone: str = Field(index=True, unique=True)
    address: Optional[str] = None
    name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Purchase(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id")
    product_name: str
    amount: float
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    daily_return: Optional[float] = None
    status: Optional[str] = None
    extra: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
