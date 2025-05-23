from fastapi import APIRouter, Depends , HTTPException , Query
from sqlalchemy.orm import Session
from database import get_db
from analytics import analyze_period
from datetime import datetime, timedelta
from routers import analytics

router = APIRouter()

@router.get("/generate")
def generate_analytics(db: Session = Depends(get_db) ,bank_name: str = Query(...),):
    now = datetime.now()

    results = {
        "daily": analyze_period(db, now.replace(hour=0, minute=0, second=0), now, "daily", bank_name),
        "weekly": analyze_period(db, now - timedelta(days=7), now, "weekly", bank_name),
        "monthly": analyze_period(db, now - timedelta(days=30), now, "monthly", bank_name),
        "yearly": analyze_period(db, now - timedelta(days=365), now, "yearly", bank_name),
    }

    return {k: {
        "total_income": v.total_income,
        "total_expense": v.total_expense,
        "net_balance": v.net_balance,
        "status": v.status,
        "start_date": str(v.start_date),
        "end_date": str(v.end_date)
    } for k, v in results.items()}

@router.delete("/{analytics_id}", response_model=dict)
def delete_analytics(analytics_id: int, db: Session = Depends(get_db)):
    record = db.query(analytics).filter(analytics.id == analytics_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Analytics record not found")

    db.delete(record)
    db.commit()
    return {"detail": f"Analytics record with ID {analytics_id} deleted"}