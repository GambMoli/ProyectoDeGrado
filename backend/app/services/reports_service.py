from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from math import ceil

from sqlalchemy import distinct, func, or_, select
from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.exercise import Exercise
from app.models.message import Message
from app.models.topic_metric_event import TopicMetricEvent
from app.models.user import User
from app.schemas.enums import ExerciseStatus, MessageRole
from app.schemas.report import (
    ReportPeriod,
    ReportsOverviewOut,
    StudentReportListItem,
    StudentReportSummaryOut,
    StudentWeeklyActivityOut,
    StudentWeeklyActivityPoint,
    TopicReportSummaryOut,
    TopicTrendOut,
    TopicTrendPoint,
)


_FAILED_EXERCISE_STATUSES = (
    ExerciseStatus.OCR_FAILED.value,
    ExerciseStatus.PARSE_FAILED.value,
    ExerciseStatus.SOLVER_FAILED.value,
)
_QUESTION_INTERACTION = "question"
_GENERATED_INTERACTION = "exercise_generated"


@dataclass(frozen=True)
class ResolvedPeriod:
    start_date: date
    end_date: date
    start_dt: datetime
    end_dt: datetime

    @property
    def weeks(self) -> int:
        span_days = (self.end_date - self.start_date).days + 1
        return max(1, ceil(span_days / 7))

    @property
    def days(self) -> int:
        return (self.end_date - self.start_date).days + 1

    def as_schema(self) -> ReportPeriod:
        return ReportPeriod(start=self.start_date, end=self.end_date)


