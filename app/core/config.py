import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# ✅ .env 파일 자동 로드
load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )

    # 환경 설정 (default: development)
    ENV: str = os.getenv("ENV", "development")

    # MySQL 환경 변수
    MYSQL_ROOT_PASSWORD: str
    MYSQL_DATABASE: str
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_PORT: int
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "127.0.0.1")  # 기본값: 로컬

    # 카카오 API 환경 변수
    KAKAO_CLIENT_ID: str
    KAKAO_CLIENT_SECRET: str
    KAKAO_REDIRECT_URI: str

    # 구글 API 환경 변수
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    # JWT 환경 변수
    SECRET_KEY: str
    ALGORITHM: str

    # DATABASE_URL 생성 메서드
    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+asyncmy://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"


settings = Settings()
