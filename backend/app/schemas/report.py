from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel


class ReportPeriod(BaseModel):
    start: date
    end: date


class ReportsOverviewOut(BaseModel):
    period: ReportPeriod
    active_students: int
    total_queries: int
    resolved_exercises: int
    failed_exercises: int
    ai_resolution_rate: float
    avg_queries_per_active_student: float


class StudentReportListItem(BaseModel):
    user_id: str
    display_name: str
    email: str | None = None
    is_anonymous: bool
    conversation_count: int
    message_count: int
    exercise_count: int
    last_activity_at: datetime | None = None


class StudentReportSummaryOut(BaseModel):
    user_id: str
    display_name: str
    email: str | None = None
    is_anonymous: bool
    period: ReportPeriod
    usage_frequency_days_per_week: float
    total_queries: int
    total_conversations: int
    total_exercises: int
    resolved_exercises: int
    failed_exercises: int
    ai_resolution_rate: float
    activity_span_hours_estimate: float
    first_activity_at: datetime | None = None
    last_activity_at: datetime | None = None


class StudentWeeklyActivityPoint(BaseModel):
    label: str
    queries: int
    exercises: int


class StudentWeeklyActivityOut(BaseModel):
    user_id: str
    period: ReportPeriod
    series: list[StudentWeeklyActivityPoint]


class TopicReportSummaryOut(BaseModel):
    topic: str
    label: str
    questions_count: int
    exercises_generated: int
    active_students_ratio: float
    interaction_level: str
    questions_change_ratio: float | None = None
    exercises_change_ratio: float | None = None


class TopicTrendPoint(BaseModel):
    date: date
    label: str
    questions: int


class TopicTrendOut(BaseModel):
    topic: str
    label: str
    period: ReportPeriod
    series: list[TopicTrendPoint]
