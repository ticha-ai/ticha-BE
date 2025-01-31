import aiohttp
import requests
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.user import User
from app.services.jwt_service import create_access_token, create_refresh_token


async def google_login(code: str, db: AsyncSession):
    """
    Google OAuth 인증 후 사용자 정보 반환
    """
    try:
        # 1️⃣ Access Token 요청
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "code": code,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, data=token_data) as resp:
                token_json = await resp.json()

        if "access_token" not in token_json:
            raise Exception("Failed to retrieve access token")

        access_token = token_json["access_token"]

        # 2️⃣ 사용자 정보 요청
        user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        async with session.get(
            user_info_url, headers={"Authorization": f"Bearer {access_token}"}
        ) as resp:
            user_data = await resp.json()

        # 3️⃣ 사용자 정보 확인 및 저장
        email = user_data.get("email")
        name = user_data.get("name")

        # 데이터베이스에서 사용자 확인 또는 생성
        result = await db.execute(select(User).filter(User.email == email))
        user = result.scalars().first()

        if not user:
            user = User(
                email=email,
                name=name,
                password="OAUTH_USER",  # ✅ 기본값 추가 (NULL 방지)
                oauth_provider="google",
                oauth_id=user_data.get("id"),
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)

        # 4️⃣ JWT 토큰 생성
        access_token = create_access_token({"user_id": user.id})
        refresh_token = create_refresh_token({"user_id": user.id})

        return {
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    except Exception as e:
        raise Exception(f"Google OAuth error: {str(e)}")
