import logging

import httpx

KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_USER_INFO_URL = "https://kapi.kakao.com/v2/user/me"

logger = logging.getLogger(__name__)


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
        try:
            response = await client.post(KAKAO_TOKEN_URL, data=payload)
            response.raise_for_status()
            data = response.json()

            if "access_token" not in data:
                raise ValueError("Access token not found in response")

            return {
                "access_token": data["access_token"],
                "refresh_token": data.get("refresh_token"),  # ✅ `None`일 수 있음
                "expires_in": data.get("expires_in"),
                "token_type": data.get("token_type", "bearer"),
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"Kakao token request failed: {e.response.json()}")
            raise ValueError(f"Kakao OAuth failed: {e.response.text}")

        except Exception as e:
            logger.error(f"Unexpected error in get_kakao_access_token: {e}")
            raise ValueError("Unexpected error occurred while getting Kakao token")


async def get_kakao_user_info(access_token: str):
    """카카오 액세스 토큰을 이용해 사용자 정보를 가져옵니다."""
    headers = {"Authorization": f"Bearer {access_token}"}

    # 🚨 디버깅: 실제 API 요청 전, Authorization 헤더 확인
    print("🔹 Sending Authorization Header:", headers)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(KAKAO_USER_INFO_URL, headers=headers)
            response.raise_for_status()
            data = response.json()

            # 🚨 디버깅: 카카오 API 응답 확인
            print("🔹 Kakao User Info Response:", data)

            if "id" not in data:
                raise ValueError("User ID not found in Kakao response")

            kakao_account = data.get("kakao_account", {})

            return {
                "id": data["id"],
                "nickname": kakao_account.get("profile", {}).get("nickname"),
                "profile_image": kakao_account.get("profile", {}).get(
                    "profile_image_url"
                ),
                "email": kakao_account.get("email"),
            }

        except httpx.HTTPStatusError as e:
            print(f"🔺 Kakao user info request failed: {e.response.json()}")
            raise ValueError(f"Failed to fetch Kakao user info: {e.response.text}")

        except Exception as e:
            print(f"🔺 Unexpected error in get_kakao_user_info: {e}")
            raise ValueError("Unexpected error occurred while getting Kakao user info")
