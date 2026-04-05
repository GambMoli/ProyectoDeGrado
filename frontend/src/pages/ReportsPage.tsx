import React from "react";
import { 
  Box, 
  Typography, 
  Paper, 
  Grid, 
  TextField, 
  InputAdornment, 
  Button, 
  Avatar, 
  Checkbox, 
  List, 
  ListItem, 
  ListItemButton, 
  ListItemText,
  Divider,
  LinearProgress,
  Chip
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import CalendarTodayIcon from "@mui/icons-material/CalendarToday";
import PeopleAltOutlinedIcon from "@mui/icons-material/PeopleAltOutlined";
import LibraryBooksOutlinedIcon from "@mui/icons-material/LibraryBooksOutlined";
import ShowChartIcon from "@mui/icons-material/ShowChart";
import DownloadIcon from "@mui/icons-material/Download";
import ChatIcon from "@mui/icons-material/Chat";
import TimerIcon from "@mui/icons-material/Timer";
import QuestionAnswerIcon from "@mui/icons-material/QuestionAnswer";
import AutoFixHighIcon from "@mui/icons-material/AutoFixHigh";
import ThumbUpIcon from "@mui/icons-material/ThumbUp";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from "recharts";

const mockLineData = [
  { name: "Lun", value: 10 }, { name: "Mar", value: 40 }, { name: "Mié", value: 20 },
  { name: "Jue", value: 80 }, { name: "Vie", value: 50 }, { name: "Sáb", value: 90 }, { name: "Dom", value: 60 }
];

const mockAreaData = [
  { name: "Sem 1", value: 20 }, { name: "Sem 2", value: 40 }, { name: "Sem 3", value: 30 },
  { name: "Sem 4", value: 70 }, { name: "Sem 5", value: 50 }, { name: "Sem 6", value: 90 }
];

export function ReportsPage() {
  return (
    <Box sx={{ flexGrow: 1, bgcolor: "#F9FAFB" }}>
      <Box sx={{ maxWidth: 1200, mx: "auto", px: { xs: 2, md: 4 }, py: 4 }}>
        
        {/* Header Section */}
        <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", mb: 4 }}>
          <Box>
            <Typography variant="h4" sx={{ fontWeight: 800, color: "#111827", mb: 0.5 }}>
              Dashboard de Reportes
            </Typography>
            <Typography variant="body2" sx={{ color: "#6B7280", fontWeight: 500 }}>
              Visualiza el progreso académico y la interacción con la IA.
            </Typography>
          </Box>
          <Box sx={{ display: { xs: "none", md: "flex" }, alignItems: "center", gap: 1 }}>
             <Typography variant="caption" sx={{ color: "#9CA3AF", fontWeight: 700 }}>VER EN:</Typography>
             <Button size="small" variant="text" sx={{ fontWeight: 700, color: "#1E3A8A" }}>PDF</Button>
             <Divider orientation="vertical" flexItem sx={{ mx: 0.5 }} />
             <Button size="small" variant="text" sx={{ fontWeight: 700, color: "#6B7280" }}>EXCEL</Button>
          </Box>
        </Box>

        {/* Top Summary Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={3}>
            <Paper elevation={0} sx={{ p: 2.5, borderRadius: 4, border: "1px solid #E5E7EB", bgcolor: "#fff" }}>
              <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
                <Avatar sx={{ bgcolor: "#EFF6FF", color: "#1E3A8A", borderRadius: 2 }}>
                  <PeopleAltOutlinedIcon fontSize="small" />
                </Avatar>
                <TrendingUpIcon sx={{ color: "#10B981", fontSize: 20 }} />
              </Box>
              <Typography variant="h4" sx={{ fontWeight: 800, color: "#111827" }}>42</Typography>
              <Typography variant="body2" sx={{ color: "#6B7280", fontWeight: 600 }}>Estudiantes Activos</Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} md={3}>
            <Paper elevation={0} sx={{ p: 2.5, borderRadius: 4, border: "1px solid #E5E7EB", bgcolor: "#fff" }}>
              <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
                <Avatar sx={{ bgcolor: "#F3E8FF", color: "#7E22CE", borderRadius: 2 }}>
                  <ChatIcon fontSize="small" />
                </Avatar>
                <TrendingUpIcon sx={{ color: "#10B981", fontSize: 20 }} />
              </Box>
              <Typography variant="h4" sx={{ fontWeight: 800, color: "#111827" }}>1.2k</Typography>
              <Typography variant="body2" sx={{ color: "#6B7280", fontWeight: 600 }}>Consultas Totales</Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} md={3}>
            <Paper elevation={0} sx={{ p: 2.5, borderRadius: 4, border: "1px solid #E5E7EB", bgcolor: "#fff" }}>
              <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
                <Avatar sx={{ bgcolor: "#FEF3C7", color: "#D97706", borderRadius: 2 }}>
                  <AutoFixHighIcon fontSize="small" />
                </Avatar>
                <TrendingUpIcon sx={{ color: "#10B981", fontSize: 20 }} />
              </Box>
              <Typography variant="h4" sx={{ fontWeight: 800, color: "#111827" }}>85%</Typography>
              <Typography variant="body2" sx={{ color: "#6B7280", fontWeight: 600 }}>Resolución IA</Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} md={3}>
            <Paper elevation={0} sx={{ p: 2.5, borderRadius: 4, border: "1px solid #E5E7EB", bgcolor: "#fff" }}>
              <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
                <Avatar sx={{ bgcolor: "#DCFCE7", color: "#15803D", borderRadius: 2 }}>
                  <TimerIcon fontSize="small" />
                </Avatar>
                <TrendingUpIcon sx={{ color: "#10B981", fontSize: 20 }} />
              </Box>
              <Typography variant="h4" sx={{ fontWeight: 800, color: "#111827" }}>12m</Typography>
              <Typography variant="body2" sx={{ color: "#6B7280", fontWeight: 600 }}>Promedio Sesión</Typography>
            </Paper>
          </Grid>
        </Grid>

        <Divider sx={{ mb: 4 }} />

        {/* Main Content Sections */}
        <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2 }}>
          <PeopleAltOutlinedIcon sx={{ color: "#1E3A8A" }} />
          <Typography variant="h6" sx={{ fontWeight: 800, color: "#1F2937" }}>Reportes por Estudiante</Typography>
        </Box>

        <Grid container spacing={3} sx={{ mb: 6 }}>
          {/* Seleccionar Estudiante */}
          <Grid item xs={12} md={8}>
            <Paper elevation={0} sx={{ p: 3, borderRadius: 4, border: "1px solid #E5E7EB", height: "100%" }}>
              <Box sx={{ display: "flex", justifyContent: "space-between", mb: 3, alignItems: "center" }}>
                  <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>Directorio de Estudiantes</Typography>
                  <TextField 
                      size="small" 
                      placeholder="Buscar por nombre..." 
                      InputProps={{ 
                        startAdornment: <InputAdornment position="start"><SearchIcon fontSize="small" sx={{ color: "#9CA3AF" }} /></InputAdornment>, 
                        sx: { borderRadius: 3, bgcolor: "#F9FAFB" } 
                      }}
                  />
              </Box>
              <Box sx={{ display: "flex", justifyContent: "space-between", color: "#9CA3AF", px: 2, pb: 1.5, borderBottom: "1px solid #F3F4F6" }}>
                  <Typography variant="caption" sx={{ fontWeight: 800, width: "40%", letterSpacing: "0.05em" }}>ESTUDIANTE</Typography>
                  <Typography variant="caption" sx={{ fontWeight: 800, width: "40%", letterSpacing: "0.05em" }}>CORREO</Typography>
                  <Typography variant="caption" sx={{ fontWeight: 800, width: "20%", textAlign: "right", letterSpacing: "0.05em" }}>ACCIÓN</Typography>
              </Box>
              <List disablePadding>
                {[
                  { name: "Ana Martínez", email: "ana.m@universidad.edu", initial: "AM", color: "#1D4ED8", bg: "#DBEAFE", selected: true },
                  { name: "Carlos Ramírez", email: "carlos.r@universidad.edu", initial: "CR", color: "#BE185D", bg: "#FCE7F3", selected: false },
                  { name: "Laura Gómez", email: "laura.g@universidad.edu", initial: "LG", color: "#15803D", bg: "#DCFCE7", selected: false },
                  { name: "Diego Torres", email: "diego.t@universidad.edu", initial: "DT", color: "#D97706", bg: "#FEF3C7", selected: false },
                ].map((std) => (
                  <ListItem key={std.name} sx={{ px: 2, py: 1.5, borderBottom: "1px solid #F3F4F6", "&:hover": { bgcolor: "#F9FAFB" } }}>
                      <Box sx={{ width: "40%", display: "flex", alignItems: "center", gap: 2 }}>
                          <Avatar sx={{ width: 32, height: 32, bgcolor: std.bg, color: std.color, fontSize: "0.85rem", fontWeight: 800 }}>{std.initial}</Avatar>
                          <Typography variant="body2" sx={{ fontWeight: 700, color: "#374151" }}>{std.name}</Typography>
                      </Box>
                      <Typography variant="body2" sx={{ width: "40%", color: "#6B7280", fontWeight: 500 }}>{std.email}</Typography>
                      <Box sx={{ width: "20%", textAlign: "right" }}><Checkbox checked={std.selected} size="small" sx={{ color: "#D1D5DB", "&.Mui-checked": { color: "#1E3A8A" } }} /></Box>
                  </ListItem>
                ))}
              </List>
            </Paper>
          </Grid>

          {/* Filtros de Periodo */}
          <Grid item xs={12} md={4}>
            <Paper elevation={0} sx={{ p: 4, borderRadius: 4, border: "1px solid #E5E7EB", height: "100%", display: "flex", flexDirection: "column", bgcolor: "#fff" }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 3 }}>Periodo de Análisis</Typography>
              
              <Box sx={{ mb: 3 }}>
                <Typography variant="caption" sx={{ color: "#6B7280", mb: 1, display: "block", fontWeight: 700 }}>FECHA DE INICIO</Typography>
                <TextField 
                  size="small" 
                  defaultValue="09/01/2023" 
                  fullWidth 
                  InputProps={{ 
                    startAdornment: <InputAdornment position="start"><CalendarTodayIcon fontSize="small" sx={{ color: "#1E3A8A" }} /></InputAdornment>, 
                    sx: { borderRadius: 3, bgcolor: "#F9FAFB" } 
                  }} 
                />
              </Box>

              <Box sx={{ mb: 4 }}>
                <Typography variant="caption" sx={{ color: "#6B7280", mb: 1, display: "block", fontWeight: 700 }}>FECHA DE FIN</Typography>
                <TextField 
                  size="small" 
                  defaultValue="10/31/2023" 
                  fullWidth 
                  InputProps={{ 
                    startAdornment: <InputAdornment position="start"><CalendarTodayIcon fontSize="small" sx={{ color: "#1E3A8A" }} /></InputAdornment>, 
                    sx: { borderRadius: 3, bgcolor: "#F9FAFB" } 
                  }} 
                />
              </Box>

              <Button 
                variant="contained" 
                fullWidth 
                startIcon={<ShowChartIcon />} 
                sx={{ 
                  mt: "auto", 
                  bgcolor: "#1E3A8A", 
                  borderRadius: 3, 
                  py: 1.5, 
                  textTransform: "none", 
                  fontWeight: 700,
                  boxShadow: "0 10px 20px rgba(30, 58, 138, 0.15)",
                  "&:hover": { bgcolor: "#1E40AF" }
                }}
              >
                Actualizar Métricas
              </Button>
            </Paper>
          </Grid>
        </Grid>

        {/* Multi-Section Dashboard Card */}
        <Paper elevation={0} sx={{ p: 4, borderRadius: 4, border: "1px solid #E5E7EB", mb: 6, bgcolor: "#fff" }}>
          <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", mb: 4 }}>
              <Box>
                  <Typography variant="h6" sx={{ fontWeight: 800, color: "#111827", display: "flex", alignItems: "center", gap: 1 }}>
                    Métricas Detalladas: Ana Martínez
                    <Chip label="Top Estudiante" size="small" sx={{ bgcolor: "#DCFCE7", color: "#15803D", fontWeight: 800, fontSize: "0.65rem" }} />
                  </Typography>
                  <Typography variant="body2" sx={{ color: "#6B7280", fontWeight: 500 }}>Período: 01 Sept 2023 - 31 Oct 2023</Typography>
              </Box>
              <Button 
                variant="outlined" 
                startIcon={<DownloadIcon />} 
                sx={{ 
                  color: "#4B5563", 
                  borderColor: "#D1D5DB", 
                  borderRadius: 3, 
                  textTransform: "none", 
                  fontWeight: 700,
                  px: 2,
                  "&:hover": { bgcolor: "#F9FAFB", borderColor: "#1E3A8A", color: "#1E3A8A" }
                }}
              >
                Exportar Reporte
              </Button>
          </Box>

          <Grid container spacing={3} sx={{ mb: 5 }}>
              <Grid item xs={12} md={4}>
                  <Box sx={{ p: 3, borderRadius: 4, border: "1px solid #F3F4F6", bgcolor: "#F9FAFB", display: "flex", alignItems: "center", gap: 2.5 }}>
                      <Avatar sx={{ bgcolor: "#fff", color: "#1E3A8A", width: 52, height: 52, border: "1px solid #E5E7EB" }}><ShowChartIcon /></Avatar>
                      <Box>
                          <Typography variant="caption" sx={{ color: "#6B7280", fontWeight: 700, letterSpacing: "0.02em" }}>FRECUENCIA DE USO</Typography>
                          <Typography variant="h5" sx={{ fontWeight: 900, color: "#111827", display: "flex", alignItems: "baseline", gap: 1 }}>
                            4.2 <Typography variant="caption" sx={{ color: "#6B7280", fontWeight: 600 }}>días/sem</Typography>
                          </Typography>
                      </Box>
                  </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                  <Box sx={{ p: 3, borderRadius: 4, border: "1px solid #F3F4F6", bgcolor: "#F9FAFB", display: "flex", alignItems: "center", gap: 2.5 }}>
                      <Avatar sx={{ bgcolor: "#fff", color: "#7E22CE", width: 52, height: 52, border: "1px solid #E5E7EB" }}><ChatIcon /></Avatar>
                      <Box>
                          <Typography variant="caption" sx={{ color: "#6B7280", fontWeight: 700, letterSpacing: "0.02em" }}>TOTAL CONSULTAS</Typography>
                          <Typography variant="h5" sx={{ fontWeight: 900, color: "#111827" }}>128</Typography>
                      </Box>
                  </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                  <Box sx={{ p: 3, borderRadius: 4, border: "1px solid #F3F4F6", bgcolor: "#F9FAFB", display: "flex", alignItems: "center", gap: 2.5 }}>
                      <Avatar sx={{ bgcolor: "#fff", color: "#15803D", width: 52, height: 52, border: "1px solid #E5E7EB" }}><TimerIcon /></Avatar>
                      <Box>
                          <Typography variant="caption" sx={{ color: "#6B7280", fontWeight: 700, letterSpacing: "0.02em" }}>TIEMPO EN SISTEMA</Typography>
                          <Typography variant="h5" sx={{ fontWeight: 900, color: "#111827", display: "flex", alignItems: "baseline", gap: 1 }}>
                            34 <Typography variant="caption" sx={{ color: "#6B7280", fontWeight: 600 }}>horas</Typography>
                          </Typography>
                      </Box>
                  </Box>
              </Grid>
          </Grid>

          <Typography variant="subtitle2" sx={{ fontWeight: 800, color: "#374151", mb: 3, px: 1 }}>Evolución de Interacción Semanal</Typography>
          <Box sx={{ border: "1px solid #F3F4F6", borderRadius: 4, p: 3, height: 320, bgcolor: "#fff" }}>
              <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={mockAreaData}>
                      <defs>
                          <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#1E3A8A" stopOpacity={0.15}/>
                              <stop offset="95%" stopColor="#1E3A8A" stopOpacity={0}/>
                          </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F1F5F9" />
                      <XAxis 
                        dataKey="name" 
                        axisLine={false} 
                        tickLine={false} 
                        tick={{ fill: "#94A3B8", fontSize: 12, fontWeight: 600 }} 
                        dy={15} 
                      />
                      <YAxis 
                        axisLine={false} 
                        tickLine={false} 
                        tick={{ fill: "#94A3B8", fontSize: 12, fontWeight: 600 }} 
                      />
                      <Tooltip 
                        contentStyle={{ borderRadius: "12px", border: "none", boxShadow: "0 10px 15px -3px rgba(0,0,0,0.1)" }}
                      />
                      <Area 
                        type="monotone" 
                        dataKey="value" 
                        stroke="#1E3A8A" 
                        strokeWidth={3} 
                        fillOpacity={1} 
                        fill="url(#colorValue)" 
                      />
                  </AreaChart>
              </ResponsiveContainer>
          </Box>
        </Paper>

        {/* Reportes por Tema Section */}
        <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2 }}>
            <LibraryBooksOutlinedIcon sx={{ color: "#1E3A8A" }} />
            <Typography variant="h6" sx={{ fontWeight: 800, color: "#1F2937" }}>Rendimiento por Tema</Typography>
        </Box>

        <Grid container spacing={3}>
            <Grid item xs={12} md={3}>
                <Paper elevation={0} sx={{ p: 3, borderRadius: 4, border: "1px solid #E5E7EB", height: "100%", bgcolor: "#fff" }}>
                    <Typography variant="caption" sx={{ fontWeight: 800, color: "#9CA3AF", mb: 3, display: "block", letterSpacing: "0.05em" }}>
                        TEMAS DEL CURSO
                    </Typography>
                    <List disablePadding>
                        {[
                          { label: "Límites", active: false, progress: 40 },
                          { label: "Derivadas", active: true, progress: 85 },
                          { label: "Integrales", active: false, progress: 20 },
                          { label: "Ecuaciones Diferenciales", active: false, progress: 5 }
                        ].map((t) => (
                          <ListItem key={t.label} disablePadding sx={{ mb: 1.5 }}>
                              <ListItemButton 
                                sx={{ 
                                  borderRadius: 3, 
                                  py: 1.5, 
                                  flexDirection: "column", 
                                  alignItems: "flex-start",
                                  bgcolor: t.active ? "#EFF6FF" : "transparent",
                                  border: t.active ? "1px solid #1E3A8A" : "1px solid transparent",
                                  "&:hover": { bgcolor: t.active ? "#EFF6FF" : "#F9FAFB" }
                                }}
                              >
                                <Box sx={{ display: "flex", alignItems: "center", width: "100%", mb: 1 }}>
                                  <Checkbox checked={t.active} size="small" sx={{ p: 0, mr: 1, color: t.active ? "#1E3A8A" : "#D1D5DB" }} />
                                  <ListItemText 
                                    primary={t.label} 
                                    primaryTypographyProps={{ fontSize: "0.875rem", fontWeight: t.active ? 800 : 600, color: t.active ? "#1E3A8A" : "#4B5563" }} 
                                  />
                                </Box>
                                <Box sx={{ width: "100%", px: 0.5 }}>
                                   <LinearProgress 
                                      variant="determinate" 
                                      value={t.progress} 
                                      sx={{ 
                                        height: 6, 
                                        borderRadius: 3, 
                                        bgcolor: t.active ? "#DBEAFE" : "#F1F5F9",
                                        "& .MuiLinearProgress-bar": { bgcolor: t.active ? "#1E3A8A" : "#CBD5E1" }
                                      }} 
                                   />
                                </Box>
                              </ListItemButton>
                          </ListItem>
                        ))}
                    </List>
                </Paper>
            </Grid>

            <Grid item xs={12} md={9}>
                <Paper elevation={0} sx={{ p: 4, borderRadius: 4, border: "1px solid #E5E7EB", height: "100%", bgcolor: "#fff" }}>
                    <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", mb: 4 }}>
                        <Typography variant="h6" sx={{ fontWeight: 800, color: "#111827" }}>
                            Estadísticas: Derivadas
                        </Typography>
                        <Button 
                            variant="outlined" 
                            startIcon={<DownloadIcon />}
                            sx={{ color: "#4B5563", borderColor: "#D1D5DB", borderRadius: 3, textTransform: "none", fontWeight: 700 }}
                        >
                            Exportar Datos
                        </Button>
                    </Box>

                    <Grid container spacing={2} sx={{ mb: 4 }}>
                        <Grid item xs={12} md={4}>
                            <Box sx={{ p: 2.5, borderRadius: 4, border: "1px solid #F3F4F6", bgcolor: "#F9FAFB" }}>
                                <Box sx={{ display: "flex", justifyContent: "space-between", mb: 1.5 }}>
                                    <Typography variant="caption" sx={{ color: "#6B7280", fontWeight: 800 }}>PREGUNTAS REALIZADAS</Typography>
                                    <QuestionAnswerIcon fontSize="small" sx={{ color: "#3B82F6" }} />
                                </Box>
                                <Typography variant="h4" sx={{ fontWeight: 900, color: "#111827", mb: 1 }}>450</Typography>
                                <Typography variant="caption" sx={{ color: "#10B981", display: "flex", alignItems: "center", gap: 0.5, fontWeight: 800 }}>
                                    <ShowChartIcon fontSize="small" /> +12% VS ANTERIOR
                                </Typography>
                            </Box>
                        </Grid>
                        <Grid item xs={12} md={4}>
                            <Box sx={{ p: 2.5, borderRadius: 4, border: "1px solid #F3F4F6", bgcolor: "#F9FAFB" }}>
                                <Box sx={{ display: "flex", justifyContent: "space-between", mb: 1.5 }}>
                                    <Typography variant="caption" sx={{ color: "#6B7280", fontWeight: 800 }}>EJERCICIOS GENERADOS</Typography>
                                    <AutoFixHighIcon fontSize="small" sx={{ color: "#8B5CF6" }} />
                                </Box>
                                <Typography variant="h4" sx={{ fontWeight: 900, color: "#111827", mb: 1 }}>1,240</Typography>
                                <Typography variant="caption" sx={{ color: "#10B981", display: "flex", alignItems: "center", gap: 0.5, fontWeight: 800 }}>
                                    <ShowChartIcon fontSize="small" /> +5% VS ANTERIOR
                                </Typography>
                            </Box>
                        </Grid>
                        <Grid item xs={12} md={4}>
                            <Box sx={{ p: 2.5, borderRadius: 4, border: "1px solid #F3F4F6", bgcolor: "#F9FAFB" }}>
                                <Box sx={{ display: "flex", justifyContent: "space-between", mb: 1.5 }}>
                                    <Typography variant="caption" sx={{ color: "#6B7280", fontWeight: 800 }}>NIVEL DE INTERACCIÓN</Typography>
                                    <ThumbUpIcon fontSize="small" sx={{ color: "#10B981" }} />
                                </Box>
                                <Typography variant="h4" sx={{ fontWeight: 900, color: "#111827", mb: 1 }}>ALTO</Typography>
                                <Typography variant="caption" sx={{ color: "#6B7280", display: "flex", alignItems: "center", gap: 0.5, fontWeight: 600 }}>
                                    <PeopleAltOutlinedIcon fontSize="small" /> 85% DE LOS ESTUDIANTES
                                </Typography>
                            </Box>
                        </Grid>
                    </Grid>

                    <Typography variant="subtitle2" sx={{ fontWeight: 800, color: "#374151", mb: 2, px: 1 }}>Evolución de Consultas (Últimos 7 días)</Typography>
                    <Box sx={{ border: "1px solid #F3F4F6", borderRadius: 4, p: 3, height: 180, bgcolor: "#fff" }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={mockLineData}>
                                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: "#94A3B8", fontSize: 10, fontWeight: 700 }} />
                                <Tooltip contentStyle={{ borderRadius: "10px", border: "none" }} />
                                <Line type="monotone" dataKey="value" stroke="#3B82F6" strokeWidth={3} dot={{ r: 4, fill: "#3B82F6", strokeWidth: 0 }} activeDot={{ r: 6 }} />
                            </LineChart>
                        </ResponsiveContainer>
                    </Box>
                </Paper>
            </Grid>
        </Grid>
      </Box>
    </Box>
  );
}
