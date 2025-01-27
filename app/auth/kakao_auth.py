from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.models.user import User
from app.services.jwt_service import create_access_token, create_refresh_token
from app.services.kakao_auth import get_kakao_access_token, get_kakao_profile


async def get_or_create_user(
    kakao_id: str, email: str, nickname: str, db: AsyncSession
) -> User:
    """
    DB에서 사용자 조회 또는 신규 사용자 생성
    """
    result = await db.execute(
        select(User).filter_by(oauth_provider="kakao", oauth_id=kakao_id)
    )
    user = result.scalars().first()

    if not user:
        user = User(
            name=nickname,
            email=email,
            oauth_provider="kakao",
            oauth_id=kakao_id,
            password="",  # OAuth 사용자는 비밀번호가 없음
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user


async def kakao_login(code: str, db: AsyncSession) -> dict:
    """
    카카오 로그인 처리 및 Access/Refresh Token 발급
    """
    # 1. 카카오 Access Token 요청
    access_token = await get_kakao_access_token(
        code=code,
        client_id=settings.KAKAO_CLIENT_ID,
        redirect_uri=settings.KAKAO_REDIRECT_URI,
    )
    profile = await get_kakao_profile(access_token)
    kakao_id = str(profile.get("id"))
    email = profile.get("kakao_account", {}).get("email")
    nickname = profile.get("properties", {}).get("nickname")

    user = await get_or_create_user(kakao_id, email, nickname, db)

    # Access/Refresh Token 생성
    access_token = create_access_token(
        data={"user_id": user.id}, expires_delta=timedelta(minutes=30)
    )
    refresh_token = create_refresh_token(data={"user_id": user.id})

    # DB에 Refresh Token 저장 (기존 토큰을 덮어씀)
    user.refresh_token = refresh_token
    await db.commit()

    return {"user": user, "access_token": access_token, "refresh_token": refresh_token}
