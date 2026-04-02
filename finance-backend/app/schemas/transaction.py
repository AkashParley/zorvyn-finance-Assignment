from datetime import date, datetime
from decimal import Decimal
from typing import Optional
try:
    # Pydantic v2
    from pydantic import BaseModel, Field, field_validator

    _PYDANTIC_V2 = True
except ImportError:
    # Pydantic v1 fallback
    from pydantic import BaseModel, Field, validator

    _PYDANTIC_V2 = False
from app.core.roles import TransactionType


# ── Request schemas ──────────────────────────────────────────────────────────

class TransactionCreate(BaseModel):
    amount: Decimal = Field(..., gt=0, decimal_places=2, description="Must be a positive value.")
    type: TransactionType
    category: str = Field(..., min_length=1, max_length=100)
    date: date
    description: Optional[str] = Field(None, max_length=500)


class TransactionUpdate(BaseModel):
    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    type: Optional[TransactionType] = None
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    date: Optional[date] = None
    description: Optional[str] = Field(None, max_length=500)


# ── Filter / Search schema ───────────────────────────────────────────────────

class TransactionFilter(BaseModel):
    type: Optional[TransactionType] = None
    category: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    search: Optional[str] = Field(None, description="Full-text search on category and description.")
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    # Optional offset pagination (alternative to page/page_size)
    skip: Optional[int] = Field(None, ge=0)
    limit: Optional[int] = Field(None, ge=1, le=100)

    if _PYDANTIC_V2:

        @field_validator("date_to")
        @classmethod
        def date_range_valid(cls, v: Optional[date], info) -> Optional[date]:
            date_from = info.data.get("date_from")
            if v and date_from and v < date_from:
                raise ValueError("date_to must be >= date_from.")
            return v
    else:

        @validator("date_to")
        def date_range_valid(cls, v: Optional[date], values) -> Optional[date]:
            date_from = values.get("date_from")
            if v and date_from and v < date_from:
                raise ValueError("date_to must be >= date_from.")
            return v


# ── Response schemas ─────────────────────────────────────────────────────────

class TransactionResponse(BaseModel):
    id: int
    amount: Decimal
    type: TransactionType
    category: str
    date: date
    description: Optional[str]
    created_by: int
    created_at: datetime
    updated_at: datetime

    if _PYDANTIC_V2:
        model_config = {"from_attributes": True}
    else:

        class Config:
            orm_mode = True


class TransactionListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    transactions: list[TransactionResponse]
