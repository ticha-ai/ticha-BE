from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.grade import GradeRequest
from app.services import grade_service

router = APIRouter(prefix="/problems/answers")


@router.post("/{answersheet_id}/grade", status_code=status.HTTP_201_CREATED)
async def grade_quiz(
    answersheet_id: int,
    grade_request: GradeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # TODO) 실제 현재 사용자 정보 가져오는 로직 추가

    result = await grade_service.grade_answer_sheet(
        answersheet_id, db, current_user, grade_request.answers
    )

    if not result:
        raise HTTPException(status_code=404, detail="답안지를 찾을 수 없습니다.")

    return result
