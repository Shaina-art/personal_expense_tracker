from pydantic import BaseModel, field_validator , EmailStr
from datetime import date , datetime
from typing import Optional
from utils.timezone import to_ist

class TransactionCreate(BaseModel):
    date: datetime
    name: str
    amount: float
    type: str
    description: Optional[str] = None
    source: str
    category: Optional[str] = None
    bank_name: str

class TransactionOut(TransactionCreate):
    id: int
    user_id: int
    date: datetime
    name: str
    amount: float
    type: str
    description: str | None
    source: str
    category: str | None
    bank_name: str
    
    @field_validator("date", mode="before")
    def convert_to_ist(cls, value):
        return to_ist(value)
    class Config:
        orm_mode = True

class SettingCreate(BaseModel):
    min_balance: Optional[float] = None
    category: Optional[str] = None
    limit: Optional[float] = None
    bank_name: str
    actual_balance: Optional[float] = None

class SettingUpdate(BaseModel):
    min_balance: Optional[float] = None
    limit: Optional[float] = None  # Update either min or category limit
    bank_name: str
    actual_balance: Optional[float] = None

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

    @field_validator("start_date","end_date", "generated_at", mode="before")
    def convert_to_ist(cls, value):
        return to_ist(value)
    
    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    first_name: str
    last_name: str

    class Config:
        orm_mode = True
