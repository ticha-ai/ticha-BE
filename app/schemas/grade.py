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


class ProblemDetail(BaseModel):
    problem_id: int
    user_answer: Optional[int]  # 사용자가 선택한 답안 선지
    correct_answer: int  # 문제의 정답 선지
    is_correct: bool  # 정답 여부
    is_starred: bool  # 사용자 별표 표시했는지 여부


class GradingResultResponse(BaseModel):
    total_questions: int
    correct_count: int
    passed_time: str  # "MM:SS" 형식
    chapter_name: str
    difficulty: str
    problems: List[ProblemDetail]  # 문제별 상세 정보
    current_page: int  # 현재 페이지 번호
    total_pages: int  # 총 페이지 수
