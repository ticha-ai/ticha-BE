from sqlalchemy import TIMESTAMP, Column, Enum, ForeignKey, Integer, String

from app.models.base import Base, BaseTimestamp


class Quiz(Base, BaseTimestamp):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    difficulty = Column(Enum("easy", "medium", "hard", "random"), nullable=False)
    total_problems_count = Column(Enum("5", "10", "20", "30"), nullable=False)
    status = Column(Enum("in_progress", "graded", "reviewed"), nullable=False)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False)
