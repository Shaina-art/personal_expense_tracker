from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas

router = APIRouter()

# ✅ Create a category (user-defined)
@router.post("/", response_model=schemas.CategoryOut)
def category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Category).filter(models.Category.name == category.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")

    new_category = models.Category(
        name=category.name,
        keywords=category.keywords,
        is_default=0
    )
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

# ✅ List all categories (default + user-defined)
@router.get("/get", response_model=list[schemas.CategoryOut])
def get_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).all()


DEFAULT_CATEGORIES = [
    {"name": "groceries", "keywords": "d mart,big bazaar,supermarket"},
    {"name": "food", "keywords": "zomato,swiggy,restaurant"},
    {"name": "salary", "keywords": "salary,credited,income"},
    {"name": "rent", "keywords": "rent,landlord"},
]

def seed_default_categories(db: Session):
    for cat in DEFAULT_CATEGORIES:
        existing = db.query(models.Category).filter_by(name=cat["name"]).first()
        if not existing:
            db_category = models.Category(name=cat["name"], keywords=cat["keywords"], is_default=True)
            db.add(db_category)
    db.commit()

from fastapi import HTTPException

@router.delete("/{category_id}", response_model=dict)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    db.delete(category)
    db.commit()
    return {"detail": f"Category with ID {category_id} deleted"}
