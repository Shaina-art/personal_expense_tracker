from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from analytics import analyze_period
from datetime import datetime, timedelta
from models import Analytics, User
from routers.user_auth import get_current_user

router = APIRouter()

# ✅ Generate new analytics & return ordered history
@router.get("/generate")
def generate_analytics(
    db: Session = Depends(get_db),
    bank_name: str = Query(...),
    current_user: User = Depends(get_current_user)
):
    now = datetime.now()

    # Generate and save analytics for all periods
    results = {
        "daily": analyze_period(db, now.replace(hour=0, minute=0, second=0), now, "daily", bank_name, current_user.id),
        "weekly": analyze_period(db, now - timedelta(days=7), now, "weekly", bank_name, current_user.id),
        "monthly": analyze_period(db, now - timedelta(days=30), now, "monthly", bank_name, current_user.id),
        "yearly": analyze_period(db, now - timedelta(days=365), now, "yearly", bank_name, current_user.id),
    }

    # Fetch existing analytics for this user in order
    analytics_history = (
        db.query(Analytics)
        .filter(Analytics.user_id == current_user.id)
        .order_by(Analytics.user_id.asc(), Analytics.generated_at.desc())
        .all()
    )

    return {
        "generated": {
            k: {
                "total_income": v.total_income,
                "total_expense": v.total_expense,
                "net_balance": v.net_balance,
                "status": v.status,
                "start_date": str(v.start_date),
                "end_date": str(v.end_date),
            }
            for k, v in results.items()
        },
        "history": analytics_history
    }

# ✅ Delete analytics by ID
@router.delete("/{analytics_id}", response_model=dict)
def delete_analytics(
    analytics_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    record = db.query(Analytics).filter(
        Analytics.id == analytics_id,
        Analytics.user_id == current_user.id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Analytics record not found")

    db.delete(record)
    db.commit()
    return {"detail": f"Analytics record with ID {analytics_id} deleted"}
