from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.models import Base, Conversation, Exercise, Message, TopicMetricEvent, User
from app.schemas.report import (
    ReportsOverviewOut,
    StudentReportSummaryOut,
    StudentWeeklyActivityOut,
    TopicReportSummaryOut,
    TopicTrendOut,
)
from app.services.reports_service import ReportsService


def build_session() -> Session:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def seed_data(db: Session) -> tuple[User, User]:
    ana = User(id="user-ana", display_name="Ana Martinez", is_anonymous=False)
    carlos = User(id="user-carlos", display_name="Carlos Ramirez", is_anonymous=True)
    db.add_all([ana, carlos])

    ana_conversation_1 = Conversation(
        id="conv-ana-1",
        user_id=ana.id,
        title="Integrales",
        created_at=datetime(2026, 4, 1, 14, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 4, 3, 18, 0, tzinfo=timezone.utc),
        agent_state={},
    )
    ana_conversation_2 = Conversation(
        id="conv-ana-2",
        user_id=ana.id,
        title="Derivadas",
        created_at=datetime(2026, 4, 9, 15, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 4, 10, 12, 0, tzinfo=timezone.utc),
        agent_state={},
    )
    carlos_conversation = Conversation(
        id="conv-carlos-1",
        user_id=carlos.id,
        title="Limites",
        created_at=datetime(2026, 4, 8, 10, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 4, 8, 10, 30, tzinfo=timezone.utc),
        agent_state={},
    )
    db.add_all([ana_conversation_1, ana_conversation_2, carlos_conversation])

    messages = [
        Message(
            id="msg-ana-1",
            conversation_id=ana_conversation_1.id,
            role="user",
            content="Necesito ayuda con integrales",
            created_at=datetime(2026, 4, 1, 14, 5, tzinfo=timezone.utc),
        ),
        Message(
            id="msg-ana-2",
            conversation_id=ana_conversation_1.id,
            role="assistant",
            content="Vamos con un ejercicio",
            created_at=datetime(2026, 4, 1, 14, 6, tzinfo=timezone.utc),
        ),
        Message(
            id="msg-ana-3",
            conversation_id=ana_conversation_1.id,
            role="user",
            content="No entendi el paso 2",
            created_at=datetime(2026, 4, 3, 18, 0, tzinfo=timezone.utc),
        ),
        Message(
            id="msg-ana-4",
            conversation_id=ana_conversation_2.id,
            role="user",
            content="Ahora quiero practicar derivadas",
            created_at=datetime(2026, 4, 10, 12, 0, tzinfo=timezone.utc),
        ),
        Message(
            id="msg-carlos-1",
            conversation_id=carlos_conversation.id,
            role="user",
            content="Explicame limites",
            created_at=datetime(2026, 4, 8, 10, 5, tzinfo=timezone.utc),
        ),
    ]
    db.add_all(messages)

    exercises = [
        Exercise(
            id="ex-ana-1",
            conversation_id=ana_conversation_1.id,
            user_message_id="msg-ana-1",
            assistant_message_id="msg-ana-2",
            source_type="text",
            raw_input="integral",
            detected_problem_type="integral",
            status="solved",
            created_at=datetime(2026, 4, 1, 14, 6, tzinfo=timezone.utc),
        ),
        Exercise(
            id="ex-ana-2",
            conversation_id=ana_conversation_2.id,
            user_message_id="msg-ana-4",
            assistant_message_id=None,
            source_type="text",
            raw_input="derivative",
            detected_problem_type="derivative",
            status="solver_failed",
            created_at=datetime(2026, 4, 10, 12, 1, tzinfo=timezone.utc),
        ),
        Exercise(
            id="ex-carlos-1",
            conversation_id=carlos_conversation.id,
            user_message_id="msg-carlos-1",
            assistant_message_id=None,
            source_type="text",
            raw_input="limit",
            detected_problem_type="limit",
            status="parse_failed",
            created_at=datetime(2026, 4, 8, 10, 6, tzinfo=timezone.utc),
        ),
    ]
    db.add_all(exercises)

    topic_events = [
        TopicMetricEvent(
            id="event-integral-question-current",
            user_id=ana.id,
            conversation_id=ana_conversation_1.id,
            topic="integral",
            interaction_type="question",
            created_at=datetime(2026, 4, 1, 14, 5, tzinfo=timezone.utc),
        ),
        TopicMetricEvent(
            id="event-integral-generated-current",
            user_id=ana.id,
            conversation_id=ana_conversation_1.id,
            topic="integral",
            interaction_type="exercise_generated",
            created_at=datetime(2026, 4, 1, 14, 6, tzinfo=timezone.utc),
        ),
        TopicMetricEvent(
            id="event-derivative-question-current",
            user_id=ana.id,
            conversation_id=ana_conversation_2.id,
            topic="derivative",
            interaction_type="question",
            created_at=datetime(2026, 4, 10, 12, 0, tzinfo=timezone.utc),
        ),
        TopicMetricEvent(
            id="event-derivative-generated-current",
            user_id=ana.id,
            conversation_id=ana_conversation_2.id,
            topic="derivative",
            interaction_type="exercise_generated",
            created_at=datetime(2026, 4, 10, 12, 1, tzinfo=timezone.utc),
        ),
        TopicMetricEvent(
            id="event-integral-question-previous",
            user_id=ana.id,
            conversation_id=ana_conversation_1.id,
            topic="integral",
            interaction_type="question",
            created_at=datetime(2026, 3, 25, 10, 0, tzinfo=timezone.utc),
        ),
        TopicMetricEvent(
            id="event-integral-generated-previous",
            user_id=ana.id,
            conversation_id=ana_conversation_1.id,
            topic="integral",
            interaction_type="exercise_generated",
            created_at=datetime(2026, 3, 25, 10, 5, tzinfo=timezone.utc),
        ),
    ]
    db.add_all(topic_events)
    db.commit()
    return ana, carlos


