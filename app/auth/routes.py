from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models.user import User
from app.core.database import SessionLocal
from app.auth.security import (
    create_access_token, create_email_token, decode_token
)
from app.utils.email_utils import send_verification_email

router = APIRouter(prefix="/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register")
def register_user(background_tasks: BackgroundTasks, user_data: dict, db: Session = Depends(get_db)):
    """Register new user and send confirmation email"""
    email = user_data["email"]
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = pwd_context.hash(user_data["password"])
    new_user = User(
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
        username=user_data["username"],
        email=email,
        password=hashed_pw,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_email_token(new_user.email)
    send_verification_email(background_tasks, new_user.email, token)

    return {"detail": "User registered. Please check your email to confirm your account."}


@router.get("/verify")
def verify_email(token: str, db: Session = Depends(get_db)):
    """Confirm email address"""
    payload = decode_token(token)
    if not payload or payload.get("type") != "email_verification":
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_confirmed:
        return {"detail": "Email already confirmed"}

    user.is_confirmed = True
    db.commit()
    return {"detail": "Email confirmed successfully!"}


@router.post("/login")
def login_user(form_data: dict, db: Session = Depends(get_db)):
    """Login and return JWT"""
    email = form_data["email"]
    password = form_data["password"]

    user = db.query(User).filter(User.email == email).first()
    if not user or not pwd_context.verify(password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not user.is_confirmed:
        raise HTTPException(status_code=403, detail="Please confirm your email first.")

    token = create_access_token(user.id, user.username)
    return {"access_token": token, "token_type": "bearer"}
