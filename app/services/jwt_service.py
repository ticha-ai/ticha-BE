from datetime import datetime, timedelta

import jwt

from app.core.config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    JWT Access Token 생성
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Refresh Token 생성
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=7))  # 기본 7일 만료
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    """
    Access Token 또는 Refresh Token 디코딩
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
