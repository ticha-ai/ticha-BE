from sqlalchemy import Column, Date, ForeignKey, Integer

from app.models.base import Base, BaseTimestamp


class StudyLog(Base, BaseTimestamp):
    __tablename__ = "study_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quiz_date = Column(Date, nullable=False)
    quiz_count = Column(Integer, default=0)
