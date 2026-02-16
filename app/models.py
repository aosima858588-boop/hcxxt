from typing import Optional
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel, Column, JSON


class Dataset(SQLModel, table=True):
    """Dataset model representing an uploaded CSV file"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    columns: list = Field(sa_column=Column(JSON))
    row_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Record(SQLModel, table=True):
    """Record model representing a row from a dataset"""
    id: Optional[int] = Field(default=None, primary_key=True)
    dataset_id: int = Field(foreign_key="dataset.id", index=True)
    data: dict = Field(sa_column=Column(JSON))
