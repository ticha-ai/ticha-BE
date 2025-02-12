from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.answer_star import StarredProblemsResponse, StarUpdate
from app.services.answer_star_service import get_starred_problems, update_star_status

router = APIRouter(prefix="/answers")


@router.post(
    "/{answer_sheet_id}/problems/{problem_id}/star", status_code=status.HTTP_200_OK
)
async def update_star_status_endpoint(
    answer_sheet_id: int,
    problem_id: int,
    star_update: StarUpdate,
    db: AsyncSession = Depends(get_db),
):
    await update_star_status(db, answer_sheet_id, problem_id, star_update.is_starred)
    return {"message": "별표 상태가 성공적으로 업데이트되었습니다."}


@router.get(
    "/{answersheet_id}/star",
    response_model=StarredProblemsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_starred_problems_endpoint(
    answersheet_id: int,
    db: AsyncSession = Depends(get_db),
):
    starred_problems = await get_starred_problems(db, answersheet_id)
    return {"starred_problems": starred_problems}
