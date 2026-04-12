import Diversity3OutlinedIcon from "@mui/icons-material/Diversity3Outlined";
import DownloadOutlinedIcon from "@mui/icons-material/DownloadOutlined";
import HelpOutlineOutlinedIcon from "@mui/icons-material/HelpOutlineOutlined";
import InsightsOutlinedIcon from "@mui/icons-material/InsightsOutlined";
import PersonOutlineRoundedIcon from "@mui/icons-material/PersonOutlineRounded";
import PlaylistAddCheckRoundedIcon from "@mui/icons-material/PlaylistAddCheckRounded";
import { Box, Button, CircularProgress, Grid, Stack, Typography } from "@mui/material";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { TopicReportSummary } from "../../../types/api";
import { accentBlue, textPrimary, textSecondary } from "../constants";
import { formatChange, formatPercentage, formatWholeNumber, interactionLevelLabel } from "../utils";
import { SectionCard } from "./SectionCard";
import { TopicMetricCard } from "./TopicMetricCard";

interface TopicTrendChartPoint {
  name: string;
  preguntas: number;
}

interface TopicReportsSectionProps {
  isTopicTrendLoading: boolean;
  isTopicsLoading: boolean;
  selectedTopic: TopicReportSummary["topic"];
  selectedTopicSummary: TopicReportSummary | null;
  topicSummaries: TopicReportSummary[];
  topicTrendData: TopicTrendChartPoint[];
  onSelectTopic: (topic: TopicReportSummary["topic"]) => void;
}

