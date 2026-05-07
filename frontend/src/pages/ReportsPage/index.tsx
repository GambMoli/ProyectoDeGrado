import { Box, Typography } from "@mui/material";
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
    <Box sx={{ flexGrow: 1, bgcolor:"background.default", minHeight: "100%" }}>
      <Box sx={{ maxWidth: 1320, mx: "auto", px: { xs: 2, md: 4 }, py: { xs: 3, md: 4 } }}>
        <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", mb: 5, gap: 3, flexWrap: "wrap" }}>
          <Box>
            <Typography variant="h4" sx={{ color: "text.primary" }}>
              Reportes
            </Typography>
          </Box>
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
