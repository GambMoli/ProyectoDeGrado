import React from "react";
import { Box, AppBar, Toolbar, Typography, Avatar, IconButton, Paper, Grid, TextField, InputAdornment, Button, Checkbox, List, ListItem, ListItemButton, ListItemText } from "@mui/material";
import NotificationsNoneOutlinedIcon from "@mui/icons-material/NotificationsNoneOutlined";
import ChatBubbleOutlineIcon from "@mui/icons-material/ChatBubbleOutline";
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
import { AreaChart, Area, XAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from "recharts";

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
    <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh", bgcolor: "#F9FAFB", fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
      {/* Header Básico */}
      <AppBar position="static" elevation={0} sx={{ bgcolor: "#fff", color: "#374151", borderBottom: 1, borderColor: "grey.200" }}>
        <Toolbar sx={{ justifyContent: "space-between", minHeight: "56px !important" }}>
          <Box sx={{ display: "flex", gap: 3, alignItems: "center" }}>
            <Typography variant="body2" sx={{ fontWeight: 800, color: "#1E3A8A" }}>Cubik IA</Typography>
            <Typography variant="body2" sx={{ fontWeight: 600, cursor: "pointer" }}>Página Principal</Typography>
            <Typography variant="body2" sx={{ fontWeight: 600, cursor: "pointer" }}>Mis cursos</Typography>
          </Box>
          <Box sx={{ display: "flex", gap: 2, alignItems: "center" }}>
            <IconButton size="small"><NotificationsNoneOutlinedIcon /></IconButton>
            <IconButton size="small"><ChatBubbleOutlineIcon /></IconButton>
            <Avatar sx={{ width: 32, height: 32, bgcolor: "#EED1B4" }} />
          </Box>
        </Toolbar>
      </AppBar>

      {/* Nav Principal */}
      <Box sx={{ bgcolor: "#1E3A8A", color: "#fff", px: 3 }}>
        <Box sx={{ maxWidth: 1200, mx: "auto", display: "flex", gap: 4, alignItems: "center", py: 1.5 }}>
          <Typography variant="body2" sx={{ cursor: "pointer", opacity: 0.8 }}>Curso</Typography>
          <Typography variant="body2" sx={{ cursor: "pointer", opacity: 0.8 }}>Participantes</Typography>
          <Typography variant="body2" sx={{ cursor: "pointer", opacity: 0.8 }}>Calificaciones</Typography>
          <Typography variant="body2" sx={{ cursor: "pointer", fontWeight: 700, borderBottom: "2px solid #fff", pb: 0.5 }}>REPORTES</Typography>
          <Typography variant="body2" sx={{ cursor: "pointer", opacity: 0.8 }}>Banco de contenido</Typography>
          <Box sx={{ display: "flex", alignItems: "center", gap: 1, cursor: "pointer", opacity: 0.8 }}>
              <ChatBubbleOutlineIcon fontSize="small" />
              <Typography variant="body2">Chatbot</Typography>
          </Box>
        </Box>
      </Box>

      {/* Content */}
      <Box sx={{ flexGrow: 1 }}>
        <Box sx={{ maxWidth: 1200, mx: "auto", px: 3, py: 4 }}>
          <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", mb: 3 }}>
            <Typography variant="h4" sx={{ fontWeight: 800, color: "#111827" }}>Reportes</Typography>
            <Typography variant="body2" sx={{ color: "#6B7280" }}>Página Principal / Mis cursos / Reportes</Typography>
          </Box>

          <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2 }}>
            <PeopleAltOutlinedIcon sx={{ color: "#1E3A8A" }} />
            <Typography variant="h6" sx={{ fontWeight: 700, color: "#1F2937" }}>Reportes por Estudiante</Typography>
          </Box>

          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} md={8}>
              <Paper elevation={0} sx={{ p: 3, borderRadius: 3, border: "1px solid #E5E7EB", height: "100%" }}>
                <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2, alignItems: "center" }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>Seleccionar Estudiante</Typography>
                    <TextField 
                        size="small" placeholder="Buscar..." 
                        InputProps={{ startAdornment: <InputAdornment position="start"><SearchIcon fontSize="small" /></InputAdornment>, sx: { borderRadius: 2 } }}
                    />
                </Box>
                <List disablePadding>
                  <ListItem sx={{ px: 2, py: 1.5, borderBottom: "1px solid #F3F4F6" }}>
                      <Box sx={{ width: "30%", display: "flex", alignItems: "center", gap: 1.5 }}>
                          <Avatar sx={{ width: 28, height: 28, bgcolor: "#DBEAFE", color: "#1D4ED8", fontSize: "0.75rem", fontWeight: 700 }}>AM</Avatar>
                          <Typography variant="body2" sx={{ fontWeight: 600 }}>Ana Martínez</Typography>
                      </Box>
                      <Typography variant="body2" sx={{ width: "40%", color: "#6B7280" }}>ana.m@universidad.edu</Typography>
                      <Box sx={{ width: "20%", textAlign: "right" }}><Checkbox defaultChecked size="small" /></Box>
                  </ListItem>
                  <ListItem sx={{ px: 2, py: 1.5, borderBottom: "1px solid #F3F4F6" }}>
                      <Box sx={{ width: "30%", display: "flex", alignItems: "center", gap: 1.5 }}>
                          <Avatar sx={{ width: 28, height: 28, bgcolor: "#FCE7F3", color: "#BE185D", fontSize: "0.75rem", fontWeight: 700 }}>CR</Avatar>
                          <Typography variant="body2" sx={{ fontWeight: 500 }}>Carlos Ramírez</Typography>
                      </Box>
                      <Typography variant="body2" sx={{ width: "40%", color: "#6B7280" }}>carlos.r@universidad.edu</Typography>
                      <Box sx={{ width: "20%", textAlign: "right" }}><Checkbox size="small" /></Box>
                  </ListItem>
                </List>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper elevation={0} sx={{ p: 3, borderRadius: 3, border: "1px solid #E5E7EB", height: "100%", display: "flex", flexDirection: "column" }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>Filtros de Periodo</Typography>
                <TextField size="small" defaultValue="09/01/2023" fullWidth sx={{ mb: 2 }} InputProps={{ startAdornment: <InputAdornment position="start"><CalendarTodayIcon fontSize="small" /></InputAdornment>, sx: { borderRadius: 2 } }} />
                <TextField size="small" defaultValue="10/31/2023" fullWidth sx={{ mb: 4 }} InputProps={{ startAdornment: <InputAdornment position="start"><CalendarTodayIcon fontSize="small" /></InputAdornment>, sx: { borderRadius: 2 } }} />
                <Button variant="contained" fullWidth startIcon={<ShowChartIcon />} sx={{ mt: "auto", bgcolor: "#1E3A8A", borderRadius: 2, py: 1, textTransform: "none", fontWeight: 600 }}>Generar métricas</Button>
              </Paper>
            </Grid>
          </Grid>

          <Paper elevation={0} sx={{ p: 3, borderRadius: 3, border: "1px solid #E5E7EB", mb: 5 }}>
            <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", mb: 3 }}>
                <Box>
                    <Typography variant="h6" sx={{ fontWeight: 700, color: "#1F2937" }}>Resultados: Ana Martínez</Typography>
                    <Typography variant="body2" sx={{ color: "#6B7280" }}>Período: 01 Sept 2023 - 31 Oct 2023</Typography>
                </Box>
                <Button variant="outlined" startIcon={<DownloadIcon />} sx={{ color: "#4B5563", borderColor: "#D1D5DB", borderRadius: 2, textTransform: "none", fontWeight: 600 }}>Generar reporte</Button>
            </Box>
            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} md={4}>
                    <Box sx={{ p: 3, borderRadius: 3, border: "1px solid #E5E7EB", display: "flex", alignItems: "center", gap: 2 }}>
                        <Avatar sx={{ bgcolor: "#EFF6FF", color: "#1E3A8A", width: 48, height: 48 }}><ShowChartIcon /></Avatar>
                        <Box>
                            <Typography variant="caption" sx={{ color: "#6B7280", fontWeight: 600 }}>Frecuencia de Uso</Typography>
                            <Typography variant="h5" sx={{ fontWeight: 800, color: "#1F2937", display: "flex", alignItems: "baseline", gap: 1 }}>4.2 <Typography variant="caption" sx={{ color: "#6B7280", fontWeight: 500 }}>días/sem</Typography></Typography>
                        </Box>
                    </Box>
                </Grid>
                <Grid item xs={12} md={4}>
                    <Box sx={{ p: 3, borderRadius: 3, border: "1px solid #E5E7EB", display: "flex", alignItems: "center", gap: 2 }}>
                        <Avatar sx={{ bgcolor: "#F3E8FF", color: "#7E22CE", width: 48, height: 48 }}><ChatIcon /></Avatar>
                        <Box>
                            <Typography variant="caption" sx={{ color: "#6B7280", fontWeight: 600 }}>Total de Consultas</Typography>
                            <Typography variant="h5" sx={{ fontWeight: 800, color: "#1F2937" }}>128</Typography>
                        </Box>
                    </Box>
                </Grid>
            </Grid>

            <Box sx={{ border: "1px solid #E5E7EB", borderRadius: 3, p: 3, height: 260 }}>
                <Typography variant="body2" sx={{ fontWeight: 600, color: "#374151", mb: 2 }}>Actividad por Semana</Typography>
                <ResponsiveContainer width="100%" height="80%">
                    <AreaChart data={mockAreaData}>
                        <defs>
                            <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#1E3A8A" stopOpacity={0.1}/>
                                <stop offset="95%" stopColor="#1E3A8A" stopOpacity={0}/>
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                        <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: "#6B7280", fontSize: 12 }} dy={10} />
                        <Tooltip />
                        <Area type="monotone" dataKey="value" stroke="#1E3A8A" strokeWidth={2} fillOpacity={1} fill="url(#colorValue)" />
                    </AreaChart>
                </ResponsiveContainer>
            </Box>
          </Paper>
        </Box>
      </Box>
    </Box>
  );
}
