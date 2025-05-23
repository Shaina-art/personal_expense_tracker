from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from database import get_db
from schemas import TransactionCreate, TransactionOut
from models import Transaction
from typing import List, Optional
from datetime import date
import shutil
from tagging import auto_tag

router = APIRouter()

@router.post("/add", response_model=TransactionOut)
def add_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    new_txn = Transaction(**transaction.dict())
    db.add(new_txn)
    db.commit()
    db.refresh(new_txn)
    return new_txn

@router.post("/add", response_model=TransactionOut)
def add_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    data = transaction.dict()
    if not data.get("category"):
        data["category"] = auto_tag(data.get("description") or "", db)
    new_txn = Transaction(**data)
    db.add(new_txn)
    db.commit()
    db.refresh(new_txn)
    return new_txn



@router.get("/", response_model=List[TransactionOut])
def get_transactions(
    db: Session = Depends(get_db),
    name: Optional[str] = Query(None),
    txn_type: Optional[str] = Query(None),
    min_amount: Optional[float] = Query(None),
    max_amount: Optional[float] = Query(None),
    bank_name: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None)
):
    query = db.query(Transaction)
    if bank_name:
        query = query.filter(Transaction.bank_name==bank_name)
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

    return query.order_by(Transaction.date.desc()).all()

@router.put("/{txn_id}", response_model=TransactionOut)
def update_transaction(txn_id: int, txn_update: TransactionCreate, bank_name: str = Query(...), db: Session = Depends(get_db)):
    txn = db.query(Transaction).filter(Transaction.id == txn_id , Transaction.bank_name == bank_name).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    for field, value in txn_update.dict().items():
        setattr(txn, field, value)
    db.commit()
    db.refresh(txn)
    return txn

@router.delete("/{txn_id}", response_model=dict)
def delete_transaction(txn_id: int, bank_name: str = Query(...), db: Session = Depends(get_db)):
    txn = db.query(Transaction).filter(Transaction.id == txn_id , Transaction.bank_name == bank_name).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(txn)
    db.commit()
    return {"detail": "Transaction deleted successfully"} 