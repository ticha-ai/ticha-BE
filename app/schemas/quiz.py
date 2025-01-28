from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class QuizCreateRequest(BaseModel):
    chapter_id: int = Field(..., gt=0, description="단원번호")
    question_count: int = Field(..., gt=0, description="문제의 갯수")
    difficulty: Literal["easy", "medium", "hard", "random"] = Field(
        ..., description="문제지의 난이도 (easy, medium, hard, random)"
    )


class QuizResponse(BaseModel):
    success: bool
    data: "QuizData"
    message: str


class QuizData(BaseModel):
    chapter_id: int
    question_count: int
    difficulty: str
    status: str
    user_id: int
    created_at: datetime
