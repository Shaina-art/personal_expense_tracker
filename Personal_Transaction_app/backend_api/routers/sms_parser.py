from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Transaction
from bank_detector import detect_bank
from datetime import datetime
from settings import check_spending_alerts

import re
from collections import defaultdict

router = APIRouter()

@router.post("/sms/parse")
def parse_sms(
    sender: str,
    message: str,
    db: Session = Depends(get_db)
):
    bank_name = detect_bank(sender)

    # Parse SMS message 
    match = re.search(r'(credited|debited).+?INR\s*([\d,]+\.\d+).*?on\s+(\d{2}-\d{2}-\d{4})', message, re.IGNORECASE)
    if not match:
        return {"error": "Could not parse SMS"}

    txn_type = "credit" if "credit" in match.group(1).lower() else "debit"
    amount = float(match.group(2).replace(",", ""))
    txn_date = datetime.strptime(match.group(3), "%d-%m-%Y")

    # Save transaction
    transaction = Transaction(
        amount=amount,
        type=txn_type,
        description=message[:100],
        bank_name=bank_name,
        date=txn_date
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    # 🔍 Get total balance and spending by category (simple version)
    transactions = db.query(Transaction).filter(Transaction.bank_name == bank_name).all()
    
    spending_by_category = defaultdict(float)
    current_balance = 0.0

    for txn in transactions:
        if txn.type == "credit":
            current_balance += txn.amount
        elif txn.type == "debit":
            current_balance -= txn.amount
            spending_by_category[txn.category or "Others"] += txn.amount

    spending_by_category["balance"] = current_balance

    # ✅ Check for alerts
    alerts = check_spending_alerts(spending_by_category, db)

    return {
        "status": "saved",
        "transaction_id": transaction.id,
        "alerts": alerts
    }
