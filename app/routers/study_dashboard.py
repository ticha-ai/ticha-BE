from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.study_dashboard import (
    CalendarStudyRecordsResponse,
    ChapterStatisticsResponse,
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

    Args:
        request (Request): 사용자 정보가 포함된 요청 객체
        year (int): 조회할 연도
        month (int): 조회할 월 (1-12)

    Returns:
        CalendarStudyRecordsResponse: 캘린더 학습 기록
    """
    try:
        user = request.state.user
        service = StudyDashboardService(db)
        return await service.get_calendar_study_records(user.id, year, month)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"캘린더 학습 기록을 조회하는 중 오류가 발생했습니다: {str(e)}",
        )


@router.get("/answer-sheets/in-progress", response_model=InProgressAnswerSheetResponse)
async def get_in_progress_answer_sheets(
    request: Request, db: AsyncSession = Depends(get_db)
):
    """
    현재 로그인한 사용자가 진행 중인 답안지 목록을 조회합니다.
    - 진행 중인 답안지의 진행률, 학습일, 퀴즈 제목 포함

    Args:
        request (Request): 사용자 정보가 포함된 요청 객체
        db (AsyncSession): 데이터베이스 세션

    Returns:
        InProgressAnswerSheetResponse: 진행 중인 답안지 목록
            - answer_sheet_id (int): 답안지 ID
            - quiz_title (str): 퀴즈 제목
            - progress_rate (float): 진행률
            - study_date (date): 학습일
    """
    try:
        user = request.state.user
        service = StudyDashboardService(db)
        return await service.get_in_progress_answer_sheets(user.id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"진행 중인 답안지를 조회하는 중 오류가 발생했습니다: {str(e)}",
        ) from e


@router.get("/chapters/statistics", response_model=ChapterStatisticsResponse)
async def get_chapter_statistics(request: Request, db: AsyncSession = Depends(get_db)):

    try:
        user = request.state.user
        service = StudyDashboardService(db)
        return await service.get_chapter_statistics(user.id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"단원 통계를 조회하는 중 오류가 발생했습니다: {str(e)}",
        ) from e
