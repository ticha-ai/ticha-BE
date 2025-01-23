from sqlalchemy import Column, Integer, Enum, TIMESTAMP, ForeignKey
from app.models.base import Base, BaseTimestamp

class AnswerSheet(Base, BaseTimestamp):
    __tablename__ = "answer_sheets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum("in_progress", "graded", "reviewed"), nullable=False)
    resumed_at = Column(TIMESTAMP)
    stopped_at = Column(TIMESTAMP)
    passed_time = Column(Integer)
    unanswered_count = Column(Integer, default=0)