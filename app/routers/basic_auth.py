from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.basic_auth import TokenResponse, UserLogin, UserRegister
from app.services import basic_auth_service  # 함수들을 직접 import

router = APIRouter(prefix="/auth", tags=["basic-auth"])


@router.post("/register")
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    """일반 회원가입"""
    return await basic_auth_service.register(db, user_data)


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """일반 로그인"""
    return await basic_auth_service.login(db, user_data)
