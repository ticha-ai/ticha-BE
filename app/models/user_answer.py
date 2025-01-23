from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey
from app.models.base import Base, BaseTimestamp


class UserAnswer(Base, BaseTimestamp):
    __tablename__ = "user_answers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    answer_sheet_id = Column(Integer, ForeignKey("answer_sheets.id"), nullable=False)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
    user_answer = Column(Text)
    is_correct = Column(Boolean, default=False)
    is_starred = Column(Boolean, default=False)
    has_answer = Column(Boolean, default=False)
