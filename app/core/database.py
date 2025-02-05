from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# ✅ SQLAlchemy 비동기 엔진 생성 (RDS에 최적화)
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    pool_recycle=1800,  # 30분마다 연결 재설정 (타임아웃 방지)
    pool_pre_ping=True,  # 끊어진 연결 자동 복구
    connect_args={"charset": "utf8mb4"},  # UTF-8 지원
)

# ✅ 세션 생성
async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


# ✅ 의존성 주입
async def get_db():
    async with async_session() as session:
        yield session
