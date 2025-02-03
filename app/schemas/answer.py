from typing import List, Optional

from pydantic import BaseModel, Field


class AnswerCreate(BaseModel):
    problem_id: int
    selected_option: Optional[str] = None
    is_starred: bool = False


class AnswerSheetCreate(BaseModel):
    user_id: int
    answers: List[AnswerCreate]
    passed_time: float = Field(ge=0)
