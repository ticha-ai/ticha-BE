from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.study_dashboard import (
    CalendarStudyRecordsResponse,
    InProgressAnswerSheetResponse,
)
from app.services.study_dashboard_service import StudyDashboardService

router = APIRouter()


@router.get(
    "/calendars/study-records",
    response_model=CalendarStudyRecordsResponse,
    summary="Get calendar study records",
)
async def get_calendar_study_records(
    request: Request,
    year: int = Query(..., description="Year to fetch records for"),
    month: int = Query(..., description="Month to fetch records for", ge=1, le=12),
    db: Session = Depends(get_db),
):
    """
    학습 대시보드의 캘린더 학습 기록을 조회합니다.
    - 해당 월의 모든 날짜에 대한 학습 기록 여부
    - 학습한 날의 경우 관련 퀴즈 정보 포함
    """
    try:
        user = request.state.user  # 미들웨어에서 설정된 사용자 정보
        service = StudyDashboardService(db)
        return await service.get_calendar_study_records(user.id, year, month)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch calendar study records: {str(e)}"
        )


@router.get("/answer-sheets/in-progress", response_model=InProgressAnswerSheetResponse)
async def get_in_progress_answer_sheets(
    request: Request, db: AsyncSession = Depends(get_db)
):
    """
    현재 로그인한 사용자가 진행 중인 답안지 목록을 조회합니다.
    """
    user = request.state.user
    service = StudyDashboardService(db)
    return await service.get_in_progress_answer_sheets(user.id)
