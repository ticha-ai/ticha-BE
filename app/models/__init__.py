from sqlalchemy.orm import DeclarativeBase


# Base 클래스 정의
class Base(DeclarativeBase):
    pass


from app.models.answer_sheet import AnswerSheet
from app.models.chapter import Chapter
from app.models.grading_result import GradingResult
from app.models.learning_progress import LearningProgress, LearningStatus
from app.models.problem import Problem
from app.models.problem_in_quiz import ProblemInQuiz
from app.models.quiz import Quiz
from app.models.study_log import StudyLog

# 모든 모델 import
from app.models.user import User
from app.models.user_answer import UserAnswer
from app.models.user_problem_stat import UserProblemStat
