from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.services.jwt_service import decode_access_token

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    JWT를 통해 현재 사용자 인증
    """
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
        return payload.get("user_id")
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
