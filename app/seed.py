import asyncio
import random
from datetime import datetime, timedelta

from faker import Faker
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.database import async_session
from app.models.answer_sheet import AnswerSheet, AnswerSheetStatus
from app.models.chapter import Chapter
from app.models.grading_result import GradingResult
from app.models.problem import Problem
from app.models.problem_in_quiz import ProblemInQuiz
from app.models.quiz import Quiz
from app.models.study_log import StudyLog
from app.models.user import User
from app.models.user_answer import UserAnswer
from app.models.user_problem_stat import UserProblemStat
from app.models import LearningProgress, LearningStatus


fake = Faker()

ALLOWED_DIFFICULTIES = ["easy", "medium", "hard"]
ALLOWED_STATUSES = ["in_progress", "graded", "reviewed"]
ALLOWED_PROBLEM_COUNTS = [5, 10, 20, 30]
ALLOWED_RESULTS = ["correct", "incorrect"]
ALLOWED_STUDY_LOG_DAYS = 30  # 지난 30일간의 학습 로그 생성
ALLOWED_QUIZ_COUNT_PER_DAY = [1, 2, 3, 4, 5]


async def add_unique(session, model, **kwargs):
    """중복되지 않는 데이터를 추가하는 유틸리티 함수."""
    stmt = select(model).filter_by(**kwargs)
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()
    if not existing:
        instance = model(**kwargs)
        session.add(instance)
        return instance
    return existing


async def seed_users(count: int = 10):
    async with async_session() as session:
        for _ in range(count):
            await add_unique(
                session,
                User,
                email=fake.unique.email(),
                name=fake.name(),
                password=fake.password(),
                oauth_provider=None,
                oauth_id=None,
                review_completed_quizzes_count=0,
                graded_quizzes_count=0,
                ongoing_quizzes_count=0,
                last_login_at=None,
                is_active=True,
                is_deleted=False,
            )
        try:
            await session.commit()
            print(f"✅ {count} users seeded.")
        except IntegrityError:
            await session.rollback()
            print("⚠️ Users already seeded or integrity error occurred.")


async def seed_chapters(count: int = 5):
    async with async_session() as session:
        for i in range(1, count + 1):
            chapter = await add_unique(
                session,
                Chapter,
                name=f"Chapter {i}",
                chapter_order=i,
            )
            chapter.description = fake.text()
            chapter.problems_count = 0  # 추후 업데이트 가능
        try:
            await session.commit()
            print(f"✅ {count} chapters seeded.")
        except IntegrityError:
            await session.rollback()
            print("⚠️ Chapters already seeded or integrity error occurred.")


async def seed_problems(chapter_count: int = 5, problems_per_chapter: int = 30):
    async with async_session() as session:
        for chapter_id in range(1, chapter_count + 1):
            for _ in range(problems_per_chapter):
                problem = Problem(
                    chapter_id=chapter_id,
                    difficulty=random.choice(ALLOWED_DIFFICULTIES),
                    image_url=(
                        fake.image_url()
                        if fake.boolean(chance_of_getting_true=30)
                        else None
                    ),
                    correct_answer=str(random.randint(1, 5)),  # 문자열로 저장
                    explanation=fake.paragraph(),
                    attempt_count=0,
                    correct_count=0,
                    problem_text=fake.sentence(nb_words=10),
                )
                session.add(problem)
        try:
            await session.commit()
            print(f"✅ {chapter_count * problems_per_chapter} problems seeded.")
        except IntegrityError:
            await session.rollback()
            print("⚠️ Problems already seeded or integrity error occurred.")


async def seed_quizzes(user_count: int = 10, quizzes_per_user: int = 3):
    async with async_session() as session:
        quizzes = []
        for user_id in range(1, user_count + 1):
            for _ in range(quizzes_per_user):
                quiz = Quiz(
                    title=fake.sentence(nb_words=6),
                    user_id=user_id,
                    difficulty=random.choice(ALLOWED_DIFFICULTIES),
                    total_problems_count=random.choice(ALLOWED_PROBLEM_COUNTS),
                    status=random.choice(ALLOWED_STATUSES),
                    chapter_id=random.randint(1, 5),  # assuming 5 chapters
                )
                session.add(quiz)
                quizzes.append(quiz)
        try:
            await session.commit()
            print(f"✅ {user_count * quizzes_per_user} quizzes seeded.")
        except IntegrityError as e:
            await session.rollback()
            print(f"⚠️ Quizzes already seeded or integrity error occurred: {e}")
        return quizzes  # Return for linking ProblemsInQuizzes


