"""Analyst + Admin only routes (demonstrates role tiering alongside viewer-accessible dashboard)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.middleware.auth import require_role
from app.models.user import User
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/insights", tags=["Insights"])


@router.get("/snapshot")
def insights_snapshot(
    db: Session = Depends(get_db),
    _: User = Depends(require_role(["analyst", "admin"])),
):
    """
    [Analyst / Admin] High-level KPI snapshot (same aggregates as dashboard, stricter role gate).
    Viewers should use `GET /dashboard/summary` instead.
    """
    data = TransactionService.get_summary(db)
    return {
        "total_income": data["total_income"],
        "total_expenses": data["total_expenses"],
        "net_balance": data["net_balance"],
        "savings_rate": data["savings_rate"],
        "total_transactions": data["total_transactions"],
    }
