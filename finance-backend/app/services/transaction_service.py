from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, or_, extract
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionFilter
from app.core.roles import TransactionType
from app.core.exceptions import not_found_exception, bad_request_exception


class TransactionService:

    @staticmethod
    def _base_query():
        """Return a base query that excludes soft-deleted records."""
        return select(Transaction).where(Transaction.is_deleted == False)  # noqa: E712

    @staticmethod
    def get_by_id(db: Session, transaction_id: int) -> Transaction:
        tx = db.scalar(
            TransactionService._base_query().where(Transaction.id == transaction_id)
        )
        if not tx:
            raise not_found_exception("Transaction")
        return tx

    @staticmethod
    def list_transactions(
        db: Session, filters: TransactionFilter
    ) -> tuple[int, list[Transaction]]:
        query = TransactionService._base_query()

        # Filtering
        if filters.type:
            query = query.where(Transaction.type == filters.type)
        if filters.category:
            query = query.where(Transaction.category == filters.category)
        if filters.date_from:
            query = query.where(Transaction.date >= filters.date_from)
        if filters.date_to:
            query = query.where(Transaction.date <= filters.date_to)

        # Full-text search on category + description
        if filters.search:
            term = f"%{filters.search}%"
            query = query.where(
                or_(
                    Transaction.category.ilike(term),
                    Transaction.description.ilike(term),
                )
            )

        # Count before pagination
        count_query = select(func.count()).select_from(query.subquery())
        total = db.scalar(count_query)

        # Pagination (newest first): skip/limit overrides page/page_size when both set
        if filters.skip is not None and filters.limit is not None:
            offset = filters.skip
            lim = filters.limit
        else:
            offset = (filters.page - 1) * filters.page_size
            lim = filters.page_size
        query = query.order_by(Transaction.date.desc(), Transaction.id.desc())
        query = query.offset(offset).limit(lim)

        transactions = list(db.scalars(query).all())
        return total, transactions

    @staticmethod
    def create(db: Session, data: TransactionCreate, created_by: int) -> Transaction:
        tx = Transaction(
            amount=data.amount,
            type=data.type,
            category=data.category,
            date=data.date,
            description=data.description,
            created_by=created_by,
        )
        db.add(tx)
        db.commit()
        db.refresh(tx)
        return tx

    @staticmethod
    def update(db: Session, transaction_id: int, data: TransactionUpdate) -> Transaction:
        tx = TransactionService.get_by_id(db, transaction_id)
        update_data = (
            data.model_dump(exclude_unset=True)
            if hasattr(data, "model_dump")
            else data.dict(exclude_unset=True)
        )
        for field, value in update_data.items():
            setattr(tx, field, value)
        db.commit()
        db.refresh(tx)
        return tx

    @staticmethod
    def soft_delete(db: Session, transaction_id: int) -> None:
        tx = TransactionService.get_by_id(db, transaction_id)
        tx.is_deleted = True
        db.commit()

    # ── Dashboard aggregation ────────────────────────────────────────────────

    @staticmethod
    def get_summary(db: Session) -> dict:
        base = select(Transaction).where(Transaction.is_deleted == False)  # noqa: E712

        # Totals
        income_total = db.scalar(
            select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                Transaction.is_deleted == False,
                Transaction.type == TransactionType.INCOME,
            )
        ) or Decimal("0")

        expense_total = db.scalar(
            select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                Transaction.is_deleted == False,
                Transaction.type == TransactionType.EXPENSE,
            )
        ) or Decimal("0")

        total_count = db.scalar(
            select(func.count()).select_from(base.subquery())
        ) or 0

        # Category totals (income)
        income_by_cat = db.execute(
            select(Transaction.category, func.sum(Transaction.amount).label("total"))
            .where(Transaction.is_deleted == False, Transaction.type == TransactionType.INCOME)
            .group_by(Transaction.category)
            .order_by(func.sum(Transaction.amount).desc())
        ).all()

        # Category totals (expense)
        expense_by_cat = db.execute(
            select(Transaction.category, func.sum(Transaction.amount).label("total"))
            .where(Transaction.is_deleted == False, Transaction.type == TransactionType.EXPENSE)
            .group_by(Transaction.category)
            .order_by(func.sum(Transaction.amount).desc())
        ).all()

        # Monthly trends (last 12 months)
        monthly = db.execute(
            select(
                extract("year", Transaction.date).label("year"),
                extract("month", Transaction.date).label("month"),
                Transaction.type,
                func.sum(Transaction.amount).label("total"),
            )
            .where(Transaction.is_deleted == False)
            .group_by("year", "month", Transaction.type)
            .order_by("year", "month")
        ).all()

        # Reshape monthly data
        monthly_map: dict[tuple, dict] = {}
        for row in monthly:
            key = (int(row.year), int(row.month))
            if key not in monthly_map:
                monthly_map[key] = {"year": key[0], "month": key[1],
                                    "income": Decimal("0"), "expense": Decimal("0")}
            if row.type == TransactionType.INCOME:
                monthly_map[key]["income"] = row.total
            else:
                monthly_map[key]["expense"] = row.total

        monthly_trends = []
        for v in sorted(monthly_map.values(), key=lambda x: (x["year"], x["month"])):
            v["net"] = v["income"] - v["expense"]
            monthly_trends.append(v)

        # Recent 10 transactions
        recent = list(db.scalars(
            select(Transaction)
            .where(Transaction.is_deleted == False)
            .order_by(Transaction.date.desc(), Transaction.id.desc())
            .limit(10)
        ).all())

        net_balance = income_total - expense_total
        savings_rate = (
            (net_balance / income_total * Decimal("100"))
            if income_total > 0
            else Decimal("0")
        )

        return {
            "total_income": income_total,
            "total_expenses": expense_total,
            "net_balance": net_balance,
            "savings_rate": savings_rate,
            "total_transactions": total_count,
            "income_by_category": [{"category": r.category, "total": r.total} for r in income_by_cat],
            "expense_by_category": [{"category": r.category, "total": r.total} for r in expense_by_cat],
            "monthly_trends": monthly_trends,
            "recent_transactions": recent,
        }
