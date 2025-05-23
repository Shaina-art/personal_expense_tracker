# tagging.py
from sqlalchemy.orm import Session
from models import Category

def auto_tag(description: str, db: Session) -> str:
    desc = description.lower()

    categories = db.query(Category).all()
    for category in categories:
        keywords = category.keywords.lower().split(",")
        if any(word in desc for word in keywords):
            return category.name
    return "uncategorized"




