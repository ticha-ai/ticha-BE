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


class AnswerResponse(BaseModel):
    problem_id: int
    user_answer: Optional[str] = None
    is_starred: bool
    has_answer: bool


class AnswerSheetResponse(BaseModel):
    id: int
    quiz_id: int
    user_id: int
    passed_time: int
    status: str
    answers: List[AnswerResponse] = Field(default_factory=list, alias="user_answers")
