from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings  # ✅ 환경 변수 설정 가져오기
from app.routers import answer, answer_star, auth, grade, pages, quiz

app = FastAPI()

# ✅ SessionMiddleware 추가
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="sessionid",
    same_site="lax",
    https_only=False,
    max_age=3600,
)

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
app.include_router(quiz.router, prefix="/api/v1", tags=["quizzes"])
app.include_router(answer.router, prefix="/api/v1", tags=["answers"])
app.include_router(grade.router, prefix="/api/v1", tags=["grade"])
app.include_router(answer_star.router, prefix="/api/v1", tags=["star"])


@app.get("/")
def read_root():
    return {
        "message": "Welcome to Ticha AI Backend!",
        "ENV": settings.ENV,  # ✅ 현재 실행 중인 환경 출력
        "MYSQL_HOST": settings.MYSQL_HOST,  # ✅ 데이터베이스 호스트 정보 확인
        "DATABASE_URL": settings.DATABASE_URL,  # ✅ 실제로 FastAPI에서 사용하는 DB URL
    }


@app.on_event("startup")
async def startup_event():
    print(
        f"✅ Loaded settings: {settings.model_dump()}"
    )  # ✅ FastAPI 시작 시 환경 변수 출력
