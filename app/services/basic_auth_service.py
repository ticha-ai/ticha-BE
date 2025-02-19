from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import User
from app.schemas.basic_auth import UserLogin, UserRegister
from app.services.jwt_service import create_access_token, create_refresh_token

# 비밀번호 해싱을 위한 context 생성
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """비밀번호 해싱"""
    return pwd_context.hash(password)


async def register(db: AsyncSession, user_data: UserRegister):
    """회원가입"""
    # 이메일 중복 확인
    result = await db.execute(select(User).filter(User.email == user_data.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다")

    # 비밀번호 해싱
    hashed_password = get_password_hash(user_data.password)

    # 새 사용자 생성
    user = User(email=user_data.email, password=hashed_password, name=user_data.name)
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return {"id": user.id, "email": user.email, "name": user.name}


async def login(db: AsyncSession, user_data: UserLogin):
    """로그인"""
    # 사용자 확인
    result = await db.execute(select(User).filter(User.email == user_data.email))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=400, detail="등록되지 않은 이메일입니다")

    # 비밀번호 검증
    if not verify_password(user_data.password, user.password):
        raise HTTPException(status_code=400, detail="비밀번호가 일치하지 않습니다")

    # 토큰 생성
    access_token = create_access_token(data={"user_id": user.id})
    refresh_token = create_refresh_token(data={"user_id": user.id})

    # refresh_token 저장
    user.refresh_token = refresh_token
    db.add(user)
    await db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {"id": user.id, "email": user.email, "name": user.name},
    }
