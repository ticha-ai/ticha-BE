from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBearer
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings  # ✅ 환경 변수 설정 가져오기
from app.core.public_routes import PublicRoute
from app.middleware.auth_middleware import auth_middleware
from app.routers import (
    answer,
    answer_star,
    auth,
    basic_auth,
    grade,
    pages,
    quiz,
    study_dashboard,
)

# security_scheme 정의
security_scheme = HTTPBearer(description="JWT 토큰을 입력하세요.")

app = FastAPI()


# OpenAPI 스키마에 보안 정의 추가
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # 보안 스키마 추가
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT 토큰을 입력하세요.",
        }
    }

    # PublicRoute Enum 값들을 사용
    public_paths = [route.value for route in PublicRoute]

    for endpoint_path in openapi_schema["paths"].keys():
        path_item = openapi_schema["paths"][endpoint_path]
        for method in path_item.values():
            if endpoint_path not in public_paths:
                method["security"] = [{"Bearer": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# ✅ SessionMiddleware 추가
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="sessionid",
    same_site="lax",
    https_only=False,
    max_age=3600,
)

app.middleware("http")(auth_middleware)

# ✅ CORS 미들웨어 추가 (모든 도메인 허용)
# TODO: 배포 시에 도메인을 명시적으로 설정해야 함
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory="app/static", html=True), name="static")

# Routers
app.include_router(auth.router, tags=["auth"])
app.include_router(pages.router, tags=["pages"])
app.include_router(basic_auth.router, prefix="/api/v1", tags=["basic-auth"])
app.include_router(quiz.router, prefix="/api/v1", tags=["quizzes"])
app.include_router(answer.router, prefix="/api/v1", tags=["answers"])
app.include_router(grade.router, prefix="/api/v1", tags=["grade"])
app.include_router(answer_star.router, prefix="/api/v1", tags=["star"])
app.include_router(study_dashboard.router, prefix="/api/v1", tags=["study-dashboard"])
