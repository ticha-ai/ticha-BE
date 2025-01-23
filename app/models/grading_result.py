from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BaseTimestamp

if TYPE_CHECKING:
    from app.models.answer_sheet import AnswerSheet
    from app.models.problem import Problem


class GradingResult(Base, BaseTimestamp):
    __tablename__ = "grading_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    answer_sheet_id: Mapped[int] = mapped_column(
        ForeignKey("answer_sheets.id"), nullable=False
    )
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id"), nullable=False)
    result: Mapped[str] = mapped_column(Enum("correct", "incorrect"), nullable=False)

    # Relationships
    answer_sheet: Mapped["AnswerSheet"] = relationship(
        "AnswerSheet", back_populates="grading_results"
    )
    problem: Mapped["Problem"] = relationship(
        "Problem", back_populates="grading_results"
    )
