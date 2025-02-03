from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.routers import auth, pages, quiz

app = FastAPI()

# ✅ SessionMiddleware 추가
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,  # 세션 암호화 키
    session_cookie="sessionid",  # ✅ 세션 쿠키 이름 (고정)
    same_site="lax",  # ✅ OAuth 리디렉션 후에도 세션 유지
    https_only=False,  # ✅ HTTPS 환경에서만 작동하는 것을 방지 (테스트 환경)
    max_age=3600,  # ✅ 세션 유지 시간 (1시간)
)

# Static files
app.mount("/static", StaticFiles(directory="app/static", html=True), name="static")

# Routers
app.include_router(auth.router, tags=["auth"])  # prefix 없이 등록
app.include_router(pages.router, tags=["pages"])
app.include_router(quiz.router, prefix="/api/v1", tags=["quizzes"])


@app.get("/")
def read_root():
    return {"message": "Welcome to Ticha AI Backend!"}


# 확인용으로 settings 로그 출력
@app.on_event("startup")
async def startup_event():
    print(f"Loaded settings: {settings.dict()}")
