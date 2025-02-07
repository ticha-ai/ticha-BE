import logging
import secrets  # CSRF 방지를 위한 state 생성
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.auth.google_auth import google_login  # Google OAuth 추가
from app.auth.kakao_auth import kakao_login
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.services.jwt_service import (
    create_access_token,
    create_refresh_token,
    decode_token,
)

router = APIRouter()

# ✅ 로거 설정 (중복 적용 방지)
logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logging.basicConfig(level=logging.DEBUG)


### ✅ Kakao OAuth
### TODO: 삭제필요
@router.get("/oauth/kakao/login")
async def kakao_login_redirect():
    """카카오 로그인 페이지로 리디렉션"""
    params = {
        "client_id": settings.KAKAO_CLIENT_ID,
        "redirect_uri": settings.KAKAO_REDIRECT_URI,
        "response_type": "code",
    }
    kakao_auth_url = f"https://kauth.kakao.com/oauth/authorize?{urlencode(params)}"
    return RedirectResponse(url=kakao_auth_url)


@router.get("/oauth/kakao/callback")
async def kakao_callback(data: dict, db: AsyncSession = Depends(get_db)):
    """
    프론트에서 받은 카카오 인가코드를 사용해 로그인 또는 회원가입 처리
    """
    code = data.get("code")  # ✅ 프론트에서 전달한 인가코드
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code is required")

    try:
        result = await kakao_login(code, db)
        user = result["user"]
        access_token = create_access_token(
            data={"user_id": user.id}, expires_delta=timedelta(minutes=30)
        )
        refresh_token = create_refresh_token(data={"user_id": user.id})

        return JSONResponse(
            content={
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                },
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
        )

    except Exception as e:
        logger.error(f"Kakao login failed: {e}")
        raise HTTPException(status_code=400, detail=f"Login failed: {str(e)}")


### ✅ Google OAuth 개선 (보안 강화)
@router.get("/oauth/google/login")
async def google_login_redirect(request: Request):
    """구글 로그인 페이지로 리디렉션"""

    state = secrets.token_urlsafe(32)  # ✅ state 값 생성
    request.session["oauth_state"] = {
        "value": state,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    logger.debug(f"Generated state: {state}")
    logger.debug(f"Session stored state: {request.session.get('oauth_state')}")

    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "consent",
    }
    google_auth_url = f"https://accounts.google.com/o/oauth2/auth?{urlencode(params)}"

    return RedirectResponse(url=google_auth_url)


@router.get("/oauth/google/callback")
async def google_callback(
    request: Request,
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db),
):
    """Google OAuth 인증 후 Access Token 및 사용자 정보 반환"""
    try:
        logger.debug(f"Received state from client: {state}")
        stored_state = request.session.pop("oauth_state", None)  # ✅ pop으로 제거

        if not stored_state:
            logger.error("No state found in session")
            raise HTTPException(status_code=400, detail="Invalid state parameter")

        if stored_state["value"] != state:
            logger.error(
                f"State mismatch! Stored: {stored_state['value']}, Received: {state}"
            )
            raise HTTPException(status_code=400, detail="Invalid state parameter")

        # ✅ State 생성 시간 검증 (10분 초과 시 만료)
        created_at = datetime.fromisoformat(stored_state["created_at"])
        now = datetime.now(timezone.utc)

        if now - created_at > timedelta(minutes=10):
            logger.error("State expired!")
            raise HTTPException(status_code=400, detail="State parameter expired")

        # ✅ Google OAuth 로그인 처리
        result = await google_login(code, db)
        user = result["user"]
        access_token = result["access_token"]
        refresh_token = result["refresh_token"]

        return {
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
            },
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    except Exception as e:
        logger.error(f"Google login failed: {e}")
        raise HTTPException(status_code=400, detail=f"Login failed: {str(e)}") from e


### ✅ 현재 로그인한 사용자 정보 조회
@router.get("/api/user/me")
async def get_current_user(token: str = Query(...), db: AsyncSession = Depends(get_db)):
    """현재 사용자 정보 반환 (Access Token 사용)"""
    try:
        payload = decode_token(token)
        user_id = payload.get("user_id")

        result = await db.execute(select(User).filter_by(id=user_id))
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        }
    except Exception as e:
        logger.error(f"Token validation failed: {e}")
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
