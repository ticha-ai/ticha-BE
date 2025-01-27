from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.routers import auth, pages

app = FastAPI()

# Static files
app.mount("/static", StaticFiles(directory="app/static", html=True), name="static")

# Routers
app.include_router(auth.router, tags=["auth"])  # prefix 없이 등록
app.include_router(pages.router, tags=["pages"])


@app.get("/")
def read_root():
    return {"message": "Welcome to Ticha AI Backend!"}


# 확인용으로 settings 로그 출력
@app.on_event("startup")
async def startup_event():
    print(f"Loaded settings: {settings.dict()}")
