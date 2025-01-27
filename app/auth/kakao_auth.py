from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.models.user import User
from app.services.jwt_service import create_access_token  # JWT 생성 함수 임포트
from app.services.kakao_auth import get_kakao_access_token, get_kakao_profile


async def kakao_login(code: str, db: AsyncSession) -> dict:
    """
    카카오 로그인 처리 및 회원가입:
    1. 카카오 Access Token 요청
    2. 사용자 프로필 요청
    3. DB에서 사용자 정보 확인
    4. 신규 사용자면 회원가입 처리
    5. JWT 발급 후 반환
    """
    # 1. 카카오 Access Token 요청
    access_token = await get_kakao_access_token(
        code=code,
        client_id=settings.KAKAO_CLIENT_ID,
        redirect_uri=settings.KAKAO_REDIRECT_URI,
    )

    # 2. 사용자 프로필 요청
    profile = await get_kakao_profile(access_token)
    kakao_id = str(profile.get("id"))
    email = profile.get("kakao_account", {}).get("email")
    nickname = profile.get("properties", {}).get("nickname")

    # 3. DB에서 사용자 정보 확인
    result = await db.execute(
        select(User).filter_by(oauth_provider="kakao", oauth_id=kakao_id)
    )
    user = result.scalars().first()

    if not user:
        # 4. 신규 사용자 생성 (회원가입 처리)
        user = User(
            name=nickname,
            email=email,
            oauth_provider="kakao",
            oauth_id=kakao_id,
            password="",  # OAuth 사용자는 비밀번호를 저장하지 않음
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    # 5. JWT 생성
    token = create_access_token(
        data={"user_id": user.id}, expires_delta=timedelta(hours=1)
    )

    return {"user": user, "access_token": token}
