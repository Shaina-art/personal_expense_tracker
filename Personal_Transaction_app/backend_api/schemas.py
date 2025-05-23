from pydantic import BaseModel, Field
from datetime import date , datetime
from typing import Optional

class TransactionCreate(BaseModel):
    date: date
    name: str
    amount: float
    type: str
    description: Optional[str] = None
    source: str
    category: Optional[str] = None
    bank_name: str

class TransactionOut(TransactionCreate):
    id: int

    class Config:
        orm_mode = True

class SettingCreate(BaseModel):
    min_balance: Optional[float] = None
    category: Optional[str] = None
    limit: Optional[float] = None
    bank_name: str

class SettingUpdate(BaseModel):
    min_balance: Optional[float] = None
    limit: Optional[float] = None  # Update either min or category limit
    bank_name: str

class SettingOut(BaseModel):
    id: int
    min_balance: Optional[float]
    category: Optional[str]
    limit: Optional[float]
    bank_name: str 

    class Config:
        orm_mode = True

class CategoryCreate(BaseModel):
    name: str
    keywords: Optional[str] = ""  # Optional for default categories

class CategoryOut(BaseModel):
    id: int
    name: str
    keywords: Optional[str]
    is_default: int

    class Config:
        orm_mode = True

class AnalyticsOut(BaseModel):
    period: str
    start_date: date
    end_date: date
    total_income: float
    total_expense: float
    net_balance: float
    status: str
    bank_name: str
    generated_at: datetime

    class Config:
        orm_mode = True
