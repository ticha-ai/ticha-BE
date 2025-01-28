import logging

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.exceptions import ValidationError
from app.models.chapter import Chapter
from app.models.quiz import Quiz
from app.schemas.quiz import QuizCreateRequest

logger = logging.getLogger(__name__)

ALLOWED_DIFFICULTY = {"easy", "medium", "hard", "random"}
ALLOWED_PROBLEM_COUNTS = {5, 10, 20, 30}


async def create_quiz(
    db: AsyncSession, quiz_in: QuizCreateRequest, current_user: dict
) -> Quiz:
    try:
        logger.info("Starting quiz creation")

        # Chapter 존재 여부 확인
        result = await db.execute(
            select(Chapter).where(Chapter.id == quiz_in.chapter_id)
        )
        chapter = result.scalars().first()
        if not chapter:
            logger.error(f"Chapter with id {quiz_in.chapter_id} does not exist")
            raise ValidationError(
                code="INVALID_CHAPTER_ID",
                message=f"Chapter with ID {quiz_in.chapter_id} does not exist.",
                details={"chapter_id": f"Chapter ID {quiz_in.chapter_id} is invalid"},
            )

        # 문제 수 유효성 검사
        if quiz_in.question_count not in ALLOWED_PROBLEM_COUNTS:
            logger.error(f"Invalid question count: {quiz_in.question_count}")
            raise ValidationError(
                code="INVALID_QUESTION_COUNT",
                message="Invalid question count.",
                details={
                    "question_count": f"Must be one of {ALLOWED_PROBLEM_COUNTS}.",
                },
            )

        # Difficulty  유효성 검사
        if quiz_in.difficulty not in ALLOWED_DIFFICULTY:
            logger.error(f"Invalid difficulty level: {quiz_in.difficulty}")
            raise ValidationError(
                code="VALIDATION_ERROR",
                message="Invalid difficulty level.",
                details={"difficulty": f"Must be one of {ALLOWED_DIFFICULTY}."},
            )

        # Quiz 생성
        new_quiz = Quiz(
            title=f"Quiz for Chapter {quiz_in.chapter_id}",
            user_id=current_user["user_id"],  # TODO) 실제 사용자 ID로
            difficulty=quiz_in.difficulty,
            total_problems_count=quiz_in.question_count,
            # status는 기본값으로 'in_progress'가 설정
            chapter_id=quiz_in.chapter_id,
        )
        db.add(new_quiz)
        await db.commit()
        await db.refresh(new_quiz)
        logger.info(f"Quiz created with id {new_quiz.id}")
        return new_quiz
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "DATABASE_ERROR", "message": "A database error occurred."},
        )
    except ValidationError as ve:
        logger.error(f"Validation error: {ve.detail}")
        raise ve
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "SERVER_ERROR", "message": "An unexpected error occurred."},
        )
