from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.common import DashboardSummary
from app.schemas.transaction import TransactionResponse
from app.services.transaction_service import TransactionService
from app.middleware.auth import require_role
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    _: User = Depends(require_role(["viewer", "analyst", "admin"])),
):
    """
    [Viewer / Analyst / Admin] Returns aggregated dashboard data:
    - Total income, expenses, net balance
    - Category-wise breakdowns
    - Monthly trends
    - 10 most recent transactions
    """
    data = TransactionService.get_summary(db)
    # Pydantic v2: model_validate | v1: from_orm
    _to_tx = (
        TransactionResponse.model_validate
        if hasattr(TransactionResponse, "model_validate")
        else TransactionResponse.from_orm
    )
    data["recent_transactions"] = [_to_tx(t) for t in data["recent_transactions"]]
    return DashboardSummary(**data)
