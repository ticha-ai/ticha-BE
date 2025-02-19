import enum
from datetime import date
from typing import TYPE_CHECKING, List

from sqlalchemy import CheckConstraint, Date, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BaseTimestamp

# 타입 힌트에 필요한 모델 임포트
if TYPE_CHECKING:
    from app.models.user import User


class LearningStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    REVIEWABLE = "reviewable"
    COMPLETED = "completed"


class LearningProgress(Base, BaseTimestamp):
    __tablename__ = "learning_progress"

    # -- 테이블 레벨 제약 조건 --
    __table_args__ = (
        CheckConstraint("progress >= 0 AND progress <= 100", name="ck_progress_range"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[LearningStatus] = mapped_column(
        Enum(LearningStatus), nullable=False, default=LearningStatus.IN_PROGRESS
    )
    learning_date: Mapped[date] = mapped_column(
        Date, nullable=False, default=date.today
    )

    # ============== #
    #   Relationships
    # ============== #

    # user: Mapped["User"] = relationship("User", back_populates="learning_progress")
