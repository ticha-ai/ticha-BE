import logging
import random

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import func

from app.core.exceptions import ValidationError
from app.models.chapter import Chapter
from app.models.problem import Problem
from app.models.problem_in_quiz import ProblemInQuiz
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

        # 문제 가져오기 (해당 단원 + 난이도)
        if quiz_in.difficulty == "random":
            problem_query = await db.execute(
                select(Problem).where(Problem.chapter_id == quiz_in.chapter_id)
            )
        else:
            problem_query = await db.execute(
                select(Problem).where(
                    Problem.chapter_id == quiz_in.chapter_id,
                    Problem.difficulty == quiz_in.difficulty,
                )
            )
        problems = problem_query.scalars().all()

        # 문제 개수 부족하면 오류 발생
        if len(problems) < quiz_in.question_count:
            logger.error(
                f"Not enough problems in chapter {quiz_in.chapter_id} with difficulty {quiz_in.difficulty}."
            )
            raise ValidationError(
                code="NOT_ENOUGH_PROBLEMS",
                message="Not enough problems available.",
                details={
                    "available_problems": len(problems),
                    "required_problems": quiz_in.question_count,
                },
            )

        # 문제 랜덤 선택 (지정된 개수만큼)
        selected_problems = random.sample(problems, quiz_in.question_count)

        # 문제지 생성
        new_quiz = Quiz(
            title=f"Quiz for Chapter {quiz_in.chapter_id}",
            user_id=current_user["user_id"],  # 실제 사용자 ID 사용
            difficulty=quiz_in.difficulty,
            total_problems_count=quiz_in.question_count,
            chapter_id=quiz_in.chapter_id,
        )
        db.add(new_quiz)
        await db.commit()
        await db.refresh(new_quiz)

        # 문제지와 문제 연결 (ProblemInQuiz 생성)
        for idx, problem in enumerate(selected_problems, start=1):
            problem_in_quiz = ProblemInQuiz(
                quiz_id=new_quiz.id, problem_id=problem.id, problem_number=idx
            )
            db.add(problem_in_quiz)

        await db.commit()

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


async def get_quiz_questions(db: AsyncSession, quiz_id: int, page: int, limit: int):
    offset = (page - 1) * limit

    # 퀴즈 존재 여부 확인
    quiz_query = await db.execute(select(Quiz).filter(Quiz.id == quiz_id))
    quiz = quiz_query.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    # 문제 조회 (Eager Loading)
    problems_query = (
        select(ProblemInQuiz)
        .filter(ProblemInQuiz.quiz_id == quiz_id)
        .options(selectinload(ProblemInQuiz.problem))
        .offset(offset)
        .limit(limit)
    )
    problems_result = await db.execute(problems_query)
    problems = problems_result.scalars().all()

    # 총 문제 개수 계산
    total_query = select(func.count(ProblemInQuiz.id)).filter(
        ProblemInQuiz.quiz_id == quiz_id
    )
    total_result = await db.execute(total_query)
    total_count = total_result.scalar()

    # 문제가 없는 경우 에러 처리
    if total_count == 0:
        raise HTTPException(
            status_code=404,
            detail=f"No questions found for quiz {quiz_id}. This might indicate data corruption.",
        )

    # 전체 페이지 수 계산
    total_pages = (total_count + limit - 1) // limit

    if page > total_pages:
        raise HTTPException(
            status_code=400,
            detail=f"Page {page} exceeds available pages. Max page is {total_pages}",
        )

    #  문제 데이터 변환
    questions = [
        {
            "question_id": problem.problem_id,
            "image_url": problem.problem.image_url if problem.problem.image_url else "",
            "choices": [1, 2, 3, 4, 5],  # ✅ TODO: 선택지 로직 반영 필요
        }
        for problem in problems
    ]

    return {
        "success": True,
        "data": {
            "quiz_id": quiz.id,
            "title": quiz.title,
            "difficulty": quiz.difficulty,
            "questions": questions,
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "limit": limit,
                "total_questions": total_count,
            },
        },
        "message": "Questions fetched successfully.",
    }