def test_get_overview_returns_period_metrics() -> None:
    db = build_session()
    seed_data(db)
    service = ReportsService()

    result = service.get_overview(
        db=db,
        start=date(2026, 4, 1),
        end=date(2026, 4, 10),
    )

    assert isinstance(result, ReportsOverviewOut)
    assert result.active_students == 2
    assert result.total_queries == 4
    assert result.resolved_exercises == 1
    assert result.failed_exercises == 2
    assert result.ai_resolution_rate == 0.3333
    assert result.avg_queries_per_active_student == 2.0


def test_list_students_filters_and_orders_active_students() -> None:
    db = build_session()
    ana, _ = seed_data(db)
    service = ReportsService()

    result = service.list_students(
        db=db,
        start=date(2026, 4, 1),
        end=date(2026, 4, 10),
        search="ana",
    )

    assert len(result) == 1
    assert result[0].user_id == ana.id
    assert result[0].conversation_count == 2
    assert result[0].message_count == 3
    assert result[0].exercise_count == 2


def test_get_student_summary_returns_usage_metrics() -> None:
    db = build_session()
    ana, _ = seed_data(db)
    service = ReportsService()

    result = service.get_student_summary(
        db=db,
        user_id=ana.id,
        start=date(2026, 4, 1),
        end=date(2026, 4, 10),
    )

    assert isinstance(result, StudentReportSummaryOut)
    assert result.user_id == ana.id
    assert result.total_queries == 3
    assert result.total_conversations == 2
    assert result.total_exercises == 2
    assert result.resolved_exercises == 1
    assert result.failed_exercises == 1
    assert result.ai_resolution_rate == 0.5
    assert result.usage_frequency_days_per_week == 1.5
    assert result.activity_span_hours_estimate == 213.92


def test_get_student_weekly_activity_groups_events_by_week() -> None:
    db = build_session()
    ana, _ = seed_data(db)
    service = ReportsService()

    result = service.get_student_weekly_activity(
        db=db,
        user_id=ana.id,
        start=date(2026, 4, 1),
        end=date(2026, 4, 14),
    )

    assert isinstance(result, StudentWeeklyActivityOut)
    assert [point.label for point in result.series] == ["Sem 1", "Sem 2"]
    assert result.series[0].queries == 2
    assert result.series[0].exercises == 1
    assert result.series[1].queries == 1
    assert result.series[1].exercises == 1


def test_get_student_summary_returns_none_when_user_is_missing() -> None:
    db = build_session()
    seed_data(db)
    service = ReportsService()

    result = service.get_student_summary(
        db=db,
        user_id="missing-user",
        start=date(2026, 4, 1),
        end=date(2026, 4, 10),
    )

    assert result is None


def test_list_topic_summaries_returns_metrics_for_supported_topics() -> None:
    db = build_session()
    seed_data(db)
    service = ReportsService()

    result = service.list_topic_summaries(
        db=db,
        start=date(2026, 4, 1),
        end=date(2026, 4, 10),
    )

    assert all(isinstance(item, TopicReportSummaryOut) for item in result)
    by_topic = {item.topic: item for item in result}

    assert by_topic["integral"].questions_count == 1
    assert by_topic["integral"].exercises_generated == 1
    assert by_topic["integral"].questions_change_ratio == 0.0
    assert by_topic["integral"].interaction_level in {"low", "medium", "high"}
    assert by_topic["derivative"].questions_count == 1
    assert by_topic["derivative"].exercises_generated == 1
    assert by_topic["limit"].questions_count == 1


def test_get_topic_trend_returns_daily_series() -> None:
    db = build_session()
    seed_data(db)
    service = ReportsService()

    result = service.get_topic_trend(
        db=db,
        topic="integral",
        start=date(2026, 4, 1),
        end=date(2026, 4, 6),
        days=7,
    )

    assert isinstance(result, TopicTrendOut)
    assert len(result.series) == 6
    assert result.topic == "integral"
    assert sum(point.questions for point in result.series) == 1
