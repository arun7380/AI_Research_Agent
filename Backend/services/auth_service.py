from datetime import datetime, timedelta
import hashlib
import hmac
import os
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from config.settings import settings
from models.user import User
from schemas.user import TokenPayload, UserCreate, UserLogin

# Crypt context for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash raw password using bcrypt with fallback.
    """
    try:
        return pwd_context.hash(password)
    except Exception:
        # Fallback PBKDF2 hash if bcrypt C-extension is unavailable
        salt = os.urandom(16)
        pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
        return f"pbkdf2_sha256${salt.hex()}${pwd_hash.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hashed stored password.
    """
    if hashed_password.startswith("pbkdf2_sha256$"):
        parts = hashed_password.split("$")
        if len(parts) == 3:
            salt = bytes.fromhex(parts[1])
            expected_hash = parts[2]
            computed_hash = hashlib.pbkdf2_hmac(
                "sha256", plain_password.encode("utf-8"), salt, 100000
            ).hex()
            return hmac.compare_digest(computed_hash, expected_hash)
        return False
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def create_access_token(data: dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Generate JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenPayload]:
    """
    Decode and validate JWT access token.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        sub: str = payload.get("sub")
        if sub is None:
            return None
        return TokenPayload(sub=sub)
    except JWTError:
        return None


def register_user(db: Session, user_in: UserCreate) -> User:
    """
    Register a new user in DB.
    """
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise ValueError("User with this email already exists")

    new_user = User(
        full_name=user_in.full_name,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def authenticate_user(db: Session, user_login: UserLogin) -> Optional[User]:
    """
    Authenticate user login credentials.
    """
    user = db.query(User).filter(User.email == user_login.email).first()
    if not user:
        return None
    if not verify_password(user_login.password, user.hashed_password):
        return None
    return user
