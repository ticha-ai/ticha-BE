from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BaseTimestamp

if TYPE_CHECKING:
    from app.models.problem import Problem
    from app.models.user import User


class UserProblemStat(Base, BaseTimestamp):
    __tablename__ = "user_problems_stat"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id"), nullable=False)
    is_starred: Mapped[bool] = mapped_column(Boolean, default=False)
    correct_attempts_count: Mapped[int] = mapped_column(Integer, default=0)
    total_attempts_count: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="problem_stats")
    problem: Mapped["Problem"] = relationship("Problem", back_populates="user_stats")
