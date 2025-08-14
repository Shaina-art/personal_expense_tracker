from fastapi import APIRouter, Depends, HTTPException, status , Body
from sqlalchemy.orm import Session
from pydantic import BaseModel , EmailStr
from jose import jwt, JWTError
from auth_utils import hash_password, verify_password
from datetime import datetime, timedelta
from database import get_db
from models import User
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

SECRET_KEY = "68082a165da49fa9b7884a1496dc88fe0fcb2a4a506148285cb8b8096f56d99e"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 #7 days

#pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

router = APIRouter(prefix="/auth", tags=["Authentication"])

class UserCreate(BaseModel):
    username : str
    email: EmailStr
    first_name: str
    last_name: str
    password:str

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    first_name: str
    last_name: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

#def verify_password(plain, hashed):
    #return pwd_context.verify(plain, hashed)

#def hash_password(password):
    #return pwd_context.hash(password)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user_id = payload.get("user_id")
        print("TOKEN RECEIVED:", token)
        print("DECODED PAYLOAD:", payload)
        if username is None or user_id is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token error")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter((User.username == user.username) | (User.email == user.email)).first():
        raise HTTPException(status_code=400, detail="Username or email already exists")

    hashed_password = hash_password(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        password_hash=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter((User.username == form.username) | (User.email == form.username)).first()
    print(f"USERNAME from form: {form.username}")
    print(f"PASSWORD from form: {form.password}")

    if not user:
        print("❌ User not found")
        raise HTTPException(status_code=401, detail="Invalid username or password")

    print(f"✅ User found: {user.username}")
    print(f"🔒 Stored hash: {user.password_hash}")


    if not verify_password(form.password, user.password_hash):
        print("❌ Password does not match")
        raise HTTPException(status_code=401, detail="Invalid username or password")

    print("✅ Password verified successfully")

    token = create_access_token({"sub": user.username, "user_id": user.id})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/forgot_password")
def forgot_password(username: str = Body(...),email: str = Body(...), new_password: str = Body(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.password_hash = hash_password(new_password)
    db.commit()
    return {"message": "Password reset successful"}


@router.post("/reset_password")
def reset_password(
    new_password: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_user.password_hash = hash_password(new_password)
    db.commit()
    return {"message": "Password updated successfully"}


@router.delete("/delete_account")
def delete_account(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.delete(current_user)
    db.commit()
    return {"message": "User account deleted along with all related data."}
