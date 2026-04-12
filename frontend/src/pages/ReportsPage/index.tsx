import { Box, Typography } from "@mui/material";

import { pageBackground, textPrimary } from "./constants";
import { StudentReportsSection } from "./components/StudentReportsSection";
import { TopicReportsSection } from "./components/TopicReportsSection";
import { useReportsDashboard } from "./hooks/useReportsDashboard";

export function ReportsPage() {
  const {
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
    clearError,
    setDraftEnd,
    setDraftStart,
    setSearch,
    setSelectedStudentId,
    setSelectedTopic,
  } = useReportsDashboard();

  return (
    <Box sx={{ flexGrow: 1, bgcolor: pageBackground, minHeight: "100%" }}>
      <Box sx={{ maxWidth: 1280, mx: "auto", px: { xs: 2, md: 3 }, py: 4 }}>
        <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 4 }}>
          <Typography sx={{ fontSize: 26, fontWeight: 800, color: textPrimary }}>
            Reportes
          </Typography>
          <Typography sx={{ fontSize: 14, fontWeight: 500, color: "#94A3B8" }}>
            Pagina Principal / Mis cursos / Reportes
          </Typography>
        </Box>

        <StudentReportsSection
          draftEnd={draftEnd}
          draftStart={draftStart}
          error={error}
          isStudentMetricsLoading={isStudentMetricsLoading}
          isStudentsLoading={isStudentsLoading}
          range={range}
          search={search}
          selectedStudent={selectedStudent}
          selectedStudentId={selectedStudentId}
          studentSummary={studentSummary}
          students={students}
          weeklyChartData={weeklyChartData}
          clearError={clearError}
          onApplyFilters={applyFilters}
          onChangeDraftEnd={setDraftEnd}
          onChangeDraftStart={setDraftStart}
          onChangeSearch={setSearch}
          onSelectStudent={setSelectedStudentId}
        />

        <TopicReportsSection
          isTopicTrendLoading={isTopicTrendLoading}
          isTopicsLoading={isTopicsLoading}
          selectedTopic={selectedTopic}
          selectedTopicSummary={selectedTopicSummary}
          topicSummaries={topicSummaries}
          topicTrendData={topicTrendData}
          onSelectTopic={setSelectedTopic}
        />
      </Box>
    </Box>
  );
}
