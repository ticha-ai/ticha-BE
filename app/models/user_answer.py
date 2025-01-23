from typing import TYPE_CHECKING
from sqlalchemy import Boolean, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BaseTimestamp

if TYPE_CHECKING:
    from app.models.answer_sheet import AnswerSheet
    from app.models.problem import Problem


class UserAnswer(Base, BaseTimestamp):
    __tablename__ = "user_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    answer_sheet_id: Mapped[int] = mapped_column(
        ForeignKey("answer_sheets.id"), nullable=False
    )
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id"), nullable=False)
    user_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    is_starred: Mapped[bool] = mapped_column(Boolean, default=False)
    has_answer: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    answer_sheet: Mapped["AnswerSheet"] = relationship(
        "AnswerSheet", back_populates="user_answers"
    )
    problem: Mapped["Problem"] = relationship("Problem", back_populates="user_answers")
