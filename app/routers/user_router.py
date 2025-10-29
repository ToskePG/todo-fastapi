from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.core.database import SessionLocal
from app.models.user import User
from app.schemas.user_schemas import UserCreate, UserRead
from app.auth.security import create_access_token, create_email_token, decode_token
from app.utils.email_utils import send_verification_email
from app.schemas.user_schemas import RegisterUser, LoginUser

router = APIRouter(prefix="/users", tags=["users"])
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


# ----------------------
# DB Dependency
# ----------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------------------
# AUTH ROUTES
# ----------------------
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(
    background_tasks: BackgroundTasks,
    user_data: RegisterUser,
    db: Session = Depends(get_db)
):
    """Register new user and send confirmation email"""
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_pw = pwd_context.hash(user_data.password)
    new_user = User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        username=user_data.username,
        email=user_data.email,
        password=hashed_pw,
        is_confirmed=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Send verification email
    token = create_email_token(new_user.email)
    send_verification_email(background_tasks, new_user.email, token)

    return {"detail": "User registered. Please check your email to confirm your account."}


@router.get("/verify", status_code=status.HTTP_200_OK)
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
        return {"detail": "Email already confirmed."}

    user.is_confirmed = True
    db.commit()
    db.refresh(user)

    return {"detail": "Email confirmed successfully!"}


@router.post("/login", status_code=status.HTTP_200_OK)
def login_user(form_data: LoginUser, db: Session = Depends(get_db)):
    """Login and return JWT"""
    user = db.query(User).filter(User.email == form_data.email).first()
    if not user or not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not user.is_confirmed:
        raise HTTPException(status_code=403, detail="Please confirm your email first.")

    token = create_access_token(user.id, user.username)
    return {"access_token": token, "token_type": "bearer"}


# ----------------------
# USER ROUTES (PROTECTED)
# ----------------------
from app.auth.security import get_current_user

@router.get("/", response_model=list[UserRead], status_code=status.HTTP_200_OK)
def read_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all users (protected)"""
    return db.query(User).all()


@router.get("/{user_id}", response_model=UserRead, status_code=status.HTTP_200_OK)
def read_user_by_id(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user by ID (protected)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/by-username/{username}", response_model=UserRead, status_code=status.HTTP_200_OK)
def read_user_by_username(username: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user by username (protected)"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/me", response_model=UserRead, status_code=status.HTTP_200_OK)
def delete_own_user(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete the currently logged-in user and return the deleted user"""
    deleted_user = UserRead.from_orm(current_user)

    db.delete(current_user)
    db.commit()

    return deleted_user

@router.delete("/unconfirmed", status_code=status.HTTP_200_OK)
def delete_unconfirmed_users(db: Session = Depends(get_db)):
    """
    Delete all users where is_confirmed=False (for testing).
    Returns the count of deleted users.
    """
    deleted_count = db.query(User).filter(User.is_confirmed == False).delete(synchronize_session=False)
    db.commit()
    return {"detail": f"Deleted {deleted_count} unconfirmed users."}
