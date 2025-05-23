# backup.py
import json
from .models import Transaction

def export_data(db):
    transactions = db.query(Transaction).all()
    return json.dumps([t.to_dict() for t in transactions], indent=4)

def import_data(db, json_data):
    for t in json.loads(json_data):
        db.add(Transaction(**t))
    db.commit()
