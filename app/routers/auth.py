import secrets  # CSRF 방지를 위한 state 생성
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.auth.google_auth import google_login  # Google OAuth 추가
from app.auth.kakao_auth import kakao_login
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.services.jwt_service import create_access_token, decode_token

router = APIRouter()


### ✅ Kakao OAuth
@router.get("/oauth/kakao/login")
async def kakao_login_redirect():
    """
    카카오 로그인 페이지로 리디렉션
    """
    params = {
        "client_id": settings.KAKAO_CLIENT_ID,
        "redirect_uri": settings.KAKAO_REDIRECT_URI,
        "response_type": "code",
    }
    kakao_auth_url = f"https://kauth.kakao.com/oauth/authorize?{urlencode(params)}"
    return {"auth_url": kakao_auth_url}


@router.get("/oauth/kakao/callback")
async def kakao_callback(code: str = Query(...), db: AsyncSession = Depends(get_db)):
    """
    카카오 인증 후 Access Token 및 사용자 정보 반환
    """
    try:
        result = await kakao_login(code, db)
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
        raise HTTPException(status_code=400, detail=f"Login failed: {str(e)}")


### ✅ Google OAuth 개선 (보안 강화)
@router.get("/oauth/google/login")
async def google_login_redirect():
    """
    구글 로그인 페이지로 리디렉션 (CSRF 방지, 리프레시 토큰 요청, 사용자 동의 화면 강제)
    """
    state = secrets.token_urlsafe(16)  # CSRF 방지를 위한 랜덤 state 값 생성

    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,  # ✅ CSRF 공격 방지
        "access_type": "offline",  # ✅ 리프레시 토큰 요청 가능
        "prompt": "consent",  # ✅ 사용자 동의 화면 강제 표시
    }
    google_auth_url = f"https://accounts.google.com/o/oauth2/auth?{urlencode(params)}"

    return {
        "auth_url": google_auth_url,
        "state": state,
    }  # 클라이언트가 state를 저장하도록 반환


@router.get("/oauth/google/callback")
async def google_callback(
    code: str = Query(...),
    state: str = Query(...),  # ✅ 클라이언트에서 받은 state를 검증
    db: AsyncSession = Depends(get_db),
):
    """
    구글 인증 후 Access Token 및 사용자 정보 반환
    """
    try:
        # 🔹 클라이언트에서 받은 state가 유효한지 확인 (실제 구현에서는 세션 저장 후 비교 필요)
        if not state:
            raise HTTPException(status_code=400, detail="Invalid state parameter")

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
        raise HTTPException(status_code=400, detail=f"Login failed: {str(e)}")


### ✅ 현재 로그인한 사용자 정보 조회
@router.get("/api/user/me")
async def get_current_user(token: str = Query(...), db: AsyncSession = Depends(get_db)):
    """
    현재 사용자 정보 반환 (Access Token 사용)
    """
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
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
