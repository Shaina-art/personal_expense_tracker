from fastapi import APIRouter, Depends, HTTPException , Query
from sqlalchemy.orm import Session
from database import get_db
from models import Settings
from schemas import SettingCreate, SettingUpdate, SettingOut

router = APIRouter()

# Create or update a setting
@router.post("/", response_model=SettingOut)
def all_setting(data: SettingCreate, db: Session = Depends(get_db)):
    if data.category:
        setting = db.query(Settings).filter(
            Settings.category == data.category,
            Settings.bank_name == data.bank_name
        ).first()
        if setting:
            setting.limit = data.limit
        else:
            setting = Settings(
                category=data.category,
                limit=data.limit,
                bank_name=data.bank_name
            )
            db.add(setting)
    elif data.min_balance is not None:
        setting = db.query(Settings).filter(
            Settings.min_balance.isnot(None),
            Settings.bank_name == data.bank_name
        ).first()
        if setting:
            setting.min_balance = data.min_balance
        else:
            setting = Settings(
                min_balance=data.min_balance,
                bank_name=data.bank_name
            )
            db.add(setting)
    else:
        raise HTTPException(status_code=400, detail="Must provide category or min_balance")
    
    db.commit()
    db.refresh(setting)
    return setting

# Get all settings
@router.get("/get", response_model=list[SettingOut])
def get_all_settings(bank_name: str = Query(...), db: Session = Depends(get_db)):
    return db.query(Settings).filter(Settings.bank_name == bank_name).all()

# Update by ID
@router.put("/{setting_id}", response_model=SettingOut)
def update_setting(setting_id: int, data: SettingUpdate, db: Session = Depends(get_db)):
    setting = db.query(Settings).filter(Settings.id == setting_id).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    if data.min_balance is not None:
        setting.min_balance = data.min_balance
    if data.limit is not None:
        setting.limit = data.limit
    
    db.commit()
    db.refresh(setting)
    return setting

# Delete by ID
@router.delete("/{setting_id}", response_model=dict)
def delete_setting(setting_id: int, db: Session = Depends(get_db)):
    setting = db.query(Settings).filter(Settings.id == setting_id).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    db.delete(setting)
    db.commit()
    return {"detail": f"Setting with ID {setting_id} deleted"}

# Check alerts (can be called from analytics or transaction logic)
def check_spending_alerts(spending_by_category, db: Session, bank_name: str):
    alerts = []
    all_settings = db.query(Settings).filter(Settings.bank_name == bank_name).all()
    min_setting = next((s for s in all_settings if s.min_balance is not None), None)

    # Min balance alert
    if min_setting and "balance" in spending_by_category:
        if spending_by_category["balance"] < min_setting.min_balance:
            alerts.append(f"⚠️ Balance ₹{spending_by_category['balance']} is below minimum of ₹{min_setting.min_balance}")

    # Category limits
    for s in all_settings:
        if s.category and s.limit is not None:
            spent = spending_by_category.get(s.category, 0)
            if spent > s.limit:
                alerts.append(f"⚠️ Over budget in {s.category}: ₹{spent} > ₹{s.limit}")
    
    return alerts 
