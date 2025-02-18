from typing import TYPE_CHECKING, List

from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BaseTimestamp

if TYPE_CHECKING:
    from app.models.chapter import Chapter
    from app.models.grading_result import GradingResult
    from app.models.problem_in_quiz import ProblemInQuiz
    from app.models.user_answer import UserAnswer
    from app.models.user_problem_stat import UserProblemStat


class Problem(Base, BaseTimestamp):
    __tablename__ = "problems"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chapter_id: Mapped[int] = mapped_column(ForeignKey("chapters.id"), nullable=False)
    difficulty: Mapped[str] = mapped_column(
        Enum("easy", "medium", "hard"), nullable=False
    )
    image_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    correct_answer: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    problem_text: Mapped[str] = mapped_column(Text, nullable=False)
    choices_count: Mapped[int] = mapped_column(Integer, nullable=False, default=5)

    # Relationships
    chapter: Mapped["Chapter"] = relationship("Chapter", back_populates="problems")

    user_stats: Mapped[List["UserProblemStat"]] = relationship(
        "UserProblemStat", back_populates="problem"
    )

    problems_in_quizzes: Mapped[List["ProblemInQuiz"]] = relationship(
        "ProblemInQuiz", back_populates="problem"
    )

    user_answers: Mapped[List["UserAnswer"]] = relationship(
        "UserAnswer", back_populates="problem"
    )

    grading_results: Mapped[List["GradingResult"]] = relationship(
        "GradingResult", back_populates="problem"
    )
