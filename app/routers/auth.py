from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.kakao_auth import kakao_login  # 사용자 인증/저장 비즈니스 로직
from app.core.config import settings
from app.core.database import get_db  # 비동기 세션 주입 함수

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
        # 사용자 인증 및 JWT 발급
        result = await kakao_login(code, db)  # `db` 세션을 kakao_login 함수에 전달
        user = result["user"]
        access_token = result["access_token"]

        # 로그인 성공 시 리다이렉트
        response = RedirectResponse(url=f"/?login=success&user_id={user.id}")
        response.set_cookie(key="access_token", value=access_token, httponly=True)
        return response
    except Exception as e:
        # 로그인 실패 시 리다이렉트
        return RedirectResponse(url=f"/?error=login_failed&message={str(e)}")


@router.get("/api/protected")
async def protected_route(user_id: int = Depends(get_current_user)):
    """
    JWT 인증이 필요한 보호된 라우트
    """
    return {"message": "Access granted", "user_id": user_id}
