from typing import TYPE_CHECKING, List

from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.models.base import Base, BaseTimestamp

if TYPE_CHECKING:
    from app.models.answer_sheet import AnswerSheet
    from app.models.chapter import Chapter
    from app.models.problem_in_quiz import ProblemInQuiz
    from app.models.user import User


# 허용되는 문제 수
ALLOWED_PROBLEM_COUNTS = {5, 10, 20, 30}


class Quiz(Base, BaseTimestamp):
    __tablename__ = "quizzes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    difficulty: Mapped[str] = mapped_column(
        Enum("easy", "medium", "hard", "random"), nullable=False
    )
    total_problems_count: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        Enum("in_progress", "graded", "reviewed"), nullable=False, default="in_progress"
    )
    chapter_id: Mapped[int] = mapped_column(ForeignKey("chapters.id"), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="quizzes")
    chapter: Mapped["Chapter"] = relationship("Chapter", back_populates="quizzes")
    problems_in_quizzes: Mapped[List["ProblemInQuiz"]] = relationship(
        "ProblemInQuiz", back_populates="quiz"
    )
    answer_sheets: Mapped[List["AnswerSheet"]] = relationship(
        "AnswerSheet", back_populates="quiz"
    )

    # 유효성 검사
    @validates("total_problems_count")
    def validate_problem_count(self, key: str, value: int) -> int:
        if value not in ALLOWED_PROBLEM_COUNTS:
            raise ValueError(
                f"total_problems_count must be one of {ALLOWED_PROBLEM_COUNTS}"
            )
        return value
