from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.learning_progress import LearningProgress, LearningStatus
from typing import List, Optional

class LearningProgressRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_id(self, user_id: str, status: Optional[LearningStatus] = None) -> List[LearningProgress]:
        stmt = select(LearningProgress).where(LearningProgress.user_id == user_id)
        if status:
            stmt = stmt.where(LearningProgress.status == status)

        result = await self.db.execute(stmt)  # ✅ `execute()` 사용
        return result.scalars().all()  # ✅ 결과를 `scalars()`로 변환

    async def create(self, learning_progress: LearningProgress) -> LearningProgress:
        self.db.add(learning_progress)
        await self.db.commit()  # ✅ `commit()`도 비동기 실행
        await self.db.refresh(learning_progress)
        return learning_progress
