import { useEffect, useMemo, useState } from "react";

import {
  getReportStudents,
  getStudentReportSummary,
  getStudentWeeklyActivity,
  getTopicReportSummaries,
  getTopicTrend,
} from "../../../api/client";
import type {
  StudentReportListItem,
  StudentReportSummary,
  StudentWeeklyActivity,
  TopicReportSummary,
  TopicTrend,
} from "../../../types/api";
import { formatDateInput } from "../utils";

export function useReportsDashboard() {
  const today = useMemo(() => new Date(), []);
  const defaultEnd = useMemo(() => formatDateInput(today), [today]);
  const defaultStart = useMemo(() => {
    const copy = new Date(today);
    copy.setDate(copy.getDate() - 29);
    return formatDateInput(copy);
  }, [today]);

  const [search, setSearch] = useState("");
  const [draftStart, setDraftStart] = useState(defaultStart);
  const [draftEnd, setDraftEnd] = useState(defaultEnd);
  const [range, setRange] = useState({ start: defaultStart, end: defaultEnd });

  const [students, setStudents] = useState<StudentReportListItem[]>([]);
  const [selectedStudentId, setSelectedStudentId] = useState<string | null>(null);
  const [studentSummary, setStudentSummary] = useState<StudentReportSummary | null>(null);
  const [studentWeeklyActivity, setStudentWeeklyActivity] =
    useState<StudentWeeklyActivity | null>(null);
  const [topicSummaries, setTopicSummaries] = useState<TopicReportSummary[]>([]);
  const [selectedTopic, setSelectedTopic] = useState<TopicReportSummary["topic"]>("derivative");
  const [topicTrend, setTopicTrend] = useState<TopicTrend | null>(null);

  const [isStudentsLoading, setIsStudentsLoading] = useState(false);
  const [isStudentMetricsLoading, setIsStudentMetricsLoading] = useState(false);
  const [isTopicsLoading, setIsTopicsLoading] = useState(false);
  const [isTopicTrendLoading, setIsTopicTrendLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadStudents() {
      setIsStudentsLoading(true);
      try {
        const data = await getReportStudents({
          start: range.start,
          end: range.end,
          search: search.trim() || undefined,
        });

        if (!cancelled) {
          setStudents(data);
          setSelectedStudentId((current) => {
            if (current && data.some((student) => student.user_id === current)) {
              return current;
            }
            return data[0]?.user_id ?? null;
          });
        }
      } catch (nextError) {
        if (!cancelled) {
          setError(
            nextError instanceof Error
              ? nextError.message
              : "No se pudo cargar el listado de estudiantes.",
          );
        }
      } finally {
        if (!cancelled) {
          setIsStudentsLoading(false);
        }
      }
    }

    void loadStudents();

    return () => {
      cancelled = true;
    };
  }, [range, search]);

  useEffect(() => {
    if (!selectedStudentId) {
      setStudentSummary(null);
      setStudentWeeklyActivity(null);
      return;
    }

    let cancelled = false;
    const currentStudentId = selectedStudentId;

    async function loadStudentMetrics() {
      setIsStudentMetricsLoading(true);
      try {
        const [summary, weekly] = await Promise.all([
          getStudentReportSummary({
            userId: currentStudentId,
            start: range.start,
            end: range.end,
          }),
          getStudentWeeklyActivity({
            userId: currentStudentId,
            start: range.start,
            end: range.end,
          }),
        ]);

        if (!cancelled) {
          setStudentSummary(summary);
          setStudentWeeklyActivity(weekly);
        }
      } catch (nextError) {
        if (!cancelled) {
          setError(
            nextError instanceof Error
              ? nextError.message
              : "No se pudieron cargar las metricas del estudiante.",
          );
        }
      } finally {
        if (!cancelled) {
          setIsStudentMetricsLoading(false);
        }
      }
    }

    void loadStudentMetrics();

    return () => {
      cancelled = true;
    };
  }, [range, selectedStudentId]);

  useEffect(() => {
    let cancelled = false;

    async function loadTopics() {
      setIsTopicsLoading(true);
      try {
        const data = await getTopicReportSummaries({
          start: range.start,
          end: range.end,
        });

        if (!cancelled) {
          setTopicSummaries(data);
          setSelectedTopic((current) => {
            if (data.some((topic) => topic.topic === current)) {
              return current;
            }
            return data[0]?.topic ?? "derivative";
          });
        }
      } catch (nextError) {
        if (!cancelled) {
          setError(
            nextError instanceof Error
              ? nextError.message
              : "No se pudieron cargar las metricas por tema.",
          );
        }
      } finally {
        if (!cancelled) {
          setIsTopicsLoading(false);
        }
      }
    }

    void loadTopics();

    return () => {
      cancelled = true;
    };
  }, [range]);

  useEffect(() => {
    let cancelled = false;

    async function loadTopicTrend() {
      setIsTopicTrendLoading(true);
      try {
        const data = await getTopicTrend({
          topic: selectedTopic,
          start: range.start,
          end: range.end,
          days: 7,
        });

        if (!cancelled) {
          setTopicTrend(data);
        }
      } catch (nextError) {
        if (!cancelled) {
          setError(
            nextError instanceof Error
              ? nextError.message
              : "No se pudo cargar la tendencia del tema.",
          );
        }
      } finally {
        if (!cancelled) {
          setIsTopicTrendLoading(false);
        }
      }
    }

    void loadTopicTrend();

    return () => {
      cancelled = true;
    };
  }, [range, selectedTopic]);

  const selectedStudent = useMemo(
    () => students.find((student) => student.user_id === selectedStudentId) ?? null,
    [selectedStudentId, students],
  );

  const selectedTopicSummary = useMemo(
    () => topicSummaries.find((topic) => topic.topic === selectedTopic) ?? null,
    [selectedTopic, topicSummaries],
  );

  const weeklyChartData = useMemo(
    () =>
      studentWeeklyActivity?.series.map((point) => ({
        name: point.label,
        total: point.queries + point.exercises,
      })) ?? [],
    [studentWeeklyActivity],
  );

  const topicTrendData = useMemo(
    () =>
      topicTrend?.series.map((point) => ({
        name: point.label,
        preguntas: point.questions,
      })) ?? [],
    [topicTrend],
  );

  function applyFilters() {
    setError(null);
    if (!draftStart || !draftEnd) {
      setError("Selecciona una fecha de inicio y una fecha de fin.");
      return;
    }
    if (draftStart > draftEnd) {
      setError("La fecha de inicio no puede ser mayor que la fecha de fin.");
      return;
    }
    setRange({ start: draftStart, end: draftEnd });
  }

  return {
    draftEnd,
    draftStart,
    error,
    isStudentMetricsLoading,
    isStudentsLoading,
    isTopicTrendLoading,
    isTopicsLoading,
    range,
    search,
    selectedStudent,
    selectedStudentId,
    selectedTopic,
    selectedTopicSummary,
    studentSummary,
    students,
    topicSummaries,
    topicTrendData,
    weeklyChartData,
    applyFilters,
    clearError: () => setError(null),
    setDraftEnd,
    setDraftStart,
    setSearch,
    setSelectedStudentId,
    setSelectedTopic,
  };
}
