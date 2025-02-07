from typing import TYPE_CHECKING, List

from sqlalchemy import TIMESTAMP, Boolean, CheckConstraint, Column, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BaseTimestamp

# 타입 힌트에 필요한 모델 임포트
if TYPE_CHECKING:
    from app.models.answer_sheet import AnswerSheet
    from app.models.quiz import Quiz
    from app.models.study_log import StudyLog
    from app.models.user_problem_stat import UserProblemStat


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

    # ✅ password 필드를 nullable=True로 변경 (OAuth 사용자는 NULL)
    password: Mapped[str | None] = mapped_column(String(255), nullable=True)

    oauth_provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    oauth_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    refresh_token: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # ✅ 카카오 프로필 이미지 추가
    profile_image: Mapped[str | None] = mapped_column(String(500), nullable=True)

    review_completed_quizzes_count: Mapped[int] = mapped_column(Integer, default=0)
    graded_quizzes_count: Mapped[int] = mapped_column(Integer, default=0)
    ongoing_quizzes_count: Mapped[int] = mapped_column(Integer, default=0)

    last_login_at: Mapped[TIMESTAMP | None] = mapped_column(TIMESTAMP, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    # ============== #
    #   Relationships
    # ============== #

    problem_stats: Mapped[List["UserProblemStat"]] = relationship(
        "UserProblemStat", back_populates="user"
    )

    quizzes: Mapped[List["Quiz"]] = relationship("Quiz", back_populates="user")

    study_logs: Mapped[List["StudyLog"]] = relationship(
        "StudyLog", back_populates="user"
    )

    answer_sheets: Mapped[List["AnswerSheet"]] = relationship(
        "AnswerSheet", back_populates="user"
    )
