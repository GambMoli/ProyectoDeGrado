import React, { useState } from "react";
import MenuIcon from "@mui/icons-material/Menu";
import NotificationsNoneOutlinedIcon from "@mui/icons-material/NotificationsNoneOutlined";
import ChatBubbleOutlineIcon from "@mui/icons-material/ChatBubbleOutline";
import {
  AppBar,
  Avatar,
  Box,
  Button,
  Drawer,
  IconButton,
  Toolbar,
  Typography,
  useMediaQuery,
  useTheme,
} from "@mui/material";

import { logoutRequest } from "../api/client";
import { Sidebar } from "../components";
import { useAuth } from "../context";

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
  const { user, logout } = useAuth();

  function handleDrawerToggle() {
    setMobileOpen((current) => !current);
  }

  async function handleLogout() {
    try {
      await logoutRequest();
    } catch {
      // Ignore transport errors here; local session cleanup still matters.
    } finally {
      logout();
    }
  }

  return (
    <Box sx={{ display: "flex", minHeight: "100vh", bgcolor: "#F9FAFB" }}>
      <Box component="nav" sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}>
        <Drawer
          variant={isMobile ? "temporary" : "permanent"}
          open={isMobile ? mobileOpen : true}
          onClose={handleDrawerToggle}
          ModalProps={{ keepMounted: true }}
          sx={{
            "& .MuiDrawer-paper": {
              boxSizing: "border-box",
              width: drawerWidth,
              borderRight: "1px solid #E5E7EB",
              bgcolor: "#fff",
            },
          }}
        >
          <Sidebar onOpenHistory={onOpenHistory} onOpenAttach={onOpenAttach} />
        </Drawer>
      </Box>

      <Box
        sx={{
          flexGrow: 1,
          display: "flex",
          flexDirection: "column",
          width: { md: `calc(100% - ${drawerWidth}px)` },
        }}
      >
        <AppBar
          position="sticky"
          elevation={0}
          sx={{ bgcolor: "#fff", color: "#374151", borderBottom: "1px solid #E5E7EB" }}
        >
          <Toolbar sx={{ justifyContent: "space-between", minHeight: "64px !important" }}>
            <Box sx={{ display: "flex", gap: 3, alignItems: "center" }}>
              {isMobile ? (
                <IconButton color="inherit" edge="start" onClick={handleDrawerToggle} sx={{ mr: 1 }}>
                  <MenuIcon />
                </IconButton>
              ) : null}

              {!isMobile ? (
                <Typography variant="h6" sx={{ fontWeight: 800, color: "#1E3A8A" }}>
                  Cubik IA
                </Typography>
              ) : null}

              <Box sx={{ display: { xs: "none", sm: "flex" }, gap: 3 }}>
                <Typography
                  variant="body2"
                  sx={{ fontWeight: 600, cursor: "pointer", "&:hover": { color: "#1E3A8A" } }}
                >
                  Pagina Principal
                </Typography>
                <Typography
                  variant="body2"
                  sx={{ fontWeight: 600, cursor: "pointer", "&:hover": { color: "#1E3A8A" } }}
                >
                  Mis cursos
                </Typography>
              </Box>
            </Box>

            <Box sx={{ display: "flex", gap: 2, alignItems: "center" }}>
              <IconButton size="small">
                <NotificationsNoneOutlinedIcon />
              </IconButton>
              <IconButton size="small">
                <ChatBubbleOutlineIcon />
              </IconButton>
              <Button
                onClick={() => void handleLogout()}
                size="small"
                sx={{ textTransform: "none", color: "#4B5563", fontWeight: 700 }}
              >
                Salir
              </Button>
              <Avatar
                sx={{
                  width: 32,
                  height: 32,
                  bgcolor: "#EED1B4",
                  fontSize: "0.875rem",
                  fontWeight: 700,
                  color: "#9A6A38",
                }}
              >
                {(user?.display_name ?? "US").slice(0, 2).toUpperCase()}
              </Avatar>
            </Box>
          </Toolbar>

          <Box sx={{ bgcolor: "#1E3A8A", color: "#fff", px: { xs: 2, md: 4 } }}>
            <Box
              sx={{
                display: "flex",
                gap: { xs: 2, md: 4 },
                alignItems: "center",
                py: 1.5,
                overflowX: "auto",
                whiteSpace: "nowrap",
              }}
            >
              <Typography variant="body2" sx={{ cursor: "pointer", opacity: 0.8, "&:hover": { opacity: 1 } }}>
                Curso
              </Typography>
              <Typography variant="body2" sx={{ cursor: "pointer", opacity: 0.8, "&:hover": { opacity: 1 } }}>
                Participantes
              </Typography>
              <Typography variant="body2" sx={{ cursor: "pointer", opacity: 0.8, "&:hover": { opacity: 1 } }}>
                Calificaciones
              </Typography>
              {user?.role === "teacher" ? (
                <Typography
                  variant="body2"
                  sx={{ cursor: "pointer", fontWeight: 700, borderBottom: "2px solid #fff", pb: 0.5 }}
                >
                  REPORTES
                </Typography>
              ) : null}
              <Typography variant="body2" sx={{ cursor: "pointer", opacity: 0.8, "&:hover": { opacity: 1 } }}>
                Banco de contenido
              </Typography>
              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  gap: 1,
                  cursor: "pointer",
                  opacity: 0.8,
                  "&:hover": { opacity: 1 },
                }}
              >
                <ChatBubbleOutlineIcon fontSize="small" />
                <Typography variant="body2">Chatbot</Typography>
              </Box>
            </Box>
          </Box>
        </AppBar>

        <Box
          component="main"
          sx={{
            flexGrow: 1,
            height: "100%",
            overflow: "hidden",
            display: "flex",
            flexDirection: "column",
          }}
        >
          {children}
        </Box>
      </Box>
    </Box>
  );
}