async def seed_problems_in_quizzes(quizzes: list, problems_per_quiz: int = 10):
    async with async_session() as session:
        problems_in_quizzes = []
        for quiz in quizzes:
            # 문제 선택: 해당 챕터의 문제 중 랜덤하게 선택
            stmt = select(Problem).filter_by(chapter_id=quiz.chapter_id)
            result = await session.execute(stmt)
            chapter_problems = result.scalars().all()
            if len(chapter_problems) < problems_per_quiz:
                selected_problems = chapter_problems
            else:
                selected_problems = random.sample(chapter_problems, problems_per_quiz)

            for idx, problem in enumerate(selected_problems, start=1):
                piq = ProblemInQuiz(
                    quiz_id=quiz.id, problem_id=problem.id, problem_number=idx
                )
                session.add(piq)
                problems_in_quizzes.append(piq)
        try:
            await session.commit()
            print(f"✅ {len(problems_in_quizzes)} problems_in_quizzes seeded.")
        except IntegrityError as e:
            await session.rollback()
            print(
                f"⚠️ ProblemsInQuizzes already seeded or integrity error occurred: {e}"
            )


async def seed_answer_sheets(user_count: int = 10, quizzes_per_user: int = 3):
    async with async_session() as session:
        answer_sheets = []
        quiz_id = 1  # assuming quizzes are sequentially numbered starting at 1
        for user_id in range(1, user_count + 1):
            for _ in range(quizzes_per_user):
                answer_sheet = AnswerSheet(
                    quiz_id=quiz_id,
                    user_id=user_id,
                    status=random.choice(list(AnswerSheetStatus)),
                    resumed_at=None,
                    stopped_at=None,
                    passed_time=None,
                    unanswered_count=random.randint(0, 5),
                )
                session.add(answer_sheet)
                answer_sheets.append(answer_sheet)
                quiz_id += 1
        try:
            await session.commit()
            print(f"✅ {user_count * quizzes_per_user} answer sheets seeded.")
        except IntegrityError as e:
            await session.rollback()
            print(f"⚠️ Answer sheets already seeded or integrity error occurred: {e}")
        return answer_sheets  # Return for linking UserAnswers and GradingResults


async def seed_user_answers(
    user_count: int = 10, quizzes_per_user: int = 3, problems_per_quiz: int = 10
):
    async with async_session() as session:
        user_answers = []
        # 모든 ProblemInQuiz 엔트리 가져오기
        stmt = select(ProblemInQuiz)
        piq_results = await session.execute(stmt)
        piqs = piq_results.scalars().all()

        # quiz_id별로 problem_id 목록 매핑
        quiz_to_problems = {}
        for piq in piqs:
            quiz_to_problems.setdefault(piq.quiz_id, []).append(piq.problem_id)

        # 모든 AnswerSheet 가져오기
        stmt = select(AnswerSheet)
        result = await session.execute(stmt)
        answer_sheets = result.scalars().all()

        for answer_sheet in answer_sheets:
            quiz_id = answer_sheet.quiz_id
            problem_ids = quiz_to_problems.get(quiz_id, [])
            for problem_id in problem_ids:
                # 문제의 정답 가져오기
                stmt = select(Problem.correct_answer).filter_by(id=problem_id)
                result = await session.execute(stmt)
                correct_answer = result.scalar_one_or_none()
                if correct_answer is None:
                    print(f"⚠️ Problem ID {problem_id} does not exist.")
                    continue

                # 사용자 답변 생성
                user_answer_value = random.randint(1, 5)
                is_correct = str(user_answer_value) == correct_answer

                user_answer = UserAnswer(
                    answer_sheet_id=answer_sheet.id,
                    problem_id=problem_id,
                    user_answer=str(user_answer_value),  # 문자열로 저장
                    is_correct=is_correct,
                    is_starred=fake.boolean(chance_of_getting_true=10),
                    has_answer=True,
                )
                session.add(user_answer)
                user_answers.append(user_answer)
        try:
            await session.commit()
            print(f"✅ {len(user_answers)} user answers seeded.")
        except IntegrityError as e:
            await session.rollback()
            print(f"⚠️ User answers already seeded or integrity error occurred: {e}")
        return user_answers  # Return for linking GradingResults


async def seed_grading_results(user_answers: list):
    async with async_session() as session:
        grading_results = []
        for ua in user_answers:
            grading_result = GradingResult(
                answer_sheet_id=ua.answer_sheet_id,
                problem_id=ua.problem_id,
                result="correct" if ua.is_correct else "incorrect",
            )
            session.add(grading_result)
            grading_results.append(grading_result)
        try:
            await session.commit()
            print(f"✅ {len(grading_results)} grading results seeded.")
        except IntegrityError as e:
            await session.rollback()
            print(f"⚠️ Grading results already seeded or integrity error occurred: {e}")


