import httpx

from app.core.config import settings  # Assuming settings is defined in app.config


async def get_kakao_access_token(code: str, client_id: str, redirect_uri: str) -> str:
    """
    카카오 로그인에서 액세스 토큰 요청
    """
    token_url = "https://kauth.kakao.com/oauth/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "code": code,
        "client_secret": settings.KAKAO_CLIENT_SECRET,  # 🔹 추가된 부분
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, headers=headers, data=data)
        if response.status_code == 200:
            return response.json().get("access_token")
        raise ValueError("Failed to get access token")


async def get_kakao_profile(access_token: str) -> dict:
    """
    카카오 사용자 프로필 요청
    """
    profile_url = "https://kapi.kakao.com/v2/user/me"
    headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(profile_url, headers=headers)
        if response.status_code == 200:
            return response.json()
        response.raise_for_status()