class ReportsService:
    _topic_labels = {
        "limit": "Limites",
        "derivative": "Derivadas",
        "integral": "Integrales",
        "equation": "Ecuaciones",
    }
    _topic_order = ("limit", "derivative", "integral", "equation")
    _weekday_labels = ("Lun", "Mar", "Mie", "Jue", "Vie", "Sab", "Dom")

    def get_overview(
        self,
        *,
        db: Session,
        start: date | None = None,
        end: date | None = None,
    ) -> ReportsOverviewOut:
        period = self._resolve_period(start=start, end=end)
        user_messages_subquery = self._user_messages_subquery(period=period).subquery()

        total_queries = db.scalar(select(func.count()).select_from(user_messages_subquery)) or 0
        active_students = (
            db.scalar(
                select(func.count(distinct(user_messages_subquery.c.user_id))).select_from(user_messages_subquery)
            )
            or 0
        )
        resolved_exercises = self._count_exercises(
            db=db,
            period=period,
            statuses=(ExerciseStatus.SOLVED.value,),
        )
        failed_exercises = self._count_exercises(
            db=db,
            period=period,
            statuses=_FAILED_EXERCISE_STATUSES,
        )
        total_scored_exercises = resolved_exercises + failed_exercises
        ai_resolution_rate = (
            round(resolved_exercises / total_scored_exercises, 4) if total_scored_exercises else 0.0
        )
        avg_queries_per_active_student = round(total_queries / active_students, 2) if active_students else 0.0

        return ReportsOverviewOut(
            period=period.as_schema(),
            active_students=active_students,
            total_queries=total_queries,
            resolved_exercises=resolved_exercises,
            failed_exercises=failed_exercises,
            ai_resolution_rate=ai_resolution_rate,
            avg_queries_per_active_student=avg_queries_per_active_student,
        )

    def list_students(
        self,
        *,
        db: Session,
        start: date | None = None,
        end: date | None = None,
        search: str | None = None,
    ) -> list[StudentReportListItem]:
        period = self._resolve_period(start=start, end=end)
        message_stats = (
            select(
                Conversation.user_id.label("user_id"),
                func.count(Message.id).label("message_count"),
                func.count(distinct(Message.conversation_id)).label("conversation_count"),
                func.max(Message.created_at).label("last_activity_at"),
            )
            .join(Conversation, Message.conversation_id == Conversation.id)
            .where(
                Message.role == MessageRole.USER.value,
                Message.created_at >= period.start_dt,
                Message.created_at <= period.end_dt,
            )
            .group_by(Conversation.user_id)
            .subquery()
        )

        exercise_stats = (
            select(
                Conversation.user_id.label("user_id"),
                func.count(Exercise.id).label("exercise_count"),
            )
            .join(Conversation, Exercise.conversation_id == Conversation.id)
            .where(
                Exercise.created_at >= period.start_dt,
                Exercise.created_at <= period.end_dt,
            )
            .group_by(Conversation.user_id)
            .subquery()
        )

        statement = (
            select(
                User.id,
                User.display_name,
                User.email,
                User.is_anonymous,
                func.coalesce(message_stats.c.conversation_count, 0).label("conversation_count"),
                func.coalesce(message_stats.c.message_count, 0).label("message_count"),
                func.coalesce(exercise_stats.c.exercise_count, 0).label("exercise_count"),
                message_stats.c.last_activity_at,
            )
            .outerjoin(message_stats, message_stats.c.user_id == User.id)
            .outerjoin(exercise_stats, exercise_stats.c.user_id == User.id)
            .where(
                or_(
                    message_stats.c.user_id.is_not(None),
                    exercise_stats.c.user_id.is_not(None),
                )
            )
            .order_by(message_stats.c.last_activity_at.desc(), User.display_name.asc())
        )

        normalized_search = (search or "").strip().lower()
        if normalized_search:
            statement = statement.where(func.lower(User.display_name).like(f"%{normalized_search}%"))

        rows = db.execute(statement).all()
        return [
            StudentReportListItem(
                user_id=row.id,
                display_name=row.display_name,
                email=row.email,
                is_anonymous=row.is_anonymous,
                conversation_count=int(row.conversation_count or 0),
                message_count=int(row.message_count or 0),
                exercise_count=int(row.exercise_count or 0),
                last_activity_at=self._coerce_datetime(row.last_activity_at),
            )
            for row in rows
        ]

    def get_student_summary(
        self,
        *,
        db: Session,
        user_id: str,
        start: date | None = None,
        end: date | None = None,
    ) -> StudentReportSummaryOut | None:
        period = self._resolve_period(start=start, end=end)
        user = db.get(User, user_id)
        if user is None:
            return None

        message_filters = (
            Message.role == MessageRole.USER.value,
            Message.created_at >= period.start_dt,
            Message.created_at <= period.end_dt,
            Conversation.user_id == user_id,
        )

        total_queries = (
            db.scalar(
                select(func.count(Message.id))
                .join(Conversation, Message.conversation_id == Conversation.id)
                .where(*message_filters)
            )
            or 0
        )
        total_conversations = (
            db.scalar(
                select(func.count(distinct(Message.conversation_id)))
                .join(Conversation, Message.conversation_id == Conversation.id)
                .where(*message_filters)
            )
            or 0
        )
        active_days = (
            db.scalar(
                select(func.count(distinct(func.date(Message.created_at))))
                .join(Conversation, Message.conversation_id == Conversation.id)
                .where(*message_filters)
            )
            or 0
        )
        first_activity_at = self._coerce_datetime(
            db.scalar(
                select(func.min(Message.created_at))
                .join(Conversation, Message.conversation_id == Conversation.id)
                .where(*message_filters)
            )
        )
        last_activity_at = self._coerce_datetime(
            db.scalar(
                select(func.max(Message.created_at))
                .join(Conversation, Message.conversation_id == Conversation.id)
                .where(*message_filters)
            )
        )

        total_exercises = (
            db.scalar(
                select(func.count(Exercise.id))
                .join(Conversation, Exercise.conversation_id == Conversation.id)
                .where(
                    Conversation.user_id == user_id,
                    Exercise.created_at >= period.start_dt,
                    Exercise.created_at <= period.end_dt,
                )
            )
            or 0
        )
        resolved_exercises = (
            db.scalar(
                select(func.count(Exercise.id))
                .join(Conversation, Exercise.conversation_id == Conversation.id)
                .where(
                    Conversation.user_id == user_id,
                    Exercise.created_at >= period.start_dt,
                    Exercise.created_at <= period.end_dt,
                    Exercise.status == ExerciseStatus.SOLVED.value,
                )
            )
            or 0
        )
        failed_exercises = (
            db.scalar(
                select(func.count(Exercise.id))
                .join(Conversation, Exercise.conversation_id == Conversation.id)
                .where(
                    Conversation.user_id == user_id,
                    Exercise.created_at >= period.start_dt,
                    Exercise.created_at <= period.end_dt,
                    Exercise.status.in_(_FAILED_EXERCISE_STATUSES),
                )
            )
            or 0
        )

        total_scored_exercises = resolved_exercises + failed_exercises
        ai_resolution_rate = (
            round(resolved_exercises / total_scored_exercises, 4) if total_scored_exercises else 0.0
        )
        usage_frequency_days_per_week = round(active_days / period.weeks, 2) if active_days else 0.0
        activity_span_hours_estimate = self._activity_span_hours(
            first_activity_at=first_activity_at,
            last_activity_at=last_activity_at,
        )

        return StudentReportSummaryOut(
            user_id=user.id,
            display_name=user.display_name,
            email=user.email,
            is_anonymous=user.is_anonymous,
            period=period.as_schema(),
            usage_frequency_days_per_week=usage_frequency_days_per_week,
            total_queries=int(total_queries),
            total_conversations=int(total_conversations),
            total_exercises=int(total_exercises),
            resolved_exercises=int(resolved_exercises),
            failed_exercises=int(failed_exercises),
            ai_resolution_rate=ai_resolution_rate,
            activity_span_hours_estimate=activity_span_hours_estimate,
            first_activity_at=first_activity_at,
            last_activity_at=last_activity_at,
        )

    def get_student_weekly_activity(
        self,
        *,
        db: Session,
        user_id: str,
        start: date | None = None,
        end: date | None = None,
    ) -> StudentWeeklyActivityOut | None:
        period = self._resolve_period(start=start, end=end)
        user = db.get(User, user_id)
        if user is None:
            return None

        message_rows = db.scalars(
            select(Message.created_at)
            .join(Conversation, Message.conversation_id == Conversation.id)
            .where(
                Conversation.user_id == user_id,
                Message.role == MessageRole.USER.value,
                Message.created_at >= period.start_dt,
                Message.created_at <= period.end_dt,
            )
            .order_by(Message.created_at.asc())
        ).all()

        exercise_rows = db.scalars(
            select(Exercise.created_at)
            .join(Conversation, Exercise.conversation_id == Conversation.id)
            .where(
                Conversation.user_id == user_id,
                Exercise.created_at >= period.start_dt,
                Exercise.created_at <= period.end_dt,
            )
            .order_by(Exercise.created_at.asc())
        ).all()

        series = [
            StudentWeeklyActivityPoint(label=f"Sem {index}", queries=0, exercises=0)
            for index in range(1, period.weeks + 1)
        ]

        for created_at in message_rows:
            self._increment_weekly_counter(
                series=series,
                created_at=self._coerce_datetime(created_at),
                start_date=period.start_date,
                field="queries",
            )

        for created_at in exercise_rows:
            self._increment_weekly_counter(
                series=series,
                created_at=self._coerce_datetime(created_at),
                start_date=period.start_date,
                field="exercises",
            )

        return StudentWeeklyActivityOut(
            user_id=user_id,
            period=period.as_schema(),
            series=series,
        )

    def list_topic_summaries(
        self,
        *,
        db: Session,
        start: date | None = None,
        end: date | None = None,
    ) -> list[TopicReportSummaryOut]:
        period = self._resolve_period(start=start, end=end)
        previous_period = self._previous_period(period)
        active_students = self._count_active_students(db=db, period=period)

        question_counts = self._topic_counts(
            db=db,
            period=period,
            interaction_type=_QUESTION_INTERACTION,
        )
        generated_counts = self._topic_counts(
            db=db,
            period=period,
            interaction_type=_GENERATED_INTERACTION,
        )
        student_counts = self._topic_student_counts(db=db, period=period)

        previous_question_counts = self._topic_counts(
            db=db,
            period=previous_period,
            interaction_type=_QUESTION_INTERACTION,
        )
        previous_generated_counts = self._topic_counts(
            db=db,
            period=previous_period,
            interaction_type=_GENERATED_INTERACTION,
        )

        summaries: list[TopicReportSummaryOut] = []
        for topic in self._topic_order:
            questions_count = question_counts[topic]
            exercises_generated = generated_counts[topic]
            topic_student_count = student_counts[topic]
            active_students_ratio = (
                round(topic_student_count / active_students, 4) if active_students else 0.0
            )

            summaries.append(
                TopicReportSummaryOut(
                    topic=topic,
                    label=self._topic_labels[topic],
                    questions_count=questions_count,
                    exercises_generated=exercises_generated,
                    active_students_ratio=active_students_ratio,
                    interaction_level=self._interaction_level(
                        questions_count=questions_count,
                        exercises_generated=exercises_generated,
                        active_students_ratio=active_students_ratio,
                    ),
                    questions_change_ratio=self._compute_change_ratio(
                        current=questions_count,
                        previous=previous_question_counts[topic],
                    ),
                    exercises_change_ratio=self._compute_change_ratio(
                        current=exercises_generated,
                        previous=previous_generated_counts[topic],
                    ),
                )
            )

        return summaries

    def get_topic_trend(
        self,
        *,
        db: Session,
        topic: str,
        start: date | None = None,
        end: date | None = None,
        days: int = 7,
    ) -> TopicTrendOut:
        resolved_topic = self._resolve_topic(topic)
        period = self._resolve_period(start=start, end=end)
        if days <= 0:
            raise ValueError("El numero de dias debe ser mayor a cero.")

        trend_start = max(period.start_date, period.end_date - timedelta(days=days - 1))
        trend_period = self._build_period(trend_start, period.end_date)
        daily_counts = self._topic_daily_question_counts(
            db=db,
            period=trend_period,
            topic=resolved_topic,
        )

        series: list[TopicTrendPoint] = []
        current_day = trend_period.start_date
        while current_day <= trend_period.end_date:
            series.append(
                TopicTrendPoint(
                    date=current_day,
                    label=self._weekday_labels[current_day.weekday()],
                    questions=daily_counts.get(current_day, 0),
                )
            )
            current_day += timedelta(days=1)

        return TopicTrendOut(
            topic=resolved_topic,
            label=self._topic_labels[resolved_topic],
            period=trend_period.as_schema(),
            series=series,
        )

    def _resolve_period(self, *, start: date | None, end: date | None) -> ResolvedPeriod:
        today = datetime.now(timezone.utc).date()
        end_date = end or today
        start_date = start or (end_date - timedelta(days=29))
        return self._build_period(start_date, end_date)

    def _build_period(self, start_date: date, end_date: date) -> ResolvedPeriod:
        if start_date > end_date:
            raise ValueError("La fecha de inicio no puede ser mayor que la fecha de fin.")

        start_dt = datetime.combine(start_date, time.min, tzinfo=timezone.utc)
        end_dt = datetime.combine(end_date, time.max, tzinfo=timezone.utc)
        return ResolvedPeriod(
            start_date=start_date,
            end_date=end_date,
            start_dt=start_dt,
            end_dt=end_dt,
        )

    def _previous_period(self, period: ResolvedPeriod) -> ResolvedPeriod:
        previous_end = period.start_date - timedelta(days=1)
        previous_start = previous_end - timedelta(days=period.days - 1)
        return self._build_period(previous_start, previous_end)

    def _user_messages_subquery(self, *, period: ResolvedPeriod):
        return (
            select(
                Message.id.label("message_id"),
                Conversation.user_id.label("user_id"),
            )
            .join(Conversation, Message.conversation_id == Conversation.id)
            .where(
                Message.role == MessageRole.USER.value,
                Message.created_at >= period.start_dt,
                Message.created_at <= period.end_dt,
            )
        )

    def _count_exercises(self, *, db: Session, period: ResolvedPeriod, statuses: tuple[str, ...]) -> int:
        return (
            db.scalar(
                select(func.count(Exercise.id)).where(
                    Exercise.created_at >= period.start_dt,
                    Exercise.created_at <= period.end_dt,
                    Exercise.status.in_(statuses),
                )
            )
            or 0
        )

    def _count_active_students(self, *, db: Session, period: ResolvedPeriod) -> int:
        active_message_users = (
            select(distinct(Conversation.user_id).label("user_id"))
            .select_from(Message)
            .join(Conversation, Message.conversation_id == Conversation.id)
            .where(
                Message.role == MessageRole.USER.value,
                Message.created_at >= period.start_dt,
                Message.created_at <= period.end_dt,
            )
        )
        active_exercise_users = (
            select(distinct(Conversation.user_id).label("user_id"))
            .select_from(Exercise)
            .join(Conversation, Exercise.conversation_id == Conversation.id)
            .where(
                Exercise.created_at >= period.start_dt,
                Exercise.created_at <= period.end_dt,
            )
        )
        active_users = active_message_users.union(active_exercise_users).subquery()
        return db.scalar(select(func.count()).select_from(active_users)) or 0

    def _topic_counts(
        self,
        *,
        db: Session,
        period: ResolvedPeriod,
        interaction_type: str,
    ) -> dict[str, int]:
        event_rows = db.execute(
            select(TopicMetricEvent.topic, func.count(TopicMetricEvent.id))
            .where(
                TopicMetricEvent.created_at >= period.start_dt,
                TopicMetricEvent.created_at <= period.end_dt,
                TopicMetricEvent.interaction_type == interaction_type,
                TopicMetricEvent.topic.in_(self._topic_order),
            )
            .group_by(TopicMetricEvent.topic)
        ).all()
        event_counts = {topic: int(count or 0) for topic, count in event_rows}

        fallback_counts = self._topic_exercise_counts(db=db, period=period)
        combined: dict[str, int] = {}
        for topic in self._topic_order:
            combined[topic] = event_counts.get(topic, 0) or fallback_counts.get(topic, 0)
        return combined

    def _topic_student_counts(self, *, db: Session, period: ResolvedPeriod) -> dict[str, int]:
        event_rows = db.execute(
            select(TopicMetricEvent.topic, func.count(distinct(TopicMetricEvent.user_id)))
            .where(
                TopicMetricEvent.created_at >= period.start_dt,
                TopicMetricEvent.created_at <= period.end_dt,
                TopicMetricEvent.topic.in_(self._topic_order),
            )
            .group_by(TopicMetricEvent.topic)
        ).all()
        event_counts = {topic: int(count or 0) for topic, count in event_rows}

        fallback_counts = self._topic_exercise_student_counts(db=db, period=period)
        combined: dict[str, int] = {}
        for topic in self._topic_order:
            combined[topic] = event_counts.get(topic, 0) or fallback_counts.get(topic, 0)
        return combined

    def _topic_exercise_counts(self, *, db: Session, period: ResolvedPeriod) -> dict[str, int]:
        rows = db.execute(
            select(Exercise.detected_problem_type, func.count(Exercise.id))
            .where(
                Exercise.created_at >= period.start_dt,
                Exercise.created_at <= period.end_dt,
                Exercise.detected_problem_type.in_(self._topic_order),
            )
            .group_by(Exercise.detected_problem_type)
        ).all()
        return {str(topic): int(count or 0) for topic, count in rows if topic}

    def _topic_exercise_student_counts(self, *, db: Session, period: ResolvedPeriod) -> dict[str, int]:
        rows = db.execute(
            select(Exercise.detected_problem_type, func.count(distinct(Conversation.user_id)))
            .join(Conversation, Exercise.conversation_id == Conversation.id)
            .where(
                Exercise.created_at >= period.start_dt,
                Exercise.created_at <= period.end_dt,
                Exercise.detected_problem_type.in_(self._topic_order),
            )
            .group_by(Exercise.detected_problem_type)
        ).all()
        return {str(topic): int(count or 0) for topic, count in rows if topic}

    def _topic_daily_question_counts(
        self,
        *,
        db: Session,
        period: ResolvedPeriod,
        topic: str,
    ) -> dict[date, int]:
        event_rows = db.execute(
            select(func.date(TopicMetricEvent.created_at), func.count(TopicMetricEvent.id))
            .where(
                TopicMetricEvent.created_at >= period.start_dt,
                TopicMetricEvent.created_at <= period.end_dt,
                TopicMetricEvent.interaction_type == _QUESTION_INTERACTION,
                TopicMetricEvent.topic == topic,
            )
            .group_by(func.date(TopicMetricEvent.created_at))
        ).all()
        if event_rows:
            return {
                self._coerce_date(day): int(count or 0)
                for day, count in event_rows
                if self._coerce_date(day) is not None
            }

        exercise_rows = db.execute(
            select(func.date(Exercise.created_at), func.count(Exercise.id))
            .where(
                Exercise.created_at >= period.start_dt,
                Exercise.created_at <= period.end_dt,
                Exercise.detected_problem_type == topic,
            )
            .group_by(func.date(Exercise.created_at))
        ).all()
        return {
            self._coerce_date(day): int(count or 0)
            for day, count in exercise_rows
            if self._coerce_date(day) is not None
        }

    def _resolve_topic(self, topic: str) -> str:
        normalized = (topic or "").strip().lower()
        if normalized not in self._topic_labels:
            raise ValueError("El tema solicitado no esta soportado en reportes.")
        return normalized

    @staticmethod
    def _compute_change_ratio(*, current: int, previous: int) -> float | None:
        if previous <= 0:
            return None
        return round((current - previous) / previous, 4)

    @staticmethod
    def _interaction_level(
        *,
        questions_count: int,
        exercises_generated: int,
        active_students_ratio: float,
    ) -> str:
        if (
            active_students_ratio >= 0.7
            or questions_count >= 25
            or exercises_generated >= 25
        ):
            return "high"
        if (
            active_students_ratio >= 0.35
            or questions_count >= 8
            or exercises_generated >= 8
        ):
            return "medium"
        return "low"

    @staticmethod
    def _coerce_datetime(value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @staticmethod
    def _coerce_date(value: object) -> date | None:
        if value is None:
            return None
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            return date.fromisoformat(value)
        return None

    @staticmethod
    def _activity_span_hours(*, first_activity_at: datetime | None, last_activity_at: datetime | None) -> float:
        if first_activity_at is None or last_activity_at is None:
            return 0.0
        hours = (last_activity_at - first_activity_at).total_seconds() / 3600
        return round(max(0.0, hours), 2)

    @staticmethod
    def _increment_weekly_counter(
        *,
        series: list[StudentWeeklyActivityPoint],
        created_at: datetime | None,
        start_date: date,
        field: str,
    ) -> None:
        if created_at is None:
            return
        week_index = (created_at.date() - start_date).days // 7
        if week_index < 0 or week_index >= len(series):
            return
        point = series[week_index]
        current_value = getattr(point, field)
        setattr(point, field, current_value + 1)
