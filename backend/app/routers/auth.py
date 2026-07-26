from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import bcrypt
from datetime import datetime, timedelta
from jose import jwt

from app.db.session import get_db
from app.db.models import User
from app.models.schemas import UserSignup, UserLogin, TokenResponse
from app.config import settings

router = APIRouter(prefix = "/auth", tags=["Auth"])

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes= settings.access_token_expire_minutes)
    to_encode.update({"exp" : expire})
    return jwt.encode(to_encode,settings.secret_key, algorithm="HS256")

@router.post("/signup", response_model = TokenResponse)
async def signup(request: UserSignup, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.email == request.email)
    )

    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    user = User(
        email = request.email,
        password_hash = hash_password(request.password),
        display_name=request.display_name,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token({
        "sub" : str(user.id),
        "email": user.email
    })

    return TokenResponse(
        access_token = token
    )

@router.post("/login", response_model=TokenResponse)
async def login(request: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.email == request.email)
    )

    user = result.scalar_one_or_none()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code = 401,
            detail="Invalid email or password"
        )

    token = create_access_token(
        {
            "sub": str(user.id), 
            "email": user.email
        }
    )

    return TokenResponse(
        access_token = token
    )