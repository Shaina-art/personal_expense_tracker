from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Transaction, User, BankAlias
from bank_detector import detect_bank_name
from datetime import datetime
from routers.settings import check_spending_alerts
from routers.user_auth import get_current_user  # You may already have this
import re
from collections import defaultdict
from dateutil import parser

router = APIRouter()

@router.post("/alias/add")
def add_alias(
    alias: str,
    bank_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.query(BankAlias).filter_by(user_id=current_user.id, alias=alias).first()
    if existing:
        raise HTTPException(status_code=400, detail="Alias already exists.")

    new_alias = BankAlias(user_id=current_user.id, alias=alias, bank_name=bank_name)
    db.add(new_alias)
    db.commit()
    return {"detail": "Alias saved"}

@router.delete("/alias/delete/{alias}")
def delete_alias(
    alias: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    record = db.query(BankAlias).filter_by(user_id=current_user.id, alias=alias).first()
    if not record:
        raise HTTPException(status_code=404, detail="Alias not found.")

    db.delete(record)
    db.commit()
    return {"detail": f"Alias '{alias}' deleted successfully."}

@router.get("/alias/all")
def get_aliases(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    aliases = db.query(BankAlias).filter_by(user_id=current_user.id).all()
    return [{"alias": a.alias, "bank_name": a.bank_name} for a in aliases]


@router.post("/sms/parse")
def parse_sms(
    sender: str,
    message: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ✅ Fetch user-defined aliases
    aliases = db.query(BankAlias).filter(BankAlias.user_id == current_user.id).order_by(BankAlias.user_id.asc()).all()
    alias_dict = {a.alias: a.bank_name for a in aliases}
    bank_name = detect_bank_name(sender, message, alias_dict)

    # ✅ Use smart bank detection with fallback
    bank_name = detect_bank_name(sender, message, alias_dict)

    # ❌ No bank could be detected
    if bank_name == "Unknown":
      return {
    "status": "unknown_bank",
    "suggested_sender": sender,
    "suggested_message": message,
    "hint": "No match found. Please select the correct bank."
}

    # ✅ Extract SMS transaction details
    match = re.search(
    r'(credited|debited|sent|received).+?(?:INR|Rs\.?)\s*([\d,]+\.\d+).*?on\s+(\d{2}-\d{2}-\d{4}|\d{2}-[A-Z]{3}-\d{4})',
    message,
    re.IGNORECASE
)
    if not match:
        return {"error": "Could not parse SMS"}

    txn_type = "credit" if "credit" in match.group(1).lower() else "debit"
    amount = float(match.group(2).replace(",", ""))
    txn_date = parser.parse(match.group(3)).date()

    # 🛑 DUPLICATE CHECK
    existing = db.query(Transaction).filter(
        Transaction.amount == amount,
        Transaction.date == txn_date,
        Transaction.description == message[:100],
        Transaction.bank_name == bank_name,
        Transaction.user_id == current_user.id
    ).first()

    if existing:
        return {
            "status": "duplicate",
            "transaction_id": existing.id,
            "message": "Transaction already exists"
        }

    # ✅ Save transaction
    transaction = Transaction(
        user_id=current_user.id,
        amount=amount,
        type=txn_type,
        description=message[:100],
        bank_name=bank_name,
        date=txn_date,
        source="gpay"
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    # 🔍 Compute balance + spending by category
    transactions = db.query(Transaction).filter(
        Transaction.bank_name == bank_name,
        Transaction.user_id == current_user.id
    ).all()
    
    spending_by_category = defaultdict(float)
    current_balance = 0.0

    for txn in transactions:
        if txn.type == "credit":
            current_balance += txn.amount
        elif txn.type == "debit":
            current_balance -= txn.amount
            spending_by_category[txn.category or "Others"] += txn.amount

    spending_by_category["balance"] = current_balance

    # ✅ Check alerts
    alerts = check_spending_alerts(spending_by_category, db)

    return {
        "status": "saved",
        "transaction_id": transaction.id,
        "bank_name": bank_name,
        "alerts": alerts
    }
