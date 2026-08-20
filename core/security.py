from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Union, Any
from core.config import settings
import jwt

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


#  HASH 
def hash_password(password: str) -> str:
    return pwd_context.hash(password[:72])

#  VERIFY 
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(
        plain_password[:72],
        hashed_password
    )

# CREATE TOKEN
def create_access_token(subject, expires_delta=None):
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # "exp" = fecha de expiración, "sub" = subject (el dueño del token)
    to_encode = {"exp": expire, "sub": str(subject)}
    
    # Firmar y generar el token
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY,      
        algorithm=settings.ALGORITHM 
    )
    return encoded_jwt