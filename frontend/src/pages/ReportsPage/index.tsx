import { Box, Typography } from "@mui/material";

import { pageBackground, textPrimary, textSecondary } from "./constants";
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
      <Box sx={{ maxWidth: 1320, mx: "auto", px: { xs: 2, md: 4 }, py: { xs: 3, md: 4 } }}>
        <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", mb: 5, gap: 2, flexWrap: "wrap" }}>
          <Box>
            <Typography variant="overline" sx={{ color: "primary.main", fontWeight: 800, letterSpacing: "0.12em" }}>
              Scholar Pro
            </Typography>
            <Typography variant="h4" sx={{ color: textPrimary }}>
              Reportes Academicos
            </Typography>
            <Typography variant="body2" sx={{ color: textSecondary, mt: 0.75 }}>
              Visualiza actividad estudiantil y tendencias por tema en una reticula editorial de lectura rapida.
            </Typography>
          </Box>
          <Typography sx={{ fontSize: 13, fontWeight: 700, color: textSecondary, letterSpacing: "0.08em", textTransform: "uppercase" }}>
            Analitica institucional
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

        <Box sx={{ mt: { xs: 5, md: 7 } }}>
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
    </Box>
  );
}