async def seed_study_logs(user_count: int = 10, study_logs_per_user: int = 5):
    async with async_session() as session:
        study_logs = []
        for user_id in range(1, user_count + 1):
            for _ in range(study_logs_per_user):
                # 랜덤한 날짜 생성 (지난 ALLOWED_STUDY_LOG_DAYS 일)
                random_days_ago = random.randint(1, ALLOWED_STUDY_LOG_DAYS)
                quiz_date = datetime.now().date() - timedelta(days=random_days_ago)
                quiz_count = random.choice(ALLOWED_QUIZ_COUNT_PER_DAY)

                study_log = StudyLog(
                    user_id=user_id,
                    quiz_date=quiz_date,
                    quiz_count=quiz_count,
                )
                session.add(study_log)
                study_logs.append(study_log)
        try:
            await session.commit()
            print(f"✅ {len(study_logs)} study logs seeded.")
        except IntegrityError as e:
            await session.rollback()
            print(f"⚠️ Study logs already seeded or integrity error occurred: {e}")
        return study_logs


async def seed_user_problem_stats(user_count: int = 10, problem_count: int = 150):
    async with async_session() as session:
        user_problem_stats = []
        for user_id in range(1, user_count + 1):
            for problem_id in range(1, problem_count + 1):
                is_starred = fake.boolean(chance_of_getting_true=20)
                correct_attempts_count = random.randint(0, 5)
                total_attempts_count = correct_attempts_count + random.randint(0, 3)

                user_problem_stat = UserProblemStat(
                    user_id=user_id,
                    problem_id=problem_id,
                    is_starred=is_starred,
                    correct_attempts_count=correct_attempts_count,
                    total_attempts_count=total_attempts_count,
                )
                session.add(user_problem_stat)
                user_problem_stats.append(user_problem_stat)
        try:
            await session.commit()
            print(f"✅ {len(user_problem_stats)} user problem stats seeded.")
        except IntegrityError as e:
            await session.rollback()
            print(
                f"⚠️ User problem stats already seeded or integrity error occurred: {e}"
            )

async def seed_learning_progress(user_count: int = 10, progress_per_user: int = 5):
    async with async_session() as session:
        # ✅ 사용자 목록 가져오기
        stmt = select(User.id)
        result = await session.execute(stmt)
        users = result.scalars().all()

        if not users:
            print("⚠️ No users found in the database. Please seed users first!")
            return

        learning_progress_entries = []
        for user_id in random.sample(users, min(user_count, len(users))):
            for _ in range(progress_per_user):
                new_progress = LearningProgress(
                    user_id=user_id,
                    title=f"Quiz {random.randint(1, 100)}",
                    progress=random.randint(0, 100),
                    status=random.choice(list(LearningStatus)),
                    learning_date=datetime.now().date() - timedelta(days=random.randint(0, 30)),
                )
                session.add(new_progress)
                learning_progress_entries.append(new_progress)

        try:
            await session.commit()
            print(f"✅ {len(learning_progress_entries)} learning progress entries seeded.")
        except IntegrityError as e:
            await session.rollback()
            print(f"⚠️ Integrity error occurred while seeding learning progress: {e}")


async def main():
    print("🌱 Starting database seeding...")
    await seed_users(10)  # 사용자 10명 생성
    await seed_chapters(5)  # 단원 5개 생성
    await seed_problems(5, 30)  # 5개 단원에 각 30개 문제 생성
    quizzes = await seed_quizzes(10, 3)  # 10명 사용자에게 각 3개 퀴즈 생성
    await seed_problems_in_quizzes(quizzes, 10)  # 퀴즈당 10개 문제 연결
    answer_sheets = await seed_answer_sheets(
        10, 3
    )  # 10명 사용자에게 각 3개 답안지 생성
    user_answers = await seed_user_answers(10, 3, 10)  # 답안지당 10개 문제 답변 생성
    await seed_grading_results(user_answers)  # 답안지당 10개 문제 채점 결과 생성
    await seed_study_logs(10, 5)  # 사용자당 5개의 학습 로그 생성
    await seed_user_problem_stats(10, 150)  # 사용자당 150개의 문제 통계 생성
    await seed_learning_progress(10, 5)  # ✅ 사용자당 5개의 학습 진행 데이터 생성
    print("✅ Seeding completed!")


if __name__ == "__main__":
    asyncio.run(main())
