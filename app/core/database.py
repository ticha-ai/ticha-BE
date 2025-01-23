from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# SQLAlchemy
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# 세션 생성
async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


# 의존성 주입
async def get_db():
    async with async_session() as session:
        yield session
