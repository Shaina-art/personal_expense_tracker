from sqlalchemy import Column, Integer, String, DateTime, Float ,Boolean , Date
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base ,get_db
 
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    name = Column(String , nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(String, nullable=False)  # "credit" or "debit"
    description = Column(String)
    source = Column(String)  # "manual" or "gpay"
    category = Column(String, nullable=True)
    bank_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date.isoformat(),
            "name": self.name,
            "amount": self.amount,
            "type": self.type,
            "description": self.description,
            "source":self.source,
            "category": self.category
        }


class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    min_balance = Column(Float, nullable=True)  # For global balance reminder
    bank_name = Column(String, nullable=False)
    category = Column(String, nullable=True)    # For specific category
    limit = Column(Float, nullable=True)      # optional limit for that category


class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    keywords = Column(String)  # Comma-separated keywords
    is_default = Column(Boolean, default=False)


class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, index=True)
    period = Column(String, index=True)  # daily, weekly, monthly, yearly
    start_date = Column(Date)
    end_date = Column(Date)
    total_income = Column(Float, default=0.0)
    total_expense = Column(Float, default=0.0)
    net_balance = Column(Float, default=0.0)
    status = Column(String)  # profit or loss
    bank_name = Column(String, nullable=False) 
    generated_at = Column(DateTime, default=datetime.utcnow)

