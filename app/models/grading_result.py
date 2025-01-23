from sqlalchemy import Column, Integer, Enum, ForeignKey
from app.models.base import Base, BaseTimestamp


class GradingResult(Base, BaseTimestamp):
    __tablename__ = "grading_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    answer_sheet_id = Column(Integer, ForeignKey("answer_sheets.id"), nullable=False)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
    result = Column(Enum("correct", "incorrect"), nullable=False)
