from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.answer import AnswerSheetCreate
from app.services.answer_service import AnswerService

router = APIRouter(prefix="/problems")


@router.post("/{quiz_id}/answer", status_code=status.HTTP_201_CREATED)
async def save_quiz_answers(
    quiz_id: int, answer_data: AnswerSheetCreate, db: AsyncSession = Depends(get_db)
):
    answer_service = AnswerService(db)
    return await answer_service.save_answers(quiz_id=quiz_id, answer_data=answer_data)
