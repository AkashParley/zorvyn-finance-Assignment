from decimal import Decimal
from typing import Optional
from pydantic import BaseModel


# ── Auth ─────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── Dashboard ────────────────────────────────────────────────────────────────

class CategoryTotal(BaseModel):
    category: str
    total: Decimal


class MonthlyTrend(BaseModel):
    year: int
    month: int
    income: Decimal
    expense: Decimal
    net: Decimal


class DashboardSummary(BaseModel):
    total_income: Decimal
    total_expenses: Decimal
    net_balance: Decimal
    savings_rate: Decimal
    total_transactions: int
    income_by_category: list[CategoryTotal]
    expense_by_category: list[CategoryTotal]
    monthly_trends: list[MonthlyTrend]
    recent_transactions: list  # filled at runtime with TransactionResponse
