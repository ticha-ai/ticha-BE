from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select  # 추가

from app.auth.kakao_auth import kakao_login
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User  # 추가
from app.services.jwt_service import create_access_token, decode_token

router = APIRouter()


@router.get("/oauth/kakao/login")
async def kakao_login_redirect():
    """
    카카오 로그인 페이지로 리디렉션
    """
    params = {
        "client_id": settings.KAKAO_CLIENT_ID,
        "redirect_uri": settings.KAKAO_REDIRECT_URI,
        "response_type": "code",
    }
    kakao_auth_url = f"https://kauth.kakao.com/oauth/authorize?{urlencode(params)}"
    return {"auth_url": kakao_auth_url}


@router.get("/oauth/kakao/callback")
async def kakao_callback(code: str = Query(...), db: AsyncSession = Depends(get_db)):
    """
    카카오 인증 후 Access Token 및 사용자 정보 반환
    """
    try:
        result = await kakao_login(code, db)
        user = result["user"]
        access_token = result["access_token"]
        refresh_token = result["refresh_token"]

        return {
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
            },
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Login failed: {str(e)}")


@router.get("/api/user/me")
async def get_current_user(token: str = Query(...), db: AsyncSession = Depends(get_db)):
    """
    현재 사용자 정보 반환 (Access Token 사용)
    """
    try:
        payload = decode_token(token)
        user_id = payload.get("user_id")

        result = await db.execute(
            select(User).filter_by(id=user_id)
        )  # 수정: User 모델 사용
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
