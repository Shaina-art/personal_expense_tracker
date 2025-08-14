from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models import Settings, User , Transaction
from schemas import SettingCreate, SettingUpdate, SettingOut
from routers.user_auth import get_current_user

router = APIRouter()

# ✅ Create or update a setting
@router.post("/", response_model=list[SettingOut])
def all_setting(
    data: SettingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    created_settings = []

    # Handle min_balance
    if data.min_balance is not None:
        setting = db.query(Settings).filter(
            Settings.min_balance.isnot(None),
            Settings.bank_name == data.bank_name,
            Settings.user_id == current_user.id
        ).first()
        if setting:
            setting.min_balance = data.min_balance
        else:
            setting = Settings(
                min_balance=data.min_balance,
                bank_name=data.bank_name,
                user_id=current_user.id
            )
            db.add(setting)
        db.flush()
        created_settings.append(setting)

    # Handle category limit
    if data.category:
        setting = db.query(Settings).filter(
            Settings.category == data.category,
            Settings.bank_name == data.bank_name,
            Settings.user_id == current_user.id
        ).first()
        if setting:
            setting.limit = data.limit
        else:
            setting = Settings(
                category=data.category,
                limit=data.limit,
                bank_name=data.bank_name,
                user_id=current_user.id
            )
            db.add(setting)
        db.flush()
        created_settings.append(setting)

        # routers/settings.py → in @router.post("/")
    if data.actual_balance is not None:
        setting = db.query(Settings).filter(
        Settings.actual_balance.isnot(None),
        Settings.bank_name == data.bank_name,
        Settings.user_id == current_user.id
    ).first()
    if setting:
        setting.actual_balance = data.actual_balance
    else:
        setting = Settings(
            actual_balance=data.actual_balance,
            bank_name=data.bank_name,
            user_id=current_user.id
        )
        db.add(setting)
    db.flush()
    created_settings.append(setting)


    if not created_settings:
        raise HTTPException(status_code=400, detail="Must provide category or min_balance")

    db.commit()
    return created_settings

# ✅ Grouped response for UI (min_balance + category limits)
# routers/settings.py
@router.get("/get", response_model=dict)
def get_grouped_settings(
    bank_name: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):


    # Fetch settings
    all_settings = db.query(Settings).filter(
        Settings.bank_name == bank_name,
        Settings.user_id == current_user.id
    ).order_by(Settings.user_id.asc()).all()


    # Get min_balance (if exists)
    min_balance_setting = next((s for s in all_settings if s.min_balance is not None), None)
    min_balance = min_balance_setting.min_balance if min_balance_setting else None

    # Get actual_balance (if set)
    actual_setting = next((s for s in all_settings if s.actual_balance is not None), None)
    actual_balance = actual_setting.actual_balance if actual_setting else 0.0

    # Get calculated balance from transactions
    transactions = db.query(Transaction).filter(
        Transaction.bank_name == bank_name,
        Transaction.user_id == current_user.id
    ).all()

    calculated_balance = 0.0
    for t in transactions:
        if t.type == "credit":
            calculated_balance += t.amount
        elif t.type == "debit":
            calculated_balance -= t.amount

    total_balance = actual_balance + calculated_balance

    # Get category limits
    category_settings = [
        {"category": s.category, "limit": s.limit}
        for s in all_settings if s.category and s.limit is not None
    ]

    return {
        "min_balance": min_balance,
        "actual_balance": actual_balance,
        "calculated_balance": calculated_balance,
        "total_balance": total_balance,
        "categories": category_settings
    }


# ✅ Update by ID
@router.put("/{setting_id}", response_model=SettingOut)
def update_setting(
    setting_id: int,
    data: SettingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    setting = db.query(Settings).filter(
        Settings.id == setting_id,
        Settings.user_id == current_user.id
    ).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")

    if data.min_balance is not None:
        setting.min_balance = data.min_balance
    if data.limit is not None:
        setting.limit = data.limit

    db.commit()
    db.refresh(setting)
    return setting

# ✅ Delete by ID
@router.delete("/{setting_id}", response_model=dict)
def delete_setting(
    setting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    setting = db.query(Settings).filter(
        Settings.id == setting_id,
        Settings.user_id == current_user.id
    ).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    db.delete(setting)
    db.commit()
    return {"detail": f"Setting with ID {setting_id} deleted"}

# ✅ Logic utility for alerts
def check_spending_alerts(spending_by_category, db: Session, bank_name: str, user_id: int):
    alerts = []
    all_settings = db.query(Settings).filter(
        Settings.bank_name == bank_name,
        Settings.user_id == user_id
    ).all()

    min_setting = next((s for s in all_settings if s.min_balance is not None), None)

    # Min balance alert
    if min_setting and "balance" in spending_by_category:
        if spending_by_category["balance"] < min_setting.min_balance:
            alerts.append(
                f"⚠️ Balance ₹{spending_by_category['balance']} is below minimum of ₹{min_setting.min_balance}"
            )

    # Category limits
    for s in all_settings:
        if s.category and s.limit is not None:
            spent = spending_by_category.get(s.category, 0)
            if spent > s.limit:
                alerts.append(
                    f"⚠️ Over budget in {s.category}: ₹{spent} > ₹{s.limit}"
                )

    return alerts
