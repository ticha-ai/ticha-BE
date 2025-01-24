from typing import TYPE_CHECKING, List

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BaseTimestamp

if TYPE_CHECKING:
    from app.models.problem import Problem
    from app.models.quiz import Quiz


class Chapter(Base, BaseTimestamp):
    __tablename__ = "chapters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    problems_count: Mapped[int] = mapped_column(Integer, default=0)
    chapter_order: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relationships
    problems: Mapped[List["Problem"]] = relationship(
        "Problem", back_populates="chapter"
    )
    quizzes: Mapped[List["Quiz"]] = relationship("Quiz", back_populates="chapter")
