from sqlalchemy import Column, Enum, ForeignKey, Integer, String, Text

from app.models.base import Base, BaseTimestamp


class Problem(Base, BaseTimestamp):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False)
    difficulty = Column(Enum("easy", "medium", "hard"), nullable=False)
    image_url = Column(String(255))
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text)
    attempt_count = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    problem_text = Column(Text, nullable=False)
