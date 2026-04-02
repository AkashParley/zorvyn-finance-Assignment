from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from app.db.session import get_db
from app.schemas.transaction import (
    TransactionCreate, TransactionUpdate,
    TransactionResponse, TransactionListResponse, TransactionFilter,
)
from app.services.transaction_service import TransactionService
from app.middleware.auth import require_role, get_active_user
from app.core.roles import TransactionType
from app.models.user import User

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("", response_model=TransactionListResponse)
def list_transactions(
    type: Optional[TransactionType] = Query(None),
    category: Optional[str] = Query(None, max_length=100),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    search: Optional[str] = Query(None, max_length=200),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    skip: Optional[int] = Query(None, ge=0, description="Offset (use with limit)"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="Page size when using skip/limit"),
    db: Session = Depends(get_db),
    _: User = Depends(require_role(["viewer", "analyst", "admin"])),
):
    """
    [Viewer / Analyst / Admin] List transactions with optional filters:
    - **type**: income | expense
    - **category**: exact match
    - **date_from / date_to**: date range
    - **search**: full-text over category + description
    - **page / page_size** or **skip / limit** for pagination
    """
    filters = TransactionFilter(
        type=type, category=category,
        date_from=date_from, date_to=date_to,
        search=search, page=page, page_size=page_size,
        skip=skip, limit=limit,
    )
    total, transactions = TransactionService.list_transactions(db, filters)
    return TransactionListResponse(
        total=total, page=page, page_size=page_size, transactions=transactions
    )


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(["viewer", "analyst", "admin"])),
):
    """[Viewer / Analyst / Admin] Get a single transaction by ID."""
    return TransactionService.get_by_id(db, transaction_id)


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"])),
):
    """[Admin] Create a new financial record."""
    return TransactionService.create(db, data, created_by=current_user.id)


@router.patch("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    data: TransactionUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(["admin"])),
):
    """[Admin] Update an existing financial record."""
    return TransactionService.update(db, transaction_id, data)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(["admin"])),
):
    """[Admin] Soft-delete a transaction (record is hidden, not permanently removed)."""
    TransactionService.soft_delete(db, transaction_id)
