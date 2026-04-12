import React, { useState } from "react";
import MenuIcon from "@mui/icons-material/Menu";
import NotificationsNoneOutlinedIcon from "@mui/icons-material/NotificationsNoneOutlined";
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
import { useLocation } from "react-router-dom";

import { logoutRequest } from "../api/client";
import { Sidebar } from "../components";
import { useAuth } from "../context";

interface MainLayoutProps {
  children: React.ReactNode;
  onOpenHistory?: () => void;
  onOpenAttach?: () => void;
}

const collapsedWidth = 72;
const expandedWidth = 280;

function getPageHeading(pathname: string) {
  if (pathname === "/reports") {
    return {
      eyebrow: "Scholar Pro",
      title: "Panel de Reportes",
      subtitle: "Analitica academica y seguimiento de actividad",
    };
  }

  return {
    eyebrow: "Cubik IA",
    title: "Asistente de Aprendizaje",
    subtitle: "Chat educativo con enfoque en resolucion y practica matematica",
  };
}

export function MainLayout({ children, onOpenHistory, onOpenAttach }: MainLayoutProps) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));
  const location = useLocation();
  const { user, logout } = useAuth();
  const currentWidth = isMobile ? expandedWidth : isSidebarCollapsed ? collapsedWidth : expandedWidth;
  const pageHeading = getPageHeading(location.pathname);

  function handleDrawerToggle() {
    if (isMobile) {
      setMobileOpen((current) => !current);
      return;
    }

    setIsSidebarCollapsed((current) => !current);
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
    <Box sx={{ display: "flex", minHeight: "100vh", bgcolor: "background.default" }}>
      <Box component="nav" sx={{ width: { md: currentWidth }, flexShrink: { md: 0 } }}>
        <Drawer
          variant={isMobile ? "temporary" : "permanent"}
          open={isMobile ? mobileOpen : true}
          onClose={() => setMobileOpen(false)}
          ModalProps={{ keepMounted: true }}
          sx={{
            "& .MuiDrawer-paper": {
              boxSizing: "border-box",
              width: currentWidth,
              bgcolor: "background.paper",
              transition: theme.transitions.create("width", {
                duration: theme.transitions.duration.shorter,
              }),
              overflowX: "hidden",
            },
          }}
        >
          <Sidebar
            collapsed={!isMobile && isSidebarCollapsed}
            onOpenHistory={onOpenHistory}
            onOpenAttach={onOpenAttach}
            onToggleCollapsed={!isMobile ? handleDrawerToggle : undefined}
          />
        </Drawer>
      </Box>

      <Box
        sx={{
          flexGrow: 1,
          display: "flex",
          flexDirection: "column",
          width: { md: `calc(100% - ${currentWidth}px)` },
          minWidth: 0,
        }}
      >
        <AppBar position="sticky" color="transparent">
          <Toolbar
            sx={{
              minHeight: "88px !important",
              px: { xs: 2, md: 4 },
              gap: 2,
              bgcolor: "background.paper",
            }}
          >
            <IconButton
              color="primary"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{
                borderRadius: 2,
                border: "1px solid",
                borderColor: "divider",
                bgcolor: "background.default",
              }}
            >
              <MenuIcon />
            </IconButton>

            <Box sx={{ flexGrow: 1, minWidth: 0 }}>
              <Typography
                variant="overline"
                sx={{ display: "block", color: "primary.main", fontWeight: 800, letterSpacing: "0.12em" }}
              >
                {pageHeading.eyebrow}
              </Typography>
              <Typography variant="h5" sx={{ color: "text.primary", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                {pageHeading.title}
              </Typography>
              <Typography variant="body2" sx={{ color: "text.secondary", display: { xs: "none", sm: "block" } }}>
                {pageHeading.subtitle}
              </Typography>
            </Box>

            <IconButton
              sx={{
                borderRadius: 2,
                border: "1px solid",
                borderColor: "divider",
                color: "text.secondary",
                bgcolor: "background.default",
              }}
            >
              <NotificationsNoneOutlinedIcon />
            </IconButton>

            <Avatar
              sx={{
                width: 40,
                height: 40,
                bgcolor: "primary.light",
                color: "primary.main",
                fontSize: "0.875rem",
                fontWeight: 800,
              }}
            >
              {(user?.display_name ?? "US").slice(0, 2).toUpperCase()}
            </Avatar>

            <Box sx={{ display: { xs: "none", md: "block" }, minWidth: 0 }}>
              <Typography variant="subtitle2" sx={{ color: "text.primary", whiteSpace: "nowrap" }}>
                {user?.display_name ?? "Usuario"}
              </Typography>
              <Typography variant="caption" sx={{ color: "text.secondary", textTransform: "capitalize" }}>
                {user?.role === "teacher" ? "Profesor" : "Estudiante"}
              </Typography>
            </Box>

            <Button variant="outlined" color="primary" onClick={() => void handleLogout()}>
              Salir
            </Button>
          </Toolbar>
        </AppBar>

        <Box
          component="main"
          sx={{
            flexGrow: 1,
            minHeight: 0,
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
