from pydantic import BaseModel
from datetime import date
from app.models.learning_progress import LearningStatus

class LearningProgressResponse(BaseModel):
    title: str
    progress: int
    learning_date: date
    status: LearningStatus

    class Config:
        from_attributes = True
