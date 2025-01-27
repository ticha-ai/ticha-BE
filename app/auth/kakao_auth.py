from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.models.user import User
from app.services.jwt_service import create_access_token
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
    카카오 로그인 처리: 액세스 토큰 요청, 사용자 생성/조회, JWT 발급
    """
    access_token = await get_kakao_access_token(
        code=code,
        client_id=settings.KAKAO_CLIENT_ID,  # 환경 변수에서 가져옴
        redirect_uri=settings.KAKAO_REDIRECT_URI,  # 환경 변수에서 가져옴
    )
    profile = await get_kakao_profile(access_token)
    kakao_id = str(profile.get("id"))
    email = profile.get("kakao_account", {}).get("email")
    nickname = profile.get("properties", {}).get("nickname")

    user = await get_or_create_user(kakao_id, email, nickname, db)
    token = create_access_token(
        data={"user_id": user.id}, expires_delta=timedelta(hours=1)
    )

    return {"user": user, "access_token": token}
