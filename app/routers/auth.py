from urllib.parse import urlencode

from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from app.core.config import settings
from app.services.kakao_auth import get_kakao_access_token, get_kakao_profile

router = APIRouter()


@router.get("/oauth/kakao/login")
async def kakao_login():
    """
    카카오 로그인 페이지로 리디렉션
    """
    params = {
        "client_id": settings.KAKAO_CLIENT_ID,
        "redirect_uri": settings.KAKAO_REDIRECT_URI,  # 환경 변수에서 리다이렉트 URL 사용
        "response_type": "code",
    }
    kakao_auth_url = f"https://kauth.kakao.com/oauth/authorize?{urlencode(params)}"
    return RedirectResponse(kakao_auth_url)


@router.get("/oauth/kakao/callback")
async def kakao_callback(code: str):
    """
    카카오 로그인 처리
    """
    access_token = await get_kakao_access_token(code)
    if not access_token:
        return RedirectResponse(url="/?error=login_failed")
    profile = await get_kakao_profile(access_token)
    return RedirectResponse(url="/?login=success")
