import logging
from typing import List

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.future import select

from app.core.database import get_db
from app.models.user import User
from app.services.jwt_service import decode_token

logger = logging.getLogger(__name__)

# 인증이 필요 없는 public 경로들
PUBLIC_PATHS: List[str] = [
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/oauth/kakao/login",
    "/oauth/kakao/token",
    "/oauth/kakao/callback",
    "/oauth/google/login",
    "/oauth/google/callback",
    "/index",
    "/login",
]


async def auth_middleware(request: Request, call_next):
    """인증 미들웨어"""

    # public 경로 체크
    if any(request.url.path.startswith(path) for path in PUBLIC_PATHS):
        return await call_next(request)

    try:
        # Authorization 헤더 검증
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(status_code=401, detail="No authorization header")

        # Bearer 접두사가 있으면 제거
        token = auth_header.replace("Bearer ", "")

        # 토큰 검증 및 디코딩
        payload = decode_token(token)
        user_id = payload.get("user_id")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        # DB에서 사용자 조회
        async for db in get_db():
            result = await db.execute(select(User).filter(User.id == user_id))
            user = result.scalars().first()

            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            request.state.user = user
            break

        response = await call_next(request)
        return response

    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")  # 예상치 못한 에러 로깅
        return JSONResponse(
            status_code=401,
            content={"detail": f"Could not validate credentials: {str(e)}"},
        )
