import logging
from typing import Any, Dict, List

from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import ValidationError
from app.models import AnswerSheet, Quiz, UserAnswer
from app.models.answer_sheet import AnswerSheetStatus
from app.schemas.answer import AnswerCreate, AnswerSheetCreate

logger = logging.getLogger(__name__)


class AnswerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_answers(
        self, quiz_id: int, answer_data: AnswerSheetCreate
    ) -> Dict[str, Any]:
        """
        특정 사용자의 문제지 답안을 저장하는 API
        """
        try:
            logger.info(
                f"Starting to save answers for quiz {quiz_id} "
                f"from user {answer_data.user_id}"
            )

            async with self.db.begin():
                # 1. 퀴즈 유효성 검증
                quiz = await self._validate_quiz(quiz_id, answer_data.user_id)
                logger.debug(f"Quiz {quiz_id} validated successfully")

                # 2. AnswerSheet 업데이트 또는 생성
                answer_sheet = await self._upsert_answer_sheet(
                    quiz_id, answer_data.user_id, answer_data.passed_time
                )
                logger.debug(
                    f"Answer sheet {'updated' if answer_sheet.id else 'created'} "
                    f"with ID {answer_sheet.id}"
                )

                # 3. 답변 저장
                await self._save_user_answers(answer_sheet.id, answer_data.answers)
                logger.debug(f"Saved {len(answer_data.answers)} answers successfully")

                return {
                    "success": True,
                    "data": {"answer_sheet_id": answer_sheet.id},
                    "message": "Answers saved successfully",
                }

        except ValidationError as ve:
            logger.error(f"Validation error: {ve.detail}")
            raise ve
        except SQLAlchemyError as e:
            logger.error(f"Database error while saving answers: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "DATABASE_ERROR",
                    "message": "A database error occurred while saving answers.",
                },
            )
        except Exception as e:
            logger.error(f"Unexpected error while saving answers: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "SERVER_ERROR",
                    "message": "An unexpected error occurred while saving answers.",
                },
            )

    async def _validate_quiz(self, quiz_id: int, user_id: int) -> Quiz:
        """Validate quiz existence and status(in_progress)."""
        query = select(Quiz).where(
            Quiz.id == quiz_id,
            Quiz.user_id == user_id,
            Quiz.status == AnswerSheetStatus.IN_PROGRESS.value,
        )
        result = await self.db.execute(query)
        quiz = result.scalar_one_or_none()

        if not quiz:
            logger.error(
                f"Quiz not found or not in progress. "
                f"Quiz ID: {quiz_id}, User ID: {user_id}"
            )
            raise ValidationError(
                code="INVALID_QUIZ",
                message="Quiz not found or not in progress",
                details={
                    "quiz_id": f"Quiz {quiz_id} is either invalid or not in progress"
                },
            )
        return quiz

    async def _upsert_answer_sheet(
        self, quiz_id: int, user_id: int, passed_time: float
    ) -> AnswerSheet:
        """Update existing answer sheet or create new one."""
        query = select(AnswerSheet).where(
            AnswerSheet.quiz_id == quiz_id, AnswerSheet.user_id == user_id
        )
        result = await self.db.execute(query)
        answer_sheet = result.scalar_one_or_none()

        try:
            if answer_sheet:
                stmt = (
                    update(AnswerSheet)
                    .where(AnswerSheet.id == answer_sheet.id)
                    .values(passed_time=int(passed_time))
                )
                await self.db.execute(stmt)
                await self.db.refresh(answer_sheet)
                logger.debug(f"Updated answer sheet {answer_sheet.id}")
            else:
                answer_sheet = AnswerSheet(
                    quiz_id=quiz_id,
                    user_id=user_id,
                    passed_time=int(passed_time),
                    status=AnswerSheetStatus.IN_PROGRESS.value,
                )
                self.db.add(answer_sheet)
                await self.db.flush()
                logger.debug("Created new answer sheet")

            return answer_sheet

        except SQLAlchemyError as e:
            logger.error(f"Database error in answer sheet upsert: {e}", exc_info=True)
            raise

    async def _save_user_answers(
        self, answer_sheet_id: int, answers: List[AnswerCreate]
    ) -> None:
        """Save or update user answers."""
        try:
            for answer in answers:
                stmt = (
                    update(UserAnswer)
                    .where(
                        UserAnswer.answer_sheet_id == answer_sheet_id,
                        UserAnswer.problem_id == answer.problem_id,
                    )
                    .values(
                        user_answer=answer.selected_option,
                        is_starred=answer.is_starred,
                        has_answer=answer.selected_option is not None,
                    )
                )
                result = await self.db.execute(stmt)

                if result.rowcount == 0:
                    new_answer = UserAnswer(
                        answer_sheet_id=answer_sheet_id,
                        problem_id=answer.problem_id,
                        user_answer=answer.selected_option,
                        is_starred=answer.is_starred,
                        has_answer=answer.selected_option is not None,
                    )
                    self.db.add(new_answer)
                    logger.debug(f"Created new answer for problem {answer.problem_id}")
                else:
                    logger.debug(f"Updated answer for problem {answer.problem_id}")

        except SQLAlchemyError as e:
            logger.error(f"Database error in saving answers: {e}", exc_info=True)
            raise

    async def get_answer_sheet_by_id(self, answersheet_id: int) -> AnswerSheet:
        query = (
            select(AnswerSheet)
            .options(selectinload(AnswerSheet.user_answers))
            .where(AnswerSheet.id == answersheet_id)
        )

        result = await self.db.execute(query)
        answer_sheet = result.scalar_one_or_none()
        if not answer_sheet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Answer sheet not found"
            )
        return answer_sheet
