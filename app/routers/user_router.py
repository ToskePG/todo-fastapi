from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.core.database import SessionLocal
from app.models.user import User
from app.schemas.user_schemas import UserCreate, UserRead
from app.auth.security import get_current_user

router = APIRouter(prefix="/users", tags=["users"])
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


# ----------------------
# DEPENDENCIES
# ----------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# ----------------------
# PUBLIC ROUTES
# ----------------------
@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user (public endpoint)"""
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed_pw = hash_password(user.password)
    db_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        email=user.email,
        password=hashed_pw
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


# ----------------------
# PROTECTED ROUTES
# ----------------------
@router.get("/", response_model=list[UserRead], status_code=status.HTTP_200_OK)
def read_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all users (protected)"""
    return db.query(User).all()


@router.get("/id/{user_id}", response_model=UserRead, status_code=status.HTTP_200_OK)
def read_user_by_id(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user by ID (protected)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("/email/{email}", response_model=UserRead, status_code=status.HTTP_200_OK)
def read_user_by_email(email: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user by email (protected)"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("/username/{username}", response_model=UserRead, status_code=status.HTTP_200_OK)
def read_user_by_username(username: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user by username (protected)"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.delete("/me", response_model=UserRead, status_code=status.HTTP_200_OK)
def delete_own_user(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete the currently logged-in user and return the deleted user"""
    deleted_user = UserRead.from_orm(current_user)  # convert ORM to schema

    db.delete(current_user)
    db.commit()

    return deleted_user
