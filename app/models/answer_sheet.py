from enum import Enum as PyEnum
from typing import TYPE_CHECKING, List

from sqlalchemy import TIMESTAMP
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BaseTimestamp

if TYPE_CHECKING:
    from app.models.grading_result import GradingResult
    from app.models.quiz import Quiz
    from app.models.user import User
    from app.models.user_answer import UserAnswer


class AnswerSheetStatus(PyEnum):
    IN_PROGRESS = "in_progress"
    GRADED = "graded"
    REVIEWED = "reviewed"


class AnswerSheet(Base, BaseTimestamp):
    __tablename__ = "answer_sheets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[AnswerSheetStatus] = mapped_column(
        SQLAlchemyEnum(AnswerSheetStatus),
        nullable=False,
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
