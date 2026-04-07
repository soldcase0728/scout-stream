from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session as DBSession
from fastapi.security import OAuth2PasswordBearer

from app.config import settings
from app.database import get_db
from app.models.coach import Coach
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, CoachResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def get_current_coach(
    token: str = Depends(oauth2_scheme), db: DBSession = Depends(get_db)
) -> Coach:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        coach_id: str = payload.get("sub")
        if coach_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    coach = db.query(Coach).filter(Coach.id == coach_id).first()
    if coach is None:
        raise HTTPException(status_code=401, detail="Coach not found")
    return coach


@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: DBSession = Depends(get_db)):
    existing = db.query(Coach).filter(Coach.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    coach = Coach(
        email=req.email,
        name=req.name,
        password_hash=pwd_context.hash(req.password),
    )
    db.add(coach)
    db.commit()
    db.refresh(coach)
    token = create_access_token({"sub": coach.id})
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: DBSession = Depends(get_db)):
    coach = db.query(Coach).filter(Coach.email == req.email).first()
    if not coach or not pwd_context.verify(req.password, coach.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": coach.id})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=CoachResponse)
def me(coach: Coach = Depends(get_current_coach)):
    return coach
