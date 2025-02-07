import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import User

logger = logging.getLogger(__name__)


async def find_or_create_kakao_user(
    kakao_user_info: dict, kakao_refresh_token: str, db: AsyncSession
):
    """
    카카오 OAuth 사용자를 찾거나, 없으면 새로 생성하며, refresh_token을 저장함.
    """
    kakao_id = str(kakao_user_info["id"])
    email = kakao_user_info.get("email")
    nickname = kakao_user_info.get("nickname")
    profile_image = kakao_user_info.get("profile_image")  # ✅ DB에는 저장하지 않음

    if not kakao_id:
        raise ValueError("Kakao user ID is required")

    try:
        result = await db.execute(
            select(User).filter_by(oauth_provider="kakao", oauth_id=kakao_id)
        )
        user = result.scalars().first()

        if user:
            print(f"🔹 Existing Kakao User Found: {user.id}")
            user.refresh_token = (
                kakao_refresh_token  # ✅ 기존 사용자도 refresh_token 갱신
            )
            user.last_login_at = datetime.utcnow()
            await db.commit()

        else:
            # ✅ 신규 사용자 생성 (profile_image는 저장하지 않음)
            user = User(
                name=nickname or f"KakaoUser_{kakao_id}",
                email=email,
                oauth_provider="kakao",
                oauth_id=kakao_id,
                refresh_token=kakao_refresh_token,  # ✅ 신규 사용자도 refresh_token 저장
                last_login_at=datetime.utcnow(),
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)

            print(f"🔹 New Kakao User Created: {user.id}")

        # ✅ User 객체에 profile_image 속성을 동적으로 추가 (DB에는 저장하지 않음)
        setattr(user, "profile_image", profile_image)

        return user

    except Exception as e:
        print(f"🔺 Kakao User Save Error: {e}")
        await db.rollback()
        raise ValueError("Failed to create or find Kakao user")