export function TopicReportsSection({
  isTopicTrendLoading,
  isTopicsLoading,
  selectedTopic,
  selectedTopicSummary,
  topicSummaries,
  topicTrendData,
  onSelectTopic,
}: TopicReportsSectionProps) {
  return (
    <>
      <Stack direction="row" spacing={1.2} alignItems="center" sx={{ mb: 2.5 }}>
        <InsightsOutlinedIcon sx={{ color: accentBlue, fontSize: 24 }} />
        <Typography sx={{ fontSize: 18, fontWeight: 800, color: textPrimary }}>
          Reportes por Tema
        </Typography>
      </Stack>

      <Grid container spacing={3}>
        <Grid item xs={12} lg={3}>
          <SectionCard sx={{ p: 2.25, height: "100%" }}>
            <Typography sx={{ fontSize: 14, fontWeight: 700, color: "#1E293B", mb: 2 }}>
              TEMAS DEL CURSO
            </Typography>

            {isTopicsLoading ? (
              <Box sx={{ py: 6, display: "grid", placeItems: "center" }}>
                <CircularProgress size={26} sx={{ color: accentBlue }} />
              </Box>
            ) : (
              <Stack spacing={1.2}>
                {topicSummaries.map((topic) => {
                  const isSelected = topic.topic === selectedTopic;

                  return (
                    <Box
                      key={topic.topic}
                      onClick={() => onSelectTopic(topic.topic)}
                      sx={{
                        display: "flex",
                        alignItems: "center",
                        gap: 1.25,
                        px: 1.9,
                        py: 1.55,
                        borderRadius: "12px",
                        border: isSelected ? `1.5px solid ${accentBlue}` : "1px solid #DCE5F3",
                        bgcolor: isSelected ? "#F5F9FF" : "#FFFFFF",
                        cursor: "pointer",
                      }}
                    >
                      <Box
                        sx={{
                          width: 16,
                          height: 16,
                          borderRadius: "50%",
                          border: isSelected ? `5px solid ${accentBlue}` : "1.5px solid #CBD5E1",
                          bgcolor: "#FFFFFF",
                          flexShrink: 0,
                        }}
                      />
                      <Typography
                        sx={{ fontSize: 15, fontWeight: isSelected ? 700 : 500, color: "#1E293B" }}
                      >
                        {topic.label}
                      </Typography>
                    </Box>
                  );
                })}
              </Stack>
            )}

            <Button
              fullWidth
              disabled
              variant="contained"
              startIcon={<DownloadOutlinedIcon />}
              sx={{
                mt: 3,
                py: 1.45,
                borderRadius: "12px",
                textTransform: "none",
                fontWeight: 700,
                bgcolor: accentBlue,
                boxShadow: "none",
              }}
            >
              Exportar metricas
            </Button>
          </SectionCard>
        </Grid>

        <Grid item xs={12} lg={9}>
          <SectionCard sx={{ p: 3 }}>
            <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", mb: 3 }}>
              <Typography sx={{ fontSize: 18, fontWeight: 800, color: textPrimary }}>
                Metricas de Tema: {selectedTopicSummary?.label || "Tema"}
              </Typography>
              <Button
                disabled
                variant="outlined"
                startIcon={<DownloadOutlinedIcon />}
                sx={{
                  borderRadius: "12px",
                  textTransform: "none",
                  fontWeight: 700,
                  color: "#334155",
                  borderColor: "#D5DEEB",
                }}
              >
                Exportar
              </Button>
            </Box>

            <Grid container spacing={2.5} sx={{ mb: 3 }}>
              <Grid item xs={12} md={4}>
                <TopicMetricCard
                  title="Preguntas Realizadas"
                  value={
                    isTopicsLoading || !selectedTopicSummary
                      ? "..."
                      : formatWholeNumber(selectedTopicSummary.questions_count)
                  }
                  helper={
                    isTopicsLoading || !selectedTopicSummary
                      ? "Cargando..."
                      : formatChange(selectedTopicSummary.questions_change_ratio)
                  }
                  topIcon={<HelpOutlineOutlinedIcon sx={{ fontSize: 18 }} />}
                  bottomIcon={<InsightsOutlinedIcon sx={{ fontSize: 15 }} />}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TopicMetricCard
                  title="Ejercicios Generados"
                  value={
                    isTopicsLoading || !selectedTopicSummary
                      ? "..."
                      : formatWholeNumber(selectedTopicSummary.exercises_generated)
                  }
                  helper={
                    isTopicsLoading || !selectedTopicSummary
                      ? "Cargando..."
                      : formatChange(selectedTopicSummary.exercises_change_ratio)
                  }
                  topIcon={<PlaylistAddCheckRoundedIcon sx={{ fontSize: 18 }} />}
                  bottomIcon={<InsightsOutlinedIcon sx={{ fontSize: 15 }} />}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TopicMetricCard
                  title="Nivel de Interaccion"
                  value={
                    isTopicsLoading || !selectedTopicSummary
                      ? "..."
                      : interactionLevelLabel(selectedTopicSummary.interaction_level)
                  }
                  helper={
                    isTopicsLoading || !selectedTopicSummary
                      ? "Cargando..."
                      : `${formatPercentage(selectedTopicSummary.active_students_ratio)} de los estudiantes`
                  }
                  helperColor={textSecondary}
                  topIcon={<Diversity3OutlinedIcon sx={{ fontSize: 18, color: "#22C55E" }} />}
                  bottomIcon={<PersonOutlineRoundedIcon sx={{ fontSize: 15, color: "#64748B" }} />}
                />
              </Grid>
            </Grid>

            <Box
              sx={{
                borderRadius: "18px",
                border: "1px solid #E6EDF6",
                minHeight: 240,
                p: 3,
              }}
            >
              <Typography sx={{ fontSize: 15, fontWeight: 500, color: "#1E293B", mb: 2.5 }}>
                Evolucion de Consultas (Ultimos 7 dias)
              </Typography>

              {isTopicTrendLoading ? (
                <Box sx={{ minHeight: 170, display: "grid", placeItems: "center" }}>
                  <CircularProgress size={28} sx={{ color: accentBlue }} />
                </Box>
              ) : (
                <Box sx={{ height: 190 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={topicTrendData} margin={{ top: 8, right: 4, left: -20, bottom: 0 }}>
                      <CartesianGrid vertical={false} stroke="#EEF2F7" />
                      <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: "#94A3B8", fontSize: 12 }} />
                      <YAxis hide allowDecimals={false} />
                      <Tooltip />
                      <Line
                        type="monotone"
                        dataKey="preguntas"
                        stroke="#3B82F6"
                        strokeWidth={2.5}
                        dot={{ r: 2.5, fill: "#3B82F6" }}
                        activeDot={{ r: 4 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </Box>
              )}
            </Box>
          </SectionCard>
        </Grid>
      </Grid>
    </>
  );
}
