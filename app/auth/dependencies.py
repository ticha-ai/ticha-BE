from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.services.jwt_service import decode_access_token

# HTTPBearer를 사용하여 Authorization 헤더에서 JWT를 추출
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    JWT를 통해 현재 사용자 인증
    """
    token = credentials.credentials  # Authorization 헤더에서 토큰 추출
    try:
        # JWT 디코딩 및 검증
        payload = decode_access_token(token)
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=401, detail="Invalid authentication credentials"
            )
        return user_id
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
