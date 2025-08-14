from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Date, ForeignKey 
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
from sqlalchemy.sql import func


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)  # ✅ Add this
    first_name = Column(String)                      # ✅ Add this
    last_name = Column(String)                       # ✅ Add this
    password_hash = Column(String)

    # Relationships
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete")
    categories = relationship("Category", back_populates="user", cascade="all, delete")
    settings = relationship("Settings", back_populates="user", cascade="all, delete")  # ✅ fixed typo: settngs → settings
    analytics = relationship("Analytics", back_populates="user", cascade="all, delete")
    bank_aliases = relationship("BankAlias", back_populates="user", cascade="all, delete-orphan")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime,  default=lambda: datetime.now())
    name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(String, nullable=False)  # "credit" or "debit"
    description = Column(String)
    source = Column(String)  # "manual" or "gpay"
    category = Column(String, nullable=True)
    bank_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="transactions")

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date.isoformat(),
            "name": self.name,
            "amount": self.amount,
            "type": self.type,
            "description": self.description,
            "source": self.source,
            "category": self.category,
            "bank_name": self.bank_name
        }


class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    actual_balance = Column(Float, nullable=True) 
    min_balance = Column(Float, nullable=True)  # For global balance reminder
    bank_name = Column(String, nullable=False)
    category = Column(String, nullable=True)    # For specific category
    limit = Column(Float, nullable=True)        # Optional limit for that category

    user = relationship("User", back_populates="settings")


class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, index=True)
    keywords = Column(String)  # Comma-separated keywords
    is_default = Column(Boolean, default=False)

    user = relationship("User", back_populates="categories")


class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    period = Column(String, index=True)  # daily, weekly, monthly, yearly
    start_date = Column(Date)
    end_date = Column(Date)
    total_income = Column(Float, default=0.0)
    total_expense = Column(Float, default=0.0)
    net_balance = Column(Float, default=0.0)
    status = Column(String)  # profit or loss
    bank_name = Column(String, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="analytics")

class BankAlias(Base):
    __tablename__ = "bank_alias"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    alias = Column(String, nullable=False)
    bank_name = Column(String, nullable=False)

    user = relationship("User", back_populates="bank_aliases")
