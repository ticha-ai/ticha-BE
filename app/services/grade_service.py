from typing import List

from fastapi import HTTPException
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.answer_sheet import AnswerSheet
from app.models.problem import Problem
from app.models.problem_in_quiz import ProblemInQuiz
from app.models.quiz import Quiz
from app.models.user_answer import UserAnswer
from app.schemas.grade import AnswerGrade


async def grade_answer_sheet(
    answer_sheet_id: int,
    db: AsyncSession,
    current_user: dict,
    answers: List[AnswerGrade],
):
    current_user_id = current_user["user_id"]

    # AnswerSheet 조회
    result = await db.execute(
        select(AnswerSheet).where(
            AnswerSheet.id == answer_sheet_id,
            AnswerSheet.user_id == current_user_id,
        )
    )
    answer_sheet = result.scalars().first()
    if not answer_sheet:
        return None

    # Quiz의 total_problems_count 가져오기
    quiz_result = await db.execute(select(Quiz).where(Quiz.id == answer_sheet.quiz_id))
    quiz = quiz_result.scalars().first()
    if not quiz:
        raise HTTPException(status_code=404, detail="퀴즈를 찾을 수 없습니다.")

    total_questions = quiz.total_problems_count

    correct_count = 0

    # 사용자 답안 저장 및 정답 여부 확인
    for answer in answers:
        # 문제가 해당 퀴즈에 포함되어 있는지 확인
        problem_in_quiz_result = await db.execute(
            select(ProblemInQuiz).where(
                ProblemInQuiz.quiz_id == quiz.id,
                ProblemInQuiz.problem_id == answer.problem_id,
            )
        )
        problem_in_quiz = problem_in_quiz_result.scalars().first()
        if not problem_in_quiz:
            # 해당 문제가 퀴즈에 포함되지 않은 경우
            raise HTTPException(
                status_code=400,
                detail=f"문제 {answer.problem_id}는 퀴즈 {quiz.id}에 포함되지 않습니다.",
            )

        # 문제의 정답 가져오기
        problem_result = await db.execute(
            select(Problem).where(Problem.id == answer.problem_id)
        )
        problem = problem_result.scalars().first()
        if not problem:
            raise HTTPException(
                status_code=404,
                detail=f"문제를 찾을 수 없습니다. (ID: {answer.problem_id})",
            )

        # 정답 여부 확인
        is_correct = str(answer.selected_option) == str(problem.correct_answer)

        # UserAnswer 업데이트 또는 생성
        stmt = (
            update(UserAnswer)
            .where(
                UserAnswer.answer_sheet_id == answer_sheet_id,
                UserAnswer.problem_id == answer.problem_id,
            )
            .values(
                user_answer=answer.selected_option,
                has_answer=answer.selected_option is not None,
                is_correct=is_correct,  # 정답 여부 저장
            )
        )
        result = await db.execute(stmt)

        if result.rowcount == 0:
            # 새로 추가된 답안 처리
            new_answer = UserAnswer(
                answer_sheet_id=answer_sheet_id,
                problem_id=answer.problem_id,
                user_answer=answer.selected_option,
                has_answer=answer.selected_option is not None,
                is_correct=is_correct,  # 정답 여부 저장
            )
            db.add(new_answer)

        if is_correct:
            correct_count += 1

    # 답안지 상태 업데이트
    answer_sheet.status = "graded"
    await db.commit()
    await db.refresh(answer_sheet)

    # 점수 계산 및 반환
    score = (correct_count / total_questions) * 100 if total_questions > 0 else 0

    return {
        "score": score,
        "correct_count": correct_count,
        "total_questions": total_questions,
    }
