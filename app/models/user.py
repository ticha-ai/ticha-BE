from typing import List
from sqlalchemy import TIMESTAMP, Boolean, CheckConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BaseTimestamp


class User(Base, BaseTimestamp):
    __tablename__ = "users"

    # -- 테이블 레벨 제약 조건 --
    __table_args__ = (
        CheckConstraint("review_completed_quizzes_count >= 0", name="ck_review_cnt"),
        CheckConstraint("graded_quizzes_count >= 0", name="ck_graded_cnt"),
        CheckConstraint("ongoing_quizzes_count >= 0", name="ck_ongoing_cnt"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    oauth_provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    oauth_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    review_completed_quizzes_count: Mapped[int] = mapped_column(Integer, default=0)
    graded_quizzes_count: Mapped[int] = mapped_column(Integer, default=0)
    ongoing_quizzes_count: Mapped[int] = mapped_column(Integer, default=0)

    last_login_at: Mapped[TIMESTAMP | None] = mapped_column(TIMESTAMP, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    # ============== #
    #   Relationships
    # ============== #

    # (User -> UserProblemStat) 1:N
    problem_stats: Mapped[List["UserProblemStat"]] = relationship(
        "UserProblemStat", back_populates="user"
    )

    # (User -> Quiz) 1:N
    quizzes: Mapped[List["Quiz"]] = relationship("Quiz", back_populates="user")

    # (User -> StudyLog) 1:N
    study_logs: Mapped[List["StudyLog"]] = relationship(
        "StudyLog", back_populates="user"
    )

    # (User -> AnswerSheet) 1:N
    answer_sheets: Mapped[List["AnswerSheet"]] = relationship(
        "AnswerSheet", back_populates="user"
    )
