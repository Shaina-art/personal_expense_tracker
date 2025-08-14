from sqlalchemy.orm import Session
from models import Transaction, Analytics
from datetime import datetime
from typing import Literal

def analyze_period(
    db: Session,
    start: datetime,
    end: datetime,
    period: Literal["daily", "weekly", "monthly", "yearly"],
    bank_name: str,
    user_id: int
):
    transactions = db.query(Transaction).filter(
        Transaction.date >= start,
        Transaction.date <= end,
        Transaction.bank_name == bank_name,
        Transaction.user_id == user_id
    ).all()

    income = sum(t.amount for t in transactions if t.type == "credit")
    expense = sum(t.amount for t in transactions if t.type == "debit")
    net = income - expense
    status = "profit" if net >= 0 else "loss"

    # 🧼 DELETE any existing analytics for same user + period + bank + dates
    db.query(Analytics).filter(
        Analytics.user_id == user_id,
        Analytics.period == period,
        Analytics.bank_name == bank_name,
        Analytics.start_date == start.date(),
        Analytics.end_date == end.date()
    ).delete()

    # ✅ Add new analytics summary
    summary = Analytics(
        period=period,
        start_date=start.date(),
        end_date=end.date(),
        total_income=income,
        total_expense=expense,
        net_balance=net,
        status=status,
        bank_name=bank_name,
        user_id=user_id
    )

    db.add(summary)
    db.commit()
    db.refresh(summary)
    return summary
