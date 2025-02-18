from enum import Enum


class PublicRoute(Enum):
    # Auth 관련
    LOGIN = "/api/v1/auth/login"
    REGISTER = "/api/v1/auth/register"

    # OAuth 관련
    KAKAO_LOGIN = "/oauth/kakao/login"
    KAKAO_TOKEN = "/oauth/kakao/token"
    KAKAO_CALLBACK = "/oauth/kakao/callback"
    GOOGLE_LOGIN = "/oauth/google/login"
    GOOGLE_CALLBACK = "/oauth/google/callback"

    # Docs 관련
    SWAGGER = "/docs"
    OPENAPI = "/openapi.json"
    REDOC = "/redoc"

    # Pages
    INDEX = "/index"
    LOGIN_PAGE = "/login"


def is_public_path(path: str) -> bool:
    """정확한 경로 매칭을 통해 public 경로 여부 확인"""
    return path in [route.value for route in PublicRoute]
