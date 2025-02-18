from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class QuizCreateRequest(BaseModel):
    chapter_id: int = Field(..., gt=0, description="단원번호")
    question_count: int = Field(..., gt=0, description="문제의 갯수")
    difficulty: Literal["easy", "medium", "hard", "random"] = Field(
        ..., description="문제지의 난이도 (easy, medium, hard, random)"
    )


class QuizData(BaseModel):
    chapter_id: int
    question_count: int
    difficulty: str
    status: str
    user_id: int
    created_at: datetime


class QuizResponse(BaseModel):
    success: bool
    data: QuizData
    message: str


class Pagination(BaseModel):
    current_page: int
    total_pages: int
    limit: int
    total_questions: int


class Question(BaseModel):
    question_id: int
    image_url: str
    choices_count: int


class QuizQuestionsData(BaseModel):
    quiz_id: int
    title: str
    difficulty: str
    questions: List[Question]
    pagination: Pagination


class QuizQuestionsResponse(BaseModel):
    success: bool
    data: QuizQuestionsData
    message: Optional[str] = None
