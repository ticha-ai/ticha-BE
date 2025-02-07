import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import User

logger = logging.getLogger(__name__)


async def find_or_create_kakao_user(
    kakao_user_info: dict, kakao_refresh_token: str | None, db: AsyncSession
):
    """
    카카오 OAuth 사용자를 찾거나, 없으면 새로 생성하며, refresh_token을 저장함.
    """
    kakao_id = str(kakao_user_info["id"])
    email = kakao_user_info.get("kakao_account", {}).get("email")
    nickname = (
        kakao_user_info.get("kakao_account", {}).get("profile", {}).get("nickname")
    )
    profile_image = (
        kakao_user_info.get("kakao_account", {})
        .get("profile", {})
        .get("profile_image_url")
    )

    if not kakao_id:
        raise ValueError("Kakao user ID is required")

    try:
        result = await db.execute(
            select(User).filter_by(oauth_provider="kakao", oauth_id=kakao_id)
        )
        user = result.scalars().first()

        if user:
            print(f"🔹 Existing Kakao User Found: {user.id}")
            user.last_login_at = datetime.utcnow()

            # ✅ `refresh_token`이 제공될 경우에만 업데이트 (기존 값 유지)
            if kakao_refresh_token:
                user.refresh_token = kakao_refresh_token

            await db.commit()
            return user

        # ✅ 신규 사용자 생성
        new_user = User(
            name=nickname or f"KakaoUser_{kakao_id}",
            email=email,
            oauth_provider="kakao",
            oauth_id=kakao_id,
            profile_image=profile_image,
            refresh_token=kakao_refresh_token,  # ✅ 신규 사용자도 refresh_token 저장
            last_login_at=datetime.utcnow(),
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        print(f"🔹 New Kakao User Created: {new_user.id}")
        return new_user

    except Exception as e:
        print(f"🔺 Kakao User Save Error: {e}")
        await db.rollback()
        raise ValueError("Failed to create or find Kakao user")
