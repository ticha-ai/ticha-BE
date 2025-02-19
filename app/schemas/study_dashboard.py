from datetime import date
from typing import List

from pydantic import BaseModel


class QuizInfo(BaseModel):
    quiz_id: int
    title: str
    status: str  # "in_progress", "graded", "reviewed"


class StudyRecordDay(BaseModel):
    date: date
    has_study: bool
    quizzes: List[QuizInfo] = []  # 해당 날짜의 문제지 정보


class CalendarStudyRecordsResponse(BaseModel):
    study_records: List[StudyRecordDay]


class InProgressAnswerSheet(BaseModel):
    answer_sheet_id: int
    quiz_title: str
    progress_rate: float  # 진행률
    study_date: date  # 학습일


class InProgressAnswerSheetResponse(BaseModel):
    answer_sheets: List[InProgressAnswerSheet]
