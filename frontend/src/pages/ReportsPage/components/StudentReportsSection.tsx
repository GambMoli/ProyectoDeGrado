import CalendarTodayOutlinedIcon from "@mui/icons-material/CalendarTodayOutlined";
import ChatBubbleOutlineRoundedIcon from "@mui/icons-material/ChatBubbleOutlineRounded";
import DownloadOutlinedIcon from "@mui/icons-material/DownloadOutlined";
import FilterAltOutlinedIcon from "@mui/icons-material/FilterAltOutlined";
import PersonSearchOutlinedIcon from "@mui/icons-material/PersonSearchOutlined";
import QueryStatsOutlinedIcon from "@mui/icons-material/QueryStatsOutlined";
import SearchIcon from "@mui/icons-material/Search";
import AccessTimeRoundedIcon from "@mui/icons-material/AccessTimeRounded";
import { Alert, Avatar, Box, Button, Checkbox, CircularProgress, Grid, InputAdornment, List, ListItem, Stack, TextField, Typography } from "@mui/material";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { StudentReportListItem, StudentReportSummary } from "../../../types/api";
import { formatDateRange, formatOneDecimal, formatWholeNumber, initialsForName } from "../utils";
import { SectionCard } from "./SectionCard";
import { StudentMetricCard } from "./StudentMetricCard";
import { avatarPalette } from "../../../themes/appTheme";

interface WeeklyChartPoint {
  name: string;
  total: number;
}

interface StudentReportsSectionProps {
  draftEnd: string;
  draftStart: string;
  error: string | null;
  isStudentMetricsLoading: boolean;
  isStudentsLoading: boolean;
  range: {
    start: string;
    end: string;
  };
  search: string;
  selectedStudent: StudentReportListItem | null;
  selectedStudentId: string | null;
  studentSummary: StudentReportSummary | null;
  students: StudentReportListItem[];
  weeklyChartData: WeeklyChartPoint[];
  clearError: () => void;
  onApplyFilters: () => void;
  onChangeDraftEnd: (value: string) => void;
  onChangeDraftStart: (value: string) => void;
  onChangeSearch: (value: string) => void;
  onSelectStudent: (userId: string) => void;
}

