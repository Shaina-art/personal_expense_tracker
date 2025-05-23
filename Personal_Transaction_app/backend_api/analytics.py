from sqlalchemy.orm import Session
from models import Transaction, Analytics
from datetime import datetime
from typing import Literal

def analyze_period(
    db: Session,
    start: datetime,
    end: datetime,
    period: Literal["daily", "weekly", "monthly", "yearly"],
    bank_name: str
):
    transactions = db.query(Transaction).filter(Transaction.date >= start, Transaction.date <= end , Transaction.bank_name == bank_name).all()

    income = sum(t.amount for t in transactions if t.type == "credit")
    expense = sum(t.amount for t in transactions if t.type == "debit")
    net = income - expense
    status = "profit" if net >= 0 else "loss"

    summary = Analytics(
        period=period,
        start_date=start.date(),
        end_date=end.date(),
        total_income=income,
        total_expense=expense,
        net_balance=net,
        status=status,
        bank_name=bank_name
    )

    db.add(summary)
    db.commit()
    db.refresh(summary)
    return summary
