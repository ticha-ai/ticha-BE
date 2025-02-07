import logging
import secrets  # CSRF 방지를 위한 state 생성
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel
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
from app.services.kakao_service import get_kakao_access_token, get_kakao_user_info
from app.services.user_service import find_or_create_kakao_user


class KakaoTokenRequest(BaseModel):
    code: str


router = APIRouter()

# ✅ 로거 설정 (중복 적용 방지)
logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logging.basicConfig(level=logging.DEBUG)


### ✅ Kakao OAuth
### TODO: 삭제필요
@router.get("/oauth/kakao/login")
async def kakao_login_redirect():
    """카카오 로그인 URL을 JSON 응답으로 반환"""
    params = {
        "client_id": settings.KAKAO_CLIENT_ID,
        "redirect_uri": settings.KAKAO_REDIRECT_URI,
        "response_type": "code",
    }
    kakao_auth_url = f"https://kauth.kakao.com/oauth/authorize?{urlencode(params)}"

    return {"login_url": kakao_auth_url}  # ✅ JSON 응답 반환


@router.post("/oauth/kakao/token")
async def kakao_token_exchange(
    code: str = Body(
        ..., description="OAuth Authorization Code"
    ),  # ✅ `Query` → `Body`로 변경
    db: AsyncSession = Depends(get_db),
):
    """카카오 OAuth 인증 후 서비스 자체 JWT 발급"""
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code is required")

    try:
        kakao_token_response = await get_kakao_access_token(
            code=code,
            redirect_uri=settings.KAKAO_REDIRECT_URI,
            client_id=settings.KAKAO_CLIENT_ID,
            client_secret=settings.KAKAO_CLIENT_SECRET,
        )

        kakao_access_token = kakao_token_response.get("access_token")
        kakao_refresh_token = kakao_token_response.get("refresh_token")

        if not kakao_access_token:
            raise HTTPException(
                status_code=400, detail="Invalid access token from Kakao"
            )

        kakao_user_info = await get_kakao_user_info(kakao_access_token)

        user = await find_or_create_kakao_user(kakao_user_info, kakao_refresh_token, db)

        service_access_token = create_access_token(data={"user_id": user.id})
        service_refresh_token = create_refresh_token(data={"user_id": user.id})

        return {
            "access_token": service_access_token,
            "refresh_token": service_refresh_token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "profile_image": user.profile_image,
            },
            "message": "Login successful",
        }

    except Exception as e:
        logger.error(f"Kakao OAuth processing error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/oauth/kakao/callback")
async def kakao_callback(
    code: str = Query(..., description="OAuth Authorization Code"),
    db: AsyncSession = Depends(get_db),
):
    """카카오 OAuth 인증 후 JWT 발급"""
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code is required")

    try:
        # ✅ 1. 카카오 서버에서 액세스 토큰 받아오기
        kakao_token_response = await get_kakao_access_token(
            code=code,
            redirect_uri=settings.KAKAO_REDIRECT_URI,
            client_id=settings.KAKAO_CLIENT_ID,
            client_secret=settings.KAKAO_CLIENT_SECRET,
        )

        # 🚨 디버깅: 카카오에서 받은 토큰 확인
        print("🔹 Kakao Token Response:", kakao_token_response)

        # ✅ 2. 카카오 API에서 사용자 정보 가져오기
        kakao_access_token = kakao_token_response.get("access_token")
        kakao_refresh_token = kakao_token_response.get(
            "refresh_token"
        )  # ✅ `None`일 수도 있음

        if not kakao_access_token:
            raise HTTPException(
                status_code=400, detail="Failed to retrieve access token"
            )

        kakao_user_info = await get_kakao_user_info(kakao_access_token)

        # 🚨 디버깅: 사용자 정보 확인
        print("🔹 Kakao User Info:", kakao_user_info)

        # ✅ 3. 서비스 DB에서 사용자 확인 또는 신규 회원가입 처리
        user = await find_or_create_kakao_user(kakao_user_info, kakao_refresh_token, db)

        # 🚨 디버깅: 사용자 정보 확인
        print("🔹 Found or Created User:", user.id)

        # ✅ 4. 서비스 자체 JWT 발급
        service_access_token = create_access_token(data={"user_id": user.id})
        service_refresh_token = create_refresh_token(data={"user_id": user.id})

        return {
            "access_token": service_access_token,
            "refresh_token": service_refresh_token,
            "message": "Login successful",
        }

    except Exception as e:
        print(f"🔺 Error occurred: {e}")
        raise HTTPException(status_code=400, detail=str(e))


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
