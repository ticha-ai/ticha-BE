from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.models.learning_progress import LearningStatus
from app.schemas.learning_progress_schema import LearningProgressResponse
from app.services.learning_progress_service import LearningProgressService

router = APIRouter()


@router.get("/users/{user_id}/quizzes", response_model=List[LearningProgressResponse])
async def get_learning_progress(
    user_id: int,
    status: Optional[LearningStatus] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    service = LearningProgressService(db)
    progress_data = await service.get_learning_progress(user_id, status)

    if not progress_data:
        raise HTTPException(status_code=404, detail="DATA_NOT_FOUND")

    return progress_data