export function StudentReportsSection({
  draftEnd,
  draftStart,
  error,
  isStudentMetricsLoading,
  isStudentsLoading,
  range,
  search,
  selectedStudent,
  selectedStudentId,
  studentSummary,
  students,
  weeklyChartData,
  clearError,
  onApplyFilters,
  onChangeDraftEnd,
  onChangeDraftStart,
  onChangeSearch,
  onSelectStudent,
}: StudentReportsSectionProps) {
  return (
    <>
      <Stack direction="row" spacing={1.2} alignItems="center" sx={{ mb: 2.5 }}>
        <PersonSearchOutlinedIcon sx={{ color: "#1547A1", fontSize: 23 }} />
        <Typography sx={{ fontSize: 18, fontWeight: 800, color: "text.primary" }}>
          Reportes por Estudiante
        </Typography>
      </Stack>

      {error ? (
        <Alert severity="error" sx={{ mb: 3 }} onClose={clearError}>
          {error}
        </Alert>
      ) : null}

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} lg={8}>
          <SectionCard sx={{ overflow: "hidden" }}>
            <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", px: 3, py: 2.25, backgroundColor:"background.secondAlt" }}>
              <Typography sx={{ fontSize: 15, fontWeight: 600, color: "text.primary" }}>
                Seleccionar Estudiante
              </Typography>
              <TextField
                value={search}
                onChange={(event) => onChangeSearch(event.target.value)}
                placeholder="Buscar..."
                size="small"
                sx={{ width: { xs: "100%", sm: 262 }, color: "text.secondary" }}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon sx={{ fontSize: 18, color: "text.secondary" }} />
                    </InputAdornment>
                  ),
                  sx: { borderRadius: "12px", bgcolor: "background.default" },
                }}
              />
            </Box>

            <Box
              sx={{
                display: "grid",
                gridTemplateColumns: "1.2fr 0.9fr 120px",
                px: 3,
                py: 1.5,
                borderTop: `1px solid divider`,
                borderBottom: `1px solid divider`,
                bgcolor: "background.secondAlt",
                color: "text.secondary",
              }}
            >
              <Typography sx={{ fontSize: 13, fontWeight: 700 }}>NOMBRE DEL ESTUDIANTE</Typography>
              <Typography sx={{ fontSize: 13, fontWeight: 700 }}>CORREO ELECTRONICO</Typography>
              <Typography sx={{ fontSize: 13, fontWeight: 700, textAlign: "center" }}>
                SELECCIONAR
              </Typography>
            </Box>

            {isStudentsLoading ? (
              <Box sx={{ py: 8, display: "grid", placeItems: "center", backgroundColor:"background.paper" }}>
                <CircularProgress size={28} sx={{ color: "#1547A1" }} />
              </Box>
            ) : students.length === 0 ? (
              <Box sx={{ px: 3, py: 6, backgroundColor:"background.paper" }}>
                <Typography sx={{ fontSize: 14, color: "text.secondary" }}>
                  No hay estudiantes con actividad en el rango seleccionado.
                </Typography>
              </Box>
            ) : (
              <Box sx={{ maxHeight: 600, overflowY: "auto", overflowX: "auto" }}>
                <List disablePadding sx={{ minWidth: 480 }}>
                  {students.map((student, index) => {
                    const palette = avatarPalette[index % avatarPalette.length];
                    const isSelected = student.user_id === selectedStudentId;

                    return (
                      <ListItem
                        key={student.user_id}
                        disableGutters
                        sx={{
                          px: 3,
                          py: 1.75,
                          display: "grid",
                          gridTemplateColumns: "1.2fr 0.9fr 120px",
                          borderBottom: "1px solid #EEF2F7",
                          backgroundColor:"background.paper"
                        }}
                      >
                        <Stack direction="row" spacing={1.75} alignItems="center">
                          <Avatar
                            sx={{
                              width: 32,
                              height: 32,
                              bgcolor: palette.bg,
                              color: palette.color,
                              fontSize: 13,
                              fontWeight: 800,
                            }}
                          >
                            {initialsForName(student.display_name)}
                          </Avatar>
                          <Typography sx={{ fontSize: 14, fontWeight: 500, color: "text.primary" }}>
                            {student.display_name}
                          </Typography>
                        </Stack>
                        <Typography sx={{ fontSize: 14, fontWeight: 500, color: "text.secondary", alignSelf: "center" }}>
                          {student.email || "Sin correo registrado"}
                        </Typography>
                        <Box sx={{ display: "grid", placeItems: "center", backgroundColor:"background.paper" }}>
                          <Checkbox
                            checked={isSelected}
                            onChange={() => onSelectStudent(student.user_id)}
                            sx={{ color: "#CBD5E1", "&.Mui-checked": { color: "#1547A1" } }}
                          />
                        </Box>
                      </ListItem>
                    );
                  })}
                </List>
              </Box>
            )}
          </SectionCard>
        </Grid>

        <Grid item xs={12} lg={4} >
          <SectionCard sx={{ p: 3, height: "100%", backgroundColor:"background.paper" }}>
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 3 }}>
              <FilterAltOutlinedIcon sx={{ color: "#1547A1", fontSize: 20 }} />
              <Typography sx={{ fontSize: 16, fontWeight: 700, color: "text.primary" }}>
                Filtros de Periodo
              </Typography>
            </Stack>

            <Stack spacing={2.25}>
              <Box>
                <Typography sx={{ fontSize: 14, fontWeight: 500, color: "text.secondary", mb: 1 }}>
                  Fecha de Inicio
                </Typography>
                <TextField
                  fullWidth
                  size="small"
                  type="date"
                  value={draftStart}
                  onChange={(event) => onChangeDraftStart(event.target.value)}
                  sx={{color:"text.secondary"}}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <CalendarTodayOutlinedIcon sx={{ fontSize: 18, color: "text.secondary" }} />
                      </InputAdornment>
                    ),
                    sx: { borderRadius: "12px" },
                  }}
                />
              </Box>

              <Box>
                <Typography sx={{ fontSize: 14, fontWeight: 500, color: "text.secondary", mb: 1 }}>
                  Fecha de Fin
                </Typography>
                <TextField
                  fullWidth
                  size="small"
                  type="date"
                  value={draftEnd}
                  onChange={(event) => onChangeDraftEnd(event.target.value)}
                  sx={{color:"text.secondary"}}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <CalendarTodayOutlinedIcon sx={{ fontSize: 18, color: "text.secondary" }} />
                      </InputAdornment>
                    ),
                    sx: { borderRadius: "12px" },
                  }}
                />
              </Box>
            </Stack>

            <Button
              fullWidth
              variant="contained"
              onClick={onApplyFilters}
              sx={{
                mt: 4,
                py: 1.5,
                borderRadius: "12px",
                textTransform: "none",
                fontWeight: 700,
                bgcolor: "#1547A1",
                boxShadow: "none",
                "&:hover": { bgcolor: "#1E40AF", boxShadow: "none" },
              }}
            >
              Generar métricas
            </Button>
          </SectionCard>
        </Grid>
      </Grid>

      <SectionCard sx={{ p: 3, mb: 5, backgroundColor:"background.paper" }}>
        <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", mb: 3 }}>
          <Box>
            <Typography sx={{ fontSize: 18, fontWeight: 800, color: "text.primary" }}>
              Resultados: {selectedStudent?.display_name || "Sin estudiante seleccionado"}
            </Typography>
            <Typography sx={{ fontSize: 14, fontWeight: 500, color: "text.secondary", mt: 0.5 }}>
              Periodo: {formatDateRange(range.start, range.end)}
            </Typography>
          </Box>
          <Button
            disabled
            variant="outlined"
            startIcon={<DownloadOutlinedIcon />}
            sx={{
              borderRadius: "12px",
              textTransform: "none",
              fontWeight: 700,
              color: "text.primary",
              borderColor: "divider",
            }}
          >
            Generar reporte
          </Button>
        </Box>

        {!selectedStudent ? (
          <Box sx={{ py: 6, display: "grid", placeItems: "center" }}>
            <Typography sx={{ fontSize: 14, color: "text.secondary" }}>
              Selecciona un estudiante para ver sus métricas.
            </Typography>
          </Box>
        ) : (
          <>
            <Grid container spacing={3} sx={{ mb: 3.5 }}>
              <Grid item xs={12} md={4}>
                <StudentMetricCard
                  icon={<QueryStatsOutlinedIcon />}
                  iconBg="#E8F0FF"
                  iconColor={"#1547A1"}
                  label="Frecuencia de Uso"
                  value={
                    isStudentMetricsLoading || !studentSummary
                      ? "..."
                      : formatOneDecimal(studentSummary.usage_frequency_days_per_week)
                  }
                  suffix="dias/sem"
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <StudentMetricCard
                  icon={<ChatBubbleOutlineRoundedIcon />}
                  iconBg="#EEF2FF"
                  iconColor="#4F46E5"
                  label="Total de Consultas"
                  value={
                    isStudentMetricsLoading || !studentSummary
                      ? "..."
                      : formatWholeNumber(studentSummary.total_queries)
                  }
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <StudentMetricCard
                  icon={<AccessTimeRoundedIcon />}
                  iconBg="#E8FFF3"
                  iconColor="#059669"
                  label="Tiempo en Sistema"
                  value={
                    isStudentMetricsLoading || !studentSummary
                      ? "..."
                      : formatWholeNumber(Math.round(studentSummary.activity_span_hours_estimate))
                  }
                  suffix="horas"
                />
              </Grid>
            </Grid>

            <Box
              sx={{
                borderRadius: "18px",
                border: "1px solid #E6EDF6",
                minHeight: 280,
                p: 3,
              }}
            >
              <Typography sx={{ fontSize: 15, fontWeight: 500, color: "text.secondary", mb: 2.5 }}>
                Actividad por Semana
              </Typography>

              {isStudentMetricsLoading ? (
                <Box sx={{ minHeight: 210, display: "grid", placeItems: "center" }}>
                  <CircularProgress size={28} sx={{ color: "#1547A1" }} />
                </Box>
              ) : weeklyChartData.length === 0 ? (
                <Box sx={{ minHeight: 210, display: "grid", placeItems: "center" }}>
                  <Typography sx={{ fontSize: 14, color: "text.secondary" }}>
                    No hay actividad registrada en el rango seleccionado.
                  </Typography>
                </Box>
              ) : (
                <Box sx={{ overflowX: "auto" }}>
                <Box sx={{ height: 220, minWidth: 420 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={weeklyChartData} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
                      <defs>
                        <linearGradient id="studentActivityFill" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor={"#1547A1"} stopOpacity={0.16} />
                          <stop offset="95%" stopColor={"#1547A1"} stopOpacity={0.02} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid vertical={false} stroke="#EEF2F7" strokeDasharray="3 3" />
                      <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: "#94A3B8", fontSize: 12 }} />
                      <YAxis hide allowDecimals={false} />
                      <Tooltip />
                      <Area
                        type="monotone"
                        dataKey="total"
                        stroke={"#1547A1"}
                        strokeWidth={2.5}
                        fill="url(#studentActivityFill)"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </Box>
                </Box>
              )}
            </Box>
          </>
        )}
      </SectionCard>
    </>
  );
}