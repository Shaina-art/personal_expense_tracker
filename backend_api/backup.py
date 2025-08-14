# backup.py
import json
from models import Transaction
import csv
from io import StringIO


def export_data(db):
    transactions = db.query(Transaction).all()

    fieldnames = [
        "id", "date", "name", "amount", "type",
        "description", "source", "category", "bank_name"
    ]

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for txn in transactions:
        writer.writerow({
            "id": txn.id,
            "date": txn.date.isoformat() if txn.date else "",
            "name": txn.name,
            "amount": txn.amount,
            "type": txn.type,
            "description": txn.description or "",
            "source": txn.source or "",
            "category": txn.category or "",
            "bank_name": txn.bank_name,
        })

    return output.getvalue()


def import_data(db, json_data: str, user_id: int):
    imported = json.loads(json_data)
    count = 0

    for t in imported:
        # Skip if duplicate
        exists = db.query(Transaction).filter_by(
            user_id=user_id,
            amount=t["amount"],
            date=t["date"],
            description=t["description"][:100],
            bank_name=t["bank_name"]
        ).first()
        if exists:
            continue

        new_txn = Transaction(
            user_id=user_id,
            date=t["date"],
            name=t["name"],
            amount=t["amount"],
            type=t["type"],
            description=t["description"],
            source=t["source"],
            category=t.get("category"),
            bank_name=t["bank_name"]
        )
        db.add(new_txn)
        count += 1

    db.commit()
    return {"imported": count}

