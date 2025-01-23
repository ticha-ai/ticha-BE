from sqlalchemy import Column, Integer, Boolean, ForeignKey
from app.models.base import Base, BaseTimestamp

class UserProblemStat(Base, BaseTimestamp):
    __tablename__ = "user_problems_stat"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
    is_starred = Column(Boolean, default=False)
    correct_attempts_count = Column(Integer, default=0)
    total_attempts_count = Column(Integer, default=0)