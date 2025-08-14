from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_ 
from database import get_db
from schemas import TransactionCreate, TransactionOut
from models import Transaction, User
from typing import List, Optional
from datetime import date , datetime
from tagging import auto_tag
from routers.user_auth import get_current_user
from utils.timezone import to_ist
router = APIRouter()

# ✅ Add a transaction (auto-tagging + user_id)
@router.post("/add", response_model=TransactionOut)
def add_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    data = transaction.dict()
    if not data.get("category"):
        data["category"] = auto_tag(data.get("description") or "", db)
    data["user_id"] = current_user.id  # 💡 Assign current user
    new_txn = Transaction(**data,date=datetime.utcnow(),created_at=datetime.utcnow())
    db.add(new_txn)
    db.commit()
    db.refresh(new_txn)
    return new_txn

# ✅ Get all transactions for the current user
# ✅ Get all transactions for the current user
@router.get("/", response_model=List[TransactionOut])
def get_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    name: Optional[str] = Query(None),
    txn_type: Optional[str] = Query(None),
    min_amount: Optional[float] = Query(None),
    max_amount: Optional[float] = Query(None),
    bank_name: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None)
):
    query = db.query(Transaction).filter(Transaction.user_id == current_user.id)

    if bank_name:
        query = query.filter(Transaction.bank_name == bank_name)
    if name:
        query = query.filter(Transaction.name.ilike(f"%{name}%"))
    if txn_type:
        query = query.filter(Transaction.type == txn_type)
    if min_amount is not None:
        query = query.filter(Transaction.amount >= min_amount)
    if max_amount is not None:
        query = query.filter(Transaction.amount <= max_amount)
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)

    transactions = query.order_by(Transaction.user_id.asc(), Transaction.date.desc()).all()

    # Convert UTC → IST for created_at before returning
    for txn in transactions:
        if txn.created_at:
            txn.created_at = to_ist(txn.created_at)

    return transactions

# ✅ Update a transaction (ensure user owns it)
@router.put("/{txn_id}", response_model=TransactionOut)
def update_transaction(
    txn_id: int,
    txn_update: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    txn = db.query(Transaction).filter(
        and_(Transaction.id == txn_id, Transaction.user_id == current_user.id)
    ).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    for field, value in txn_update.dict().items():
        setattr(txn, field, value)
    db.commit()
    db.refresh(txn)
    return txn

# ✅ Delete a transaction (ensure user owns it)
@router.delete("/{txn_id}", response_model=dict)
def delete_transaction(
    txn_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    txn = db.query(Transaction).filter(
        and_(Transaction.id == txn_id, Transaction.user_id == current_user.id)
    ).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(txn)
    db.commit()
    return {"detail": "Transaction deleted successfully"}
