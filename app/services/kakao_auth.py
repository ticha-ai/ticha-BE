import httpx


async def get_kakao_access_token(code: str, client_id: str, redirect_uri: str) -> str:
    """
    카카오로부터 액세스 토큰을 요청
    """
    token_url = "https://kauth.kakao.com/oauth/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "code": code,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, headers=headers, data=data)
        if response.status_code == 200:
            return response.json().get("access_token")
        response.raise_for_status()


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
