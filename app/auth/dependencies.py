import logging

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.services.jwt_service import decode_token

security = HTTPBearer()
logger = logging.getLogger(__name__)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    JWT를 통해 현재 사용자 인증
    """
    token = credentials.credentials
    try:
        payload = decode_token(token)
        logger.info(f"Decoded JWT Payload: {payload}")  # ✅ 디코딩된 JWT 정보 로그 추가
        user_id = payload.get("user_id")

        if not isinstance(user_id, int):  # ✅ user_id가 정수인지 확인
            raise ValueError("Invalid user_id format in token")

        return {"user_id": user_id}  # ✅ 항상 딕셔너리를 반환하도록 수정
    except ValueError as e:
        logger.error(f"JWT Decode Error: {e}")  # ✅ 에러 로그 추가
        raise HTTPException(status_code=401, detail=str(e))
