from typing import List, Optional

from pydantic import BaseModel


class AnswerGrade(BaseModel):
    problem_id: int
    selected_option: Optional[int]  # null 값 허용 (미응답인 경우)


class GradeRequest(BaseModel):
    answers: List[AnswerGrade]


class GradeResult(BaseModel):
    score: float  # 점수 (0~100)
    correct_count: int  # 정답 개수
    total_questions: int  # 총 문제 수
