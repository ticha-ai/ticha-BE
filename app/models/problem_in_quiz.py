from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP
from app.models.base import Base, BaseTimestamp

class ProblemInQuiz(Base, BaseTimestamp):
    __tablename__ = "problems_in_quizzes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
    problem_number = Column(Integer, nullable=False)