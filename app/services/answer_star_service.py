from typing import List

from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AnswerSheet, ProblemInQuiz, UserAnswer
from app.schemas.answer_star import StarredProblem


async def update_star_status(
    db, answer_sheet_id: int, problem_id: int, is_starred: bool
) -> None:
    # 1. 해당 answer_sheet를 조회하여 quiz_id를 가져옴
    query = select(AnswerSheet).where(AnswerSheet.id == answer_sheet_id)
    result = await db.execute(query)
    answer_sheet = result.scalar_one_or_none()
    if not answer_sheet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 답안지가 존재하지 않습니다.",
        )
    quiz_id = answer_sheet.quiz_id

    # 2. 해당 quiz에 문제(problem_id)가 포함되어 있는지 확인
    query = select(ProblemInQuiz).where(
        ProblemInQuiz.quiz_id == quiz_id, ProblemInQuiz.problem_id == problem_id
    )
    result = await db.execute(query)
    problem_in_quiz = result.scalar_one_or_none()
    if not problem_in_quiz:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"문제 {problem_id}는 퀴즈 {quiz_id}에 포함되지 않습니다.",
        )

    # 3. UserAnswer 테이블에서 해당 레코드를 별표 상태 업데이트
    stmt = (
        update(UserAnswer)
        .where(
            UserAnswer.answer_sheet_id == answer_sheet_id,
            UserAnswer.problem_id == problem_id,
        )
        .values(is_starred=is_starred)
    )
    result = await db.execute(stmt)

    # 4. 레코드가 없으면 새 레코드 생성
    if result.rowcount == 0:
        new_answer = UserAnswer(
            answer_sheet_id=answer_sheet_id,
            problem_id=problem_id,
            is_starred=is_starred,
            user_answer=None,
            has_answer=False,
        )
        db.add(new_answer)

    try:
        await db.commit()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="별표 상태 업데이트 중 데이터베이스 오류가 발생했습니다.",
        )


async def get_starred_problems(
    db: AsyncSession, answersheet_id: int
) -> List[StarredProblem]:
    query = select(UserAnswer).where(
        UserAnswer.answer_sheet_id == answersheet_id,
        UserAnswer.is_starred == True,  # 별표된 문제만 필터링
    )
    result = await db.execute(query)
    starred_problems = result.scalars().all()

    if not starred_problems:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 문제지에서 사용자가 별표한 문제가 없습니다.",
        )

    return [
        StarredProblem(
            problem_id=user_answer.problem_id,
            is_starred=user_answer.is_starred,
        )
        for user_answer in starred_problems
    ]
