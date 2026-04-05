import React, { useState } from "react";
import { Box, AppBar, Toolbar, Typography, Avatar, IconButton, Drawer, useMediaQuery, useTheme } from "@mui/material";
import NotificationsNoneOutlinedIcon from "@mui/icons-material/NotificationsNoneOutlined";
import ChatBubbleOutlineIcon from "@mui/icons-material/ChatBubbleOutline";
import MenuIcon from "@mui/icons-material/Menu";
import { Sidebar } from "../components/Sidebar";

interface MainLayoutProps {
  children: React.ReactNode;
  onOpenHistory?: () => void;
  onOpenAttach?: () => void;
}

export function MainLayout({ children, onOpenHistory, onOpenAttach }: MainLayoutProps) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));
  const drawerWidth = 260;

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  return (
    <Box sx={{ display: "flex", minHeight: "100vh", bgcolor: "#F9FAFB", fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
      {/* Sidebar - Desktop & Mobile */}
      <Box component="nav" sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}>
        <Drawer
          variant={isMobile ? "temporary" : "permanent"}
          open={isMobile ? mobileOpen : true}
          onClose={handleDrawerToggle}
          ModalProps={{ keepMounted: true }}
          sx={{
            "& .MuiDrawer-paper": { boxSizing: "border-box", width: drawerWidth, borderRight: "1px solid #E5E7EB", bgcolor: "#fff" },
          }}
        >
          <Sidebar onOpenHistory={onOpenHistory!} onOpenAttach={onOpenAttach!} />
        </Drawer>
      </Box>

      {/* Main Content Area */}
      <Box sx={{ flexGrow: 1, display: "flex", flexDirection: "column", width: { md: `calc(100% - ${drawerWidth}px)` } }}>
        {/* Topbar / Header Básico */}
        <AppBar position="sticky" elevation={0} sx={{ bgcolor: "#fff", color: "#374151", borderBottom: "1px solid #E5E7EB" }}>
          <Toolbar sx={{ justifyContent: "space-between", minHeight: "64px !important" }}>
            <Box sx={{ display: "flex", gap: 3, alignItems: "center" }}>
              {isMobile && (
                <IconButton color="inherit" edge="start" onClick={handleDrawerToggle} sx={{ mr: 1 }}>
                  <MenuIcon />
                </IconButton>
              )}
              {!isMobile && <Typography variant="h6" sx={{ fontWeight: 800, color: "#1E3A8A" }}>Cubik IA</Typography>}
              <Box sx={{ display: { xs: "none", sm: "flex" }, gap: 3 }}>
                <Typography variant="body2" sx={{ fontWeight: 600, cursor: "pointer", "&:hover": { color: "#1E3A8A" } }}>Página Principal</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600, cursor: "pointer", "&:hover": { color: "#1E3A8A" } }}>Mis cursos</Typography>
              </Box>
            </Box>
            <Box sx={{ display: "flex", gap: 2, alignItems: "center" }}>
              <IconButton size="small"><NotificationsNoneOutlinedIcon /></IconButton>
              <IconButton size="small"><ChatBubbleOutlineIcon /></IconButton>
              <Avatar sx={{ width: 32, height: 32, bgcolor: "#EED1B4", fontSize: "0.875rem", fontWeight: 700, color: "#9A6A38" }}>US</Avatar>
            </Box>
          </Toolbar>

          {/* Nav Principal Azul (Opcional, lo podemos mostrar global o solo en reportes) */}
          <Box sx={{ bgcolor: "#1E3A8A", color: "#fff", px: { xs: 2, md: 4 } }}>
            <Box sx={{ display: "flex", gap: { xs: 2, md: 4 }, alignItems: "center", py: 1.5, overflowX: "auto", whiteSpace: "nowrap" }}>
              <Typography variant="body2" sx={{ cursor: "pointer", opacity: 0.8, "&:hover": { opacity: 1 } }}>Curso</Typography>
              <Typography variant="body2" sx={{ cursor: "pointer", opacity: 0.8, "&:hover": { opacity: 1 } }}>Participantes</Typography>
              <Typography variant="body2" sx={{ cursor: "pointer", opacity: 0.8, "&:hover": { opacity: 1 } }}>Calificaciones</Typography>
              <Typography variant="body2" sx={{ cursor: "pointer", fontWeight: 700, borderBottom: "2px solid #fff", pb: 0.5 }}>REPORTES</Typography>
              <Typography variant="body2" sx={{ cursor: "pointer", opacity: 0.8, "&:hover": { opacity: 1 } }}>Banco de contenido</Typography>
              <Box sx={{ display: "flex", alignItems: "center", gap: 1, cursor: "pointer", opacity: 0.8, "&:hover": { opacity: 1 } }}>
                  <ChatBubbleOutlineIcon fontSize="small" />
                  <Typography variant="body2">Chatbot</Typography>
              </Box>
            </Box>
          </Box>
        </AppBar>

        {/* Page Content */}
        <Box component="main" sx={{ flexGrow: 1, height: "100%", overflow: "hidden", display: "flex", flexDirection: "column" }}>
          {children}
        </Box>
      </Box>
    </Box>
  );
}
