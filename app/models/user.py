from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP
from app.models.base import Base, BaseTimestamp

class User(Base, BaseTimestamp):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    oauth_provider = Column(String(50))
    oauth_id = Column(String(255))
    review_completed_quizzes_count = Column(Integer, default=0)
    graded_quizzes_count = Column(Integer, default=0)
    ongoing_quizzes_count = Column(Integer, default=0)
    last_login_at = Column(TIMESTAMP)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)