from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas 
from routers.user_auth import get_current_user
from models import Settings, Category, User
from typing import List, Dict, Optional

router = APIRouter()

# ✅ Create a category (user-defined)
@router.post("/", response_model=schemas.CategoryOut)
def category(
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.query(Category).filter(
        Category.name == category.name,
        Category.user_id == current_user.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")

    new_category = Category(
        name=category.name,
        keywords=category.keywords,
        is_default=False,
        user_id=current_user.id
    )
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

# ✅ List all user-defined categories with their limits
@router.get("/get", response_model=List[Dict])
def get_categories_with_limits(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    categories = db.query(Category).filter(
        Category.user_id == current_user.id
    ).all()

    settings = db.query(Settings).filter(Settings.user_id == current_user.id).all()
    category_limits = {s.category: s.limit for s in settings if s.category}

    result = []
    for cat in categories:
        result.append({
            "category": cat.name,
            "keywords": cat.keywords,
            "limit": category_limits.get(cat.name)
        })

    return result

# ✅ Get specific category with limit
@router.get("/get/{category_name}", response_model=Dict)
def get_category_by_name(
    category_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    category = db.query(Category).filter(
        Category.name == category_name,
        Category.user_id == current_user.id
    ).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    setting = db.query(Settings).filter(
        Settings.user_id == current_user.id,
        Settings.category == category_name
    ).first()

    return {
        "category": category.name,
        "keywords": category.keywords,
        "limit": setting.limit if setting else None
    }
#update category 
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas 
from schemas import CategoryCreate, CategoryOut
from routers.user_auth import get_current_user
from models import Settings, Category, User
from typing import List, Dict, Optional

router = APIRouter()

# ✅ Create a category (user-defined)
@router.post("/", response_model=schemas.CategoryOut)
def category(
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.query(Category).filter(
        Category.name == category.name,
        Category.user_id == current_user.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")

    new_category = Category(
        name=category.name,
        keywords=category.keywords,
        is_default=False,
        user_id=current_user.id
    )
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

# ✅ List all user-defined categories with their limits
@router.get("/get", response_model=List[Dict])
def get_categories_with_limits(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    categories = db.query(Category).filter(
        Category.user_id == current_user.id
    ).order_by(Category.user_id.asc()).all()
    
    settings = db.query(Settings).filter(Settings.user_id == current_user.id).all()
    category_limits = {s.category: s.limit for s in settings if s.category}

    result = []
    for cat in categories:
        result.append({
            "category": cat.name,
            "keywords": cat.keywords,
            "limit": category_limits.get(cat.name)
        })

    return result

# ✅ Get specific category with limit
@router.get("/get/{category_name}", response_model=Dict)
def get_category_by_name(
    category_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    category = db.query(Category).filter(
        Category.name == category_name,
        Category.user_id == current_user.id
    ).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    setting = db.query(Settings).filter(
        Settings.user_id == current_user.id,
        Settings.category == category_name
    ).first()

    return {
        "category": category.name,
        "keywords": category.keywords,
        "limit": setting.limit if setting else None
    }
#update category 
@router.put("/{category_id}", response_model=schemas.CategoryOut)
def update_category(
    category_id: int,
    updated: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    category.name = updated.name
    category.keywords = updated.keywords
    db.commit()
    db.refresh(category)
    return category


# ✅ Delete a category
@router.delete("/{category_id}", response_model=dict)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    db.delete(category)
    db.commit()
    return {"detail": f"Category with ID {category_id} deleted"}



# ✅ Delete a category
@router.delete("/{category_id}", response_model=dict)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    db.delete(category)
    db.commit()
    return {"detail": f"Category with ID {category_id} deleted"}
