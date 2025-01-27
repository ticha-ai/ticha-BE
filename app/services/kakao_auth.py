import httpx

from app.core.config import settings


async def get_kakao_access_token(code: str) -> str:
    """
    카카오 로그인에서 액세스 토큰 요청
    """
    token_url = "https://kauth.kakao.com/oauth/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "authorization_code",
        "client_id": settings.KAKAO_CLIENT_ID,  # 환경 변수 사용
        "redirect_uri": settings.KAKAO_REDIRECT_URI,  # 환경 변수에서 리다이렉트 URL 사용
        "code": code,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, headers=headers, data=data)
        if response.status_code == 200:
            return response.json().get("access_token")
    return None


async def get_kakao_profile(access_token: str) -> dict:
    """
    카카오 프로필 정보 요청
    """
    profile_url = "https://kapi.kakao.com/v2/user/me"
    headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(profile_url, headers=headers)
        if response.status_code == 200:
            return response.json()
    return {}
