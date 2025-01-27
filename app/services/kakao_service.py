import httpx

KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_USER_INFO_URL = "https://kapi.kakao.com/v2/user/me"


async def get_kakao_access_token(
    code: str, redirect_uri: str, client_id: str, client_secret: str
):
    """카카오 서버에서 access_token을 가져옵니다."""
    payload = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "code": code,
        "client_secret": client_secret,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(KAKAO_TOKEN_URL, data=payload)
        response.raise_for_status()
        return response.json()  # {"access_token": "...", ...}


async def get_kakao_user_info(access_token: str):
    """access_token을 이용해 카카오 사용자 정보를 가져옵니다."""
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(KAKAO_USER_INFO_URL, headers=headers)
        response.raise_for_status()
        return response.json()  # {"id": ..., "kakao_account": {...}, ...}
