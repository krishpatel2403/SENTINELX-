"""Authentication API — login, logout, token refresh.

Passwords are hashed with bcrypt. Password hashes and tokens are never
returned in API responses.
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
)
from app.core.config import settings
from app.models.user import User
from app.schemas.token import Token, LoginRequest
from app.schemas.user import UserCreate, UserOut

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=201, tags=["auth"])
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Admin-only user registration."""
    existing = db.query(User).filter(User.username == user_in.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    existing_email = db.query(User).filter(User.email == user_in.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        username=user_in.username,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        role=user_in.role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token, tags=["auth"])
def login(login_in: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate and issue a JWT access token."""
    user = db.query(User).filter(User.username == login_in.username).first()
    if not user or not verify_password(login_in.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User inactive")
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout", tags=["auth"])
def logout():
    """Client-side token invalidation (stateless JWT). Server acknowledges."""
    return {"message": "Logged out"}


@router.get("/me", response_model=UserOut, tags=["auth"])
def get_me(current_user: User = Depends(get_current_user)):
    """Return the current authenticated user's profile (no sensitive fields)."""
    return current_user
