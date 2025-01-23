from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )

    # 환경변수 정의
    MYSQL_ROOT_PASSWORD: str
    MYSQL_DATABASE: str
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_PORT: int

    # DATABASE_URL 생성 메서드 추가
    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+asyncmy://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@localhost:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"


settings = Settings()
