from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.kakao_auth import kakao_login
from app.core.config import settings
from app.core.database import get_db

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
