from datetime import timedelta
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.auth.kakao_auth import kakao_login
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
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
    return RedirectResponse(kakao_auth_url)


@router.get("/oauth/kakao/callback")
async def kakao_callback(code: str, db: AsyncSession = Depends(get_db)):
    """
    카카오 로그인 처리 및 JWT 반환
    """
    try:
        result = await kakao_login(code, db)
        user = result["user"]
        access_token = result["access_token"]

        response = RedirectResponse(url=f"/?login=success&user_id={user.id}")
        response.set_cookie(key="access_token", value=access_token, httponly=True)
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Login failed: {str(e)}")


@router.post("/api/token/refresh")
async def refresh_access_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    """
    Refresh Token을 사용하여 Access Token 갱신
    """
    try:
        # Refresh Token 디코딩 및 검증
        payload = decode_token(refresh_token)
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        # DB에서 사용자 확인
        result = await db.execute(select(User).filter_by(id=user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user.refresh_token != refresh_token:
            raise HTTPException(
                status_code=401, detail="Invalid or expired refresh token"
            )

        # 새로운 Access Token 생성
        access_token = create_access_token(
            data={"user_id": user.id}, expires_delta=timedelta(minutes=30)
        )
        return {"access_token": access_token}

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
