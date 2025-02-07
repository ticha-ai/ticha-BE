from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.answer import AnswerSheetCreate, AnswerSheetResponse
from app.services.answer_service import AnswerService

router = APIRouter(prefix="/problems")


@router.post("/{quiz_id}/answer", status_code=status.HTTP_201_CREATED)
async def save_quiz_answers(
    quiz_id: int, answer_data: AnswerSheetCreate, db: AsyncSession = Depends(get_db)
):
    answer_service = AnswerService(db)
    return await answer_service.save_answers(quiz_id=quiz_id, answer_data=answer_data)


@router.get("/answers/{answersheet_id}", response_model=AnswerSheetResponse)
async def get_answer_sheet(
    answersheet_id: int,
    db: AsyncSession = Depends(get_db),
):
    answer_service = AnswerService(db)
    answer_sheet = await answer_service.get_answer_sheet_by_id(answersheet_id)

    # TODO) 사용자 본인의 퀴즈 풀이 답안만 확인할 수 있게 인증 체크

    return answer_sheet
