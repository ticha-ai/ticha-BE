from sqlalchemy.orm import Session

from app.models.learning_progress import LearningStatus
from app.repositories.learning_progress_repository import LearningProgressRepository


class LearningProgressService:
    def __init__(self, db: Session):
        self.repository = LearningProgressRepository(db)

    async def get_learning_progress(self, user_id: str, status: LearningStatus = None):
        return await self.repository.get_by_user_id(user_id, status)
