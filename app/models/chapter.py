from sqlalchemy import TIMESTAMP, Column, Integer, String, Text

from app.models.base import Base, BaseTimestamp


class Chapter(Base, BaseTimestamp):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    problems_count = Column(Integer, default=0)
    chapter_order = Column(Integer)
