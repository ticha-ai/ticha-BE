import logging
from calendar import monthrange
from datetime import date

from fastapi import HTTPException
from sqlalchemy import extract, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.answer_sheet import AnswerSheetStatus
from app.models.quiz import Quiz
from app.models.study_log import StudyLog
from app.schemas.study_dashboard import CalendarStudyRecordsResponse, StudyRecordDay

logger = logging.getLogger(__name__)


class StudyDashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_calendar_study_records(
        self, user_id: int, year: int, month: int
    ) -> CalendarStudyRecordsResponse:

        if not (1 <= month <= 12):
            raise ValueError("월은 1에서 12 사이의 값이어야 합니다.")

        try:
            # 1. StudyLog 조회
            study_logs_query = select(StudyLog).where(
                StudyLog.user_id == user_id,
                extract("year", StudyLog.quiz_date) == year,
                extract("month", StudyLog.quiz_date) == month,
            )
            study_logs_result = await self.db.execute(study_logs_query)
            study_logs = study_logs_result.scalars().all()

            # 2. 해당 월의 Quiz 조회
            quizzes_query = (
                select(Quiz)
                .where(
                    Quiz.user_id == user_id,
                    extract("year", Quiz.created_at) == year,
                    extract("month", Quiz.created_at) == month,
                )
                .options(joinedload(Quiz.answer_sheets), joinedload(Quiz.chapter))
            )
            quizzes_result = await self.db.execute(quizzes_query)
            quizzes = quizzes_result.unique().scalars().all()

            # 날짜별 퀴즈 매핑
            quiz_by_date = {}
            for quiz in quizzes:
                date_key = quiz.created_at.date()
                if date_key not in quiz_by_date:
                    quiz_by_date[date_key] = []

                # 퀴즈의 상태 확인 - AnswerSheetStatus 사용
                if quiz.answer_sheets:
                    latest_answer_sheet = max(
                        quiz.answer_sheets, key=lambda x: x.created_at
                    )
                    status = latest_answer_sheet.status
                else:
                    status = AnswerSheetStatus.IN_PROGRESS.value

                quiz_by_date[date_key].append(
                    {
                        "quiz_id": quiz.id,
                        "title": quiz.chapter.name,  # 챕터 이름 포함
                        "status": status,
                    }
                )

            # 캘린더 데이터 구성
            calendar_data = []
            _, last_day = monthrange(year, month)

            for day in range(1, last_day + 1):
                current_date = date(year, month, day)
                # study_logs를 날짜별로 딕셔너리로 매핑
                study_log_by_date = {log.quiz_date: log for log in study_logs}

                # 딕셔너리에서 특정 날짜의 study_log를 조회
                study_log = study_log_by_date.get(current_date)
                quizzes = quiz_by_date.get(current_date, [])

                calendar_data.append(
                    StudyRecordDay(
                        date=current_date,
                        has_study=study_log is not None,
                        quizzes=quizzes,
                    )
                )

            return CalendarStudyRecordsResponse(study_records=calendar_data)
        except SQLAlchemyError as e:
            logger.error(f"데이터베이스 조회 중 오류 발생: {e}")
            raise HTTPException(
                status_code=500, detail="캘린더 기록을 조회하는 중 오류가 발생했습니다."
            )
