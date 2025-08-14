from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database import SessionLocal, get_db
from backup import export_data
from routers import transactions, settings, category, analytics, sms_parser, user_auth

app = FastAPI()

# Register routers
app.include_router(user_auth.router)
app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
app.include_router(settings.router, prefix="/settings", tags=["Settings"])
app.include_router(category.router, prefix="/category", tags=["Category"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
app.include_router(sms_parser.router, prefix="/sms_parser", tags=["SMS Parser"])

# CSV backup route
@app.get("/backup/csv", tags=["Backup"])
def download_csv(db: Session = Depends(get_db)):
    try:
        csv_data = export_data(db)
        return StreamingResponse(
            iter([csv_data]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=transactions_backup.csv"}
        )
    except Exception as e:
        print("❌ CSV Export Error:", str(e))
        raise HTTPException(status_code=500, detail="CSV export failed")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Personal Transaction App API"}
