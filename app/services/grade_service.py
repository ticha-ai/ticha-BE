from typing import List

from fastapi import HTTPException
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.models.answer_sheet import AnswerSheet
from app.models.grading_result import GradingResult
from app.models.problem import Problem
from app.models.problem_in_quiz import ProblemInQuiz
from app.models.quiz import Quiz
from app.models.user_answer import UserAnswer
from app.schemas.grade import AnswerGrade


async def grade_answer_sheet(
    answer_sheet_id: int,
    db: AsyncSession,
    answers: List[AnswerGrade],
    user_id: int,
):

    # AnswerSheet 조회
    result = await db.execute(
        select(AnswerSheet).where(
            AnswerSheet.id == answer_sheet_id,
            AnswerSheet.user_id == user_id,
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
    result_text = "correct" if is_correct else "incorrect"

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

    # GradingResult
    grading_result_stmt = (
        update(GradingResult)
        .where(
            GradingResult.answer_sheet_id == answer_sheet_id,
            GradingResult.problem_id == answer.problem_id,
        )
        .values(result=result_text)
    )
    grading_result_update = await db.execute(grading_result_stmt)

    if grading_result_update.rowcount == 0:
        new_grading_result = GradingResult(
            answer_sheet_id=answer_sheet_id,
            problem_id=answer.problem_id,
            result=result_text,
        )
        db.add(new_grading_result)

    if is_correct:
        correct_count += 1

    # 답안지 상태 업데이트 - 채점 완료 상태로
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


async def get_grading_results_with_pagination(
    answer_sheet_id: int,
    page: int,
    page_size: int,
    db: AsyncSession,
):
    # 해당 답안지 AnswerSheet 조회
    answer_sheet_query = await db.execute(
        select(AnswerSheet).where(AnswerSheet.id == answer_sheet_id)
    )
    answer_sheet = answer_sheet_query.scalars().first()
    if not answer_sheet:
        raise HTTPException(status_code=404, detail="답안지를 찾을 수 없습니다.")

    # Quiz 정보 조회 (총 문제 수, 단원 이름, 난이도)
    quiz_query = await db.execute(
        select(Quiz)
        .options(joinedload(Quiz.chapter))
        .where(Quiz.id == answer_sheet.quiz_id)
    )
    quiz = quiz_query.scalars().first()
    if not quiz:
        raise HTTPException(status_code=404, detail="퀴즈를 찾을 수 없습니다.")

    # ProblemInQuiz 기준으로 모든 문제 가져오기 (페이지네이션 적용)
    problems_in_quiz_query = (
        select(ProblemInQuiz, Problem)
        .join(Problem, ProblemInQuiz.problem_id == Problem.id)
        .where(ProblemInQuiz.quiz_id == quiz.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    problems_in_quiz = await db.execute(problems_in_quiz_query)

    problems = []
    for problem_in_quiz, problem in problems_in_quiz.all():
        # GradingResult와 UserAnswer 조회
        grading_result_query = await db.execute(
            select(GradingResult, UserAnswer)
            .join(UserAnswer, GradingResult.problem_id == UserAnswer.problem_id)
            .where(
                GradingResult.answer_sheet_id == answer_sheet_id,
                GradingResult.problem_id == problem.id,
            )
        )
        result = grading_result_query.first()

        grading_result = result[0] if result else None
        user_answer = result[1] if result else None

        # 문제별 데이터 추가
        problems.append(
            {
                "problem_id": problem.id,
                "user_answer": user_answer.user_answer if user_answer else None,
                "correct_answer": problem.correct_answer,
                "is_correct": (
                    grading_result.result == "correct" if grading_result else False
                ),
                "is_starred": user_answer.is_starred if user_answer else False,
            }
        )

    # 총 문제 수 계산 및 페이지네이션 처리
    total_questions = quiz.total_problems_count
    correct_count = sum(1 for problem in problems if problem["is_correct"])
    total_pages = (total_questions + page_size - 1) // page_size

    # 소요 시간 (MM:SS format)
    passed_time_seconds = answer_sheet.passed_time or 0
    passed_time_minutes = int(passed_time_seconds // 60)
    passed_time_seconds = int(passed_time_seconds % 60)
    passed_time_formatted = f"{passed_time_minutes}:{passed_time_seconds:02d}"

    chapter_name = quiz.chapter.name

    return {
        "total_questions": total_questions,
        "correct_count": correct_count,
        "passed_time": passed_time_formatted,
        "chapter_name": chapter_name,
        "difficulty": quiz.difficulty,
        "problems": problems,
        "current_page": page,
        "total_pages": total_pages,
    }
