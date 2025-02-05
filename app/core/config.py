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

    # ✅ MySQL 환경 변수
    MYSQL_ROOT_PASSWORD: str
    MYSQL_DATABASE: str
    MYSQL_USER: str
    MYSQL_PASSWORD: str

    # ✅ MySQL 포트 & 호스트 설정 (환경에 따라 자동 변경)
    MYSQL_PORT: int = (
        3309 if ENV == "development" else 3306
    )  # 로컬(Docker)은 3309, 배포(RDS)는 3306

    MYSQL_HOST: str = (
        "host.docker.internal" if ENV == "development" else os.getenv("MYSQL_HOST")
    )  # 로컬은 Docker 내부 접근, 배포는 RDS 주소 사용

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
