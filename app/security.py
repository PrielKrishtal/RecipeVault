import logging
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

# Correct relative imports
from . import models
from .core.config import settings
from .db import get_db

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()
    # Calculate expiration time
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    # Encode the token with the secret key and algorithm
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return encoded_jwt


# This object will look for the Authorization header with a Bearer token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    logging.info("--- Attempting to get current user ---")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        logging.info(f"Token payload decoded: {payload}")
        user_id: str = payload.get("sub")
        if user_id is None:
            logging.error("User ID ('sub') is missing from token payload.")
            raise credentials_exception
    except JWTError as e:
        logging.error(f"JWTError during token decode: {e}")
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    logging.info(f"User found in DB: {user.email if user else 'None'}")

    if user is None:
        logging.error("User from token not found in database.")
        raise credentials_exception

    logging.info(f"Successfully returning user: {user.email}")
    return user
