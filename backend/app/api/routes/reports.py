from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_teacher, get_db, get_reports_service
from app.models.user import User
from app.schemas.report import (
    ReportsOverviewOut,
    StudentReportListItem,
    StudentReportSummaryOut,
    StudentWeeklyActivityOut,
    TopicReportSummaryOut,
    TopicTrendOut,
)
from app.services.reports_service import ReportsService

router = APIRouter()


@router.get("/reports/overview", response_model=ReportsOverviewOut)
def get_reports_overview(
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_teacher),
    reports_service: ReportsService = Depends(get_reports_service),
) -> ReportsOverviewOut:
    try:
        return reports_service.get_overview(db=db, start=start, end=end)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/reports/students", response_model=list[StudentReportListItem])
def list_report_students(
    search: str | None = Query(default=None),
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_teacher),
    reports_service: ReportsService = Depends(get_reports_service),
) -> list[StudentReportListItem]:
    try:
        return reports_service.list_students(db=db, start=start, end=end, search=search)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/reports/students/{user_id}/summary", response_model=StudentReportSummaryOut)
def get_student_report_summary(
    user_id: str,
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_teacher),
    reports_service: ReportsService = Depends(get_reports_service),
) -> StudentReportSummaryOut:
    try:
        result = reports_service.get_student_summary(db=db, user_id=user_id, start=start, end=end)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if result is None:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado.")
    return result


@router.get("/reports/students/{user_id}/weekly-activity", response_model=StudentWeeklyActivityOut)
def get_student_weekly_activity(
    user_id: str,
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_teacher),
    reports_service: ReportsService = Depends(get_reports_service),
) -> StudentWeeklyActivityOut:
    try:
        result = reports_service.get_student_weekly_activity(
            db=db,
            user_id=user_id,
            start=start,
            end=end,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if result is None:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado.")
    return result


@router.get("/reports/topics/summary", response_model=list[TopicReportSummaryOut])
def list_topic_summaries(
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_teacher),
    reports_service: ReportsService = Depends(get_reports_service),
) -> list[TopicReportSummaryOut]:
    try:
        return reports_service.list_topic_summaries(db=db, start=start, end=end)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/reports/topics/{topic}/trend", response_model=TopicTrendOut)
def get_topic_trend(
    topic: str,
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    days: int = Query(default=7, ge=1, le=31),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_teacher),
    reports_service: ReportsService = Depends(get_reports_service),
) -> TopicTrendOut:
    try:
        return reports_service.get_topic_trend(
            db=db,
            topic=topic,
            start=start,
            end=end,
            days=days,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
