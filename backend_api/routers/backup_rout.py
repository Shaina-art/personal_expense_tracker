from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from backup import export_data, import_data
from routers.user_auth import get_current_user
from models import User

router = APIRouter(prefix="/backup", tags=["Backup"])

@router.get("/export")
def export_user_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return export_data(db, user_id=current_user.id)

@router.post("/import")
def import_user_data(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        contents = file.file.read().decode("utf-8")
        result = import_data(db, contents, user_id=current_user.id)
        return {"message": f"Imported {result['imported']} transactions"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
