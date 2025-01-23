from typing import List, TYPE_CHECKING
from sqlalchemy import TIMESTAMP, Enum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BaseTimestamp

if TYPE_CHECKING:
    from app.models.quiz import Quiz
    from app.models.user import User
    from app.models.user_answer import UserAnswer
    from app.models.grading_result import GradingResult


class AnswerSheet(Base, BaseTimestamp):
    __tablename__ = "answer_sheets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum("in_progress", "graded", "reviewed"), nullable=False
    )
    resumed_at: Mapped[TIMESTAMP | None] = mapped_column(TIMESTAMP, nullable=True)
    stopped_at: Mapped[TIMESTAMP | None] = mapped_column(TIMESTAMP, nullable=True)
    passed_time: Mapped[int | None] = mapped_column(Integer, nullable=True)
    unanswered_count: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="answer_sheets")
    user: Mapped["User"] = relationship("User", back_populates="answer_sheets")

    user_answers: Mapped[List["UserAnswer"]] = relationship(
        "UserAnswer", back_populates="answer_sheet"
    )
    grading_results: Mapped[List["GradingResult"]] = relationship(
        "GradingResult", back_populates="answer_sheet"
    )
