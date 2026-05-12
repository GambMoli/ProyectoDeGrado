import React from "react";
import AddIcon from "@mui/icons-material/Add";
import AssessmentIcon from "@mui/icons-material/Assessment";
import ChatBubbleOutlineIcon from "@mui/icons-material/ChatBubbleOutline";
import DarkModeOutlinedIcon from "@mui/icons-material/DarkModeOutlined";
import HistoryIcon from "@mui/icons-material/History";
import LightModeOutlinedIcon from "@mui/icons-material/LightModeOutlined";
import {
  Box,
  Button,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
} from "@mui/material";
import { useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../../context";
import { useThemeMode } from "../../themes/themeContext";
import { BrandIcon } from "../Icons";

interface SidebarProps {
  onOpenHistory?: () => void;
  onOpenAttach?: () => void;
  onNavigateReports?: () => void;
  onNewChat?: () => void;
}

export function Sidebar({ onOpenHistory, onOpenAttach, onNavigateReports, onNewChat }: SidebarProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();
  const { mode, toggleMode } = useThemeMode();

  const handleNavigate = (path: string) => {
    navigate(path);
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <Box sx={{ display: "flex", flexDirection: "column", height: "100%", bgcolor: "background.paper" }}>
      <Box sx={{ p: 3, pt: 4, display: "flex", alignItems: "center", gap: 1.5 }}>
        <Box
          sx={{
            width: 40,
            height: 40,
            borderRadius: 2,
            bgcolor: "primary.light",
            display: "grid",
            placeItems: "center",
            color: "primary.main",
          }}
        >
          <BrandIcon style={{ width: 20, height: 20 }} />
        </Box>
        <Box>
          <Typography
            variant="h6"
            sx={{
              color: "primary.main",
              fontWeight: 800,
              fontSize: "1.1rem",
              lineHeight: 1.2,
              fontFamily: "Manrope, Inter, sans-serif",
            }}
          >
            Cubik IA
          </Typography>
          <Typography
            variant="caption"
            sx={{
              color: "text.secondary",
              fontWeight: 700,
              fontSize: "0.75rem",
              fontFamily: "Inter, Segoe UI, system-ui, sans-serif",
            }}
          >
            Academic Curator
          </Typography>
        </Box>
      </Box>

      <List sx={{ px: 2, flexGrow: 1 }}>
        {/* Reports (teacher only) */}
        {user?.role === "teacher" ? (
          <ListItem disablePadding sx={{ mb: 0.5 }}>
            <ListItemButton
              selected={isActive("/reports")}
              onClick={() => {
                onNavigateReports?.();
                handleNavigate("/reports");
              }}
              sx={{
                borderRadius: "8px",
                bgcolor: isActive("/reports") ? "primary.light" : "transparent",
                color: isActive("/reports") ? "primary.main" : "text.secondary",
                py: 1.2,
                px: 2,
                "&.Mui-selected": {
                  bgcolor: "primary.light",
                  color: "primary.main",
                  "&:hover": { bgcolor: "primary.light", filter: "brightness(0.95)" },
                },
                "&:hover": { bgcolor: "action.hover" },
              }}
            >
              <ListItemIcon sx={{ minWidth: 36, color: "inherit" }}>
                <AssessmentIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText
                primary="Reportes"
                primaryTypographyProps={{
                  fontSize: "0.875rem",
                  fontWeight: isActive("/reports") ? 700 : 600,
                  fontFamily: "Inter, Segoe UI, system-ui, sans-serif",
                }}
              />
            </ListItemButton>
          </ListItem>
        ) : null}

        {/* Chat */}
        <ListItem disablePadding sx={{ mb: 0.5 }}>
          <ListItemButton
            selected={isActive("/")}
            onClick={() => handleNavigate("/")}
            sx={{
              borderRadius: "8px",
              bgcolor: isActive("/") ? "primary.light" : "transparent",
              color: isActive("/") ? "primary.main" : "text.secondary",
              py: 1.2,
              px: 2,
              "&.Mui-selected": {
                bgcolor: "primary.light",
                color: "primary.main",
                "&:hover": { bgcolor: "primary.light", filter: "brightness(0.95)" },
              },
              "&:hover": { bgcolor: "action.hover" },
            }}
          >
            <ListItemIcon sx={{ minWidth: 36, color: "inherit" }}>
              <ChatBubbleOutlineIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText
              primary="Chat"
              primaryTypographyProps={{
                fontSize: "0.875rem",
                fontWeight: isActive("/") ? 700 : 600,
                fontFamily: "Inter, Segoe UI, system-ui, sans-serif",
              }}
            />
          </ListItemButton>
        </ListItem>

        {/* History */}
        <ListItem disablePadding sx={{ mb: 0.5 }}>
          <ListItemButton
            onClick={onOpenHistory}
            sx={{
              borderRadius: "8px",
              color: "text.secondary",
              py: 1.2,
              px: 2,
              "&:hover": { bgcolor: "action.hover" },
            }}
          >
            <ListItemIcon sx={{ minWidth: 36, color: "inherit" }}>
              <HistoryIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText
              primary="Historial"
              primaryTypographyProps={{
                fontSize: "0.875rem",
                fontWeight: 600,
                fontFamily: "Inter, Segoe UI, system-ui, sans-serif",
              }}
            />
          </ListItemButton>
        </ListItem>

        {/* Theme toggle */}
        <ListItem disablePadding sx={{ mb: 0.5 }}>
          <ListItemButton
            onClick={toggleMode}
            sx={{
              borderRadius: "8px",
              color: "text.secondary",
              py: 1.2,
              px: 2,
              "&:hover": { bgcolor: "action.hover" },
            }}
          >
            <ListItemIcon sx={{ minWidth: 36, color: "inherit" }}>
              {mode === "light" ? (
                <DarkModeOutlinedIcon fontSize="small" />
              ) : (
                <LightModeOutlinedIcon fontSize="small" />
              )}
            </ListItemIcon>
            <ListItemText
              primary={mode === "light" ? "Modo oscuro" : "Modo claro"}
              primaryTypographyProps={{
                fontSize: "0.875rem",
                fontWeight: 600,
                fontFamily: "Inter, Segoe UI, system-ui, sans-serif",
              }}
            />
          </ListItemButton>
        </ListItem>
      </List>

      <Box sx={{ p: 2, pb: 4 }}>
        <Button
          variant="contained"
          fullWidth
          onClick={() => {
            onNewChat?.();
            navigate("/", { state: { openFormulaPanel: true, newConversation: true } });
          }}
          startIcon={<AddIcon />}
          sx={{
            bgcolor: "primary.main",
            color: "#fff",
            borderRadius: "10px",
            textTransform: "none",
            fontWeight: 700,
            fontFamily: "Inter, Segoe UI, system-ui, sans-serif",
            py: 1.2,
            boxShadow: "0 10px 20px rgba(21, 71, 161, 0.15)",
            "&:hover": {
              bgcolor: "primary.dark",
              boxShadow: "0 10px 20px rgba(21, 71, 161, 0.25)",
            },
          }}
        >
          Nuevo ejercicio
        </Button>
      </Box>
    </Box>
  );
}
