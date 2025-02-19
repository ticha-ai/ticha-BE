import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import ValidationError
from app.schemas.quiz import (
    QuizCreateRequest,
    QuizData,
    QuizQuestionsResponse,
    QuizResponse,
)
from app.services.quiz_service import create_quiz, get_quiz_questions

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/quizzes", response_model=QuizResponse, status_code=status.HTTP_201_CREATED
)
async def create_quiz_endpoint(
    request: Request, quiz_in: QuizCreateRequest, db: AsyncSession = Depends(get_db)
):
    """
    문제지 생성 엔드포인트
    """
    try:
        quiz = await create_quiz(db, quiz_in, request.state.user.id)
        response_data = QuizData(
            quiz_id=quiz.id,
            chapter_id=quiz.chapter_id,
            question_count=quiz.total_problems_count,
            difficulty=quiz.difficulty,
            status=quiz.status,
            user_id=request.state.user.id,
            created_at=quiz.created_at,
        )
        return QuizResponse(
            success=True,
            data=response_data,
            message="Quiz created successfully.",
        )
    except ValidationError as ve:
        logger.error(f"Validation error: {ve.detail}")
        raise ve
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error creating quiz: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "SERVER_ERROR", "message": "An unexpected error occurred."},
        )


@router.get(
    "/quizzes/{quiz_id}/questions",
    response_model=QuizQuestionsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_questions(
    quiz_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(5, ge=1),
    db: AsyncSession = Depends(get_db),
):
    """
    문제지의 문제 조회하는 API
    """
    response = await get_quiz_questions(db, quiz_id, page, limit)
    return response
