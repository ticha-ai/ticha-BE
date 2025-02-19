from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.grade import GradeRequest, GradingResultResponse
from app.services import grade_service

router = APIRouter(prefix="/answers")


@router.post("/{answersheet_id}/grade", status_code=status.HTTP_201_CREATED)
async def grade_quiz(
    request: Request,
    answersheet_id: int,
    grade_request: GradeRequest,
    db: AsyncSession = Depends(get_db),
):

    result = await grade_service.grade_answer_sheet(
        answer_sheet_id=answersheet_id,
        db=db,
        answers=grade_request.answers,
        user_id=request.state.user.id,
    )

    if not result:
        raise HTTPException(status_code=404, detail="답안지를 찾을 수 없습니다.")

    return result


@router.get(
    "/{answersheet_id}/grade",
    response_model=GradingResultResponse,
    status_code=status.HTTP_200_OK,
)
async def get_grading_results_api(
    answersheet_id: int,
    page: int = Query(1, ge=1),  # 기본값은 1페이지부터 시작
    page_size: int = Query(6, ge=1),  # 기본값은 한 페이지에 6개 표시
    db: AsyncSession = Depends(get_db),
):
    results = await grade_service.get_grading_results_with_pagination(
        answersheet_id, page, page_size, db
    )

    if not results:
        raise HTTPException(status_code=404, detail="채점 결과를 찾을 수 없습니다.")

    return results
