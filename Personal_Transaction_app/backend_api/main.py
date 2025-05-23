from fastapi import FastAPI
from routers import transactions, settings , category , analytics , sms_parser
from database import SessionLocal

app = FastAPI()

# Register routers
app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
app.include_router(settings.router, prefix="/settings", tags=["Settings"])   # Add this at top
app.include_router(category.router,prefix="/category",tags=["Category"])  # Register it like others
app.include_router(analytics.router , prefix="/analytics" , tags=["analytics"])
app.include_router(sms_parser.router , prefix="/sms_parser" , tags=["sms_parser"] )

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    category.seed_default_categories(db)
    db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Personal Transaction App API"}