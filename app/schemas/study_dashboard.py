from datetime import date
from typing import List

from pydantic import BaseModel

from app.models.answer_sheet import AnswerSheetStatus


class QuizInfo(BaseModel):
    quiz_id: int
    title: str
    status: AnswerSheetStatus


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


class ChapterStatistics(BaseModel):
    chapter_id: int
    chapter_name: str
    solved_problems: int  # 단원별 푼 문제 수
    correct_answers: int  # 단원별 정답 수
    accuracy_rate: float  # 단원별 정답률


class ChapterStatisticsResponse(BaseModel):
    statistics: List[ChapterStatistics]
    total_solved_problems: int  # 전체 푼 문제 수
    total_accuracy_rate: float  # 전체 정답률
