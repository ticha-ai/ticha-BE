import logging

import httpx

from app.core.config import settings  # Assuming settings is defined in app.config

logger = logging.getLogger(__name__)


async def get_kakao_access_token(code: str, client_id: str, redirect_uri: str) -> str:
    """
    카카오 로그인에서 액세스 토큰 요청
    """
    token_url = "https://kauth.kakao.com/oauth/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    # ✅ client_secret이 존재하면 포함
    data = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "code": code,
    }

    if settings.KAKAO_CLIENT_SECRET:  # ✅ client_secret이 설정된 경우에만 추가
        data["client_secret"] = settings.KAKAO_CLIENT_SECRET

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, headers=headers, data=data)

        logger.debug(f"Kakao Token Request Data: {data}")  # ✅ 요청 데이터 로깅
        logger.debug(f"Kakao Token Response Status: {response.status_code}")
        logger.debug(f"Kakao Token Response Body: {response.text}")

        if response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to get access token: {response.text}",
            )

        token_data = response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            raise HTTPException(
                status_code=400,
                detail=f"Access token not found in response: {token_data}",
            )

        return access_token

    except httpx.RequestError as e:
        logger.error(f"HTTP request error while getting Kakao token: {str(e)}")
        raise HTTPException(status_code=500, detail="Kakao login request failed")


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
