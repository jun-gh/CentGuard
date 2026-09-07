"""
Plain Python functions that do the actual work behind each MCP tool.
Kept separate from server.py so they're easy to unit test without spinning
up an MCP server.
"""
import statistics
from datetime import date, datetime, timedelta
from collections import defaultdict

from app.database import get_db_session
from app.models import Transaction


def _parse_month(month: str | None) -> tuple[date, date]:
    """
    month: 'YYYY-MM' string, or None for the current month.
    Returns (start_date, end_date) inclusive.
    """
    if month:
        year, mon = map(int, month.split("-"))
    else:
        today = date.today()
        year, mon = today.year, today.month

    start = date(year, mon, 1)
    if mon == 12:
        end = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end = date(year, mon + 1, 1) - timedelta(days=1)
    return start, end


def get_transactions(start_date: str, end_date: str, category: str | None = None) -> list[dict]:
    """Fetch raw transactions between two ISO dates, optionally filtered by category."""
    db = get_db_session()
    try:
        start = datetime.fromisoformat(start_date).date()
        end = datetime.fromisoformat(end_date).date()

        query = db.query(Transaction).filter(
            Transaction.date >= start, Transaction.date <= end
        )
        if category:
            query = query.filter(Transaction.category.ilike(category))

        results = query.order_by(Transaction.date.desc()).all()
        return [t.to_dict() for t in results]
    finally:
        db.close()


def get_spending_by_category(month: str | None = None) -> dict:
    """Sum of expenses grouped by category for a given month ('YYYY-MM') or the current month."""
    db = get_db_session()
    try:
        start, end = _parse_month(month)
        rows = (
            db.query(Transaction)
            .filter(Transaction.date >= start, Transaction.date <= end)
            .filter(Transaction.amount > 0)  # exclude income
            .all()
        )
        totals: dict[str, float] = defaultdict(float)
        for r in rows:
            totals[r.category] += r.amount

        return {
            "month": f"{start.year}-{start.month:02d}",
            "totals_by_category": {k: round(v, 2) for k, v in totals.items()},
            "total_spent": round(sum(totals.values()), 2),
        }
    finally:
        db.close()


def get_monthly_summary(month: str | None = None) -> dict:
    """Income vs. expenses vs. net savings for a given month."""
    db = get_db_session()
    try:
        start, end = _parse_month(month)
        rows = (
            db.query(Transaction)
            .filter(Transaction.date >= start, Transaction.date <= end)
            .all()
        )
        expenses = sum(r.amount for r in rows if r.amount > 0)
        income = sum(-r.amount for r in rows if r.amount < 0)

        return {
            "month": f"{start.year}-{start.month:02d}",
            "total_income": round(income, 2),
            "total_expenses": round(expenses, 2),
            "net_savings": round(income - expenses, 2),
            "transaction_count": len(rows),
        }
    finally:
        db.close()


def detect_anomalies(threshold_multiplier: float = 2.5, lookback_days: int = 90) -> list[dict]:
    """
    Flags transactions whose amount is unusually large relative to the
    median transaction amount *within their own category*. Simple, explainable
    statistics (median + multiplier) rather than a black-box model — easy to
    describe in an interview.
    """
    db = get_db_session()
    try:
        cutoff = date.today() - timedelta(days=lookback_days)
        rows = (
            db.query(Transaction)
            .filter(Transaction.date >= cutoff, Transaction.amount > 0)
            .all()
        )

        by_category: dict[str, list[Transaction]] = defaultdict(list)
        for r in rows:
            by_category[r.category].append(r)

        anomalies = []
        for category, txns in by_category.items():
            if len(txns) < 3:
                continue  # not enough data to judge what's "normal"
            amounts = [t.amount for t in txns]
            median = statistics.median(amounts)
            for t in txns:
                if t.amount > median * threshold_multiplier:
                    anomalies.append(
                        {
                            **t.to_dict(),
                            "category_median": round(median, 2),
                            "times_above_median": round(t.amount / median, 1),
                        }
                    )

        anomalies.sort(key=lambda a: a["times_above_median"], reverse=True)
        return anomalies
    finally:
        db.close()
