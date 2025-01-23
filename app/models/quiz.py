from typing import List, TYPE_CHECKING
from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BaseTimestamp

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.chapter import Chapter
    from app.models.problem_in_quiz import ProblemInQuiz
    from app.models.answer_sheet import AnswerSheet


class Quiz(Base, BaseTimestamp):
    __tablename__ = "quizzes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    difficulty: Mapped[str] = mapped_column(
        Enum("easy", "medium", "hard", "random"), nullable=False
    )
    total_problems_count: Mapped[str] = mapped_column(
        Enum("5", "10", "20", "30"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        Enum("in_progress", "graded", "reviewed"), nullable=False
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
