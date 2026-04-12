import React from "react";
import AddIcon from "@mui/icons-material/Add";
import CalculateOutlinedIcon from "@mui/icons-material/CalculateOutlined";
import ChatBubbleOutlineIcon from "@mui/icons-material/ChatBubbleOutline";
import HistoryIcon from "@mui/icons-material/History";
import SettingsOutlinedIcon from "@mui/icons-material/SettingsOutlined";
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
import { BrandIcon } from "../Icons";

interface SidebarProps {
  onOpenHistory?: () => void;
  onOpenAttach?: () => void;
  onNavigateReports?: () => void;
}

export function Sidebar({ onOpenHistory, onOpenAttach, onNavigateReports }: SidebarProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();

  const handleNavigate = (path: string) => {
    navigate(path);
  };

  return (
    <Box sx={{ display: "flex", flexDirection: "column", height: "100%", bgcolor: "#fff" }}>
      <Box sx={{ p: 3, pt: 4, display: "flex", alignItems: "center", gap: 1.5 }}>
        <Box
          sx={{
            width: 40,
            height: 40,
            borderRadius: 2,
            bgcolor: "#EFF6FF",
            display: "grid",
            placeItems: "center",
            color: "#1E3A8A",
          }}
        >
          <BrandIcon style={{ width: 20, height: 20 }} />
        </Box>
        <Box>
          <Typography variant="h6" sx={{ color: "#1E3A8A", fontWeight: 800, fontSize: "1.1rem", lineHeight: 1.2 }}>
            Cubik IA
          </Typography>
          <Typography variant="caption" sx={{ color: "#6B7280", fontWeight: 700, fontSize: "0.75rem" }}>
            Academic Curator
          </Typography>
        </Box>
      </Box>

      <List sx={{ px: 2, flexGrow: 1 }}>
        <ListItem disablePadding sx={{ mb: 0.5 }}>
          <ListItemButton
            selected={location.pathname === "/"}
            onClick={() => handleNavigate("/")}
            sx={{
              borderRadius: "8px",
              bgcolor: location.pathname === "/" ? "#EFF6FF" : "transparent",
              color: location.pathname === "/" ? "#1E3A8A" : "#4B5563",
              py: 1.2,
              px: 2,
              "&.Mui-selected": {
                bgcolor: "#EFF6FF",
                color: "#1E3A8A",
                "&:hover": { bgcolor: "#E0EFFF" },
              },
              "&:hover": { bgcolor: "#F3F4F6" },
            }}
          >
            <ListItemIcon sx={{ minWidth: 36, color: "inherit" }}>
              <ChatBubbleOutlineIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText
              primary="Chat"
              primaryTypographyProps={{ fontSize: "0.875rem", fontWeight: location.pathname === "/" ? 700 : 600 }}
            />
          </ListItemButton>
        </ListItem>

        <ListItem disablePadding sx={{ mb: 0.5 }}>
          <ListItemButton
            onClick={onOpenHistory}
            sx={{ borderRadius: "8px", color: "#4B5563", py: 1.2, px: 2, "&:hover": { bgcolor: "#F3F4F6" } }}
          >
            <ListItemIcon sx={{ minWidth: 36, color: "inherit" }}>
              <HistoryIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText primary="History" primaryTypographyProps={{ fontSize: "0.875rem", fontWeight: 600 }} />
          </ListItemButton>
        </ListItem>

        <ListItem disablePadding sx={{ mb: 0.5 }}>
          <ListItemButton
            onClick={onOpenAttach}
            sx={{ borderRadius: "8px", color: "#4B5563", py: 1.2, px: 2, "&:hover": { bgcolor: "#F3F4F6" } }}
          >
            <ListItemIcon sx={{ minWidth: 36, color: "inherit" }}>
              <CalculateOutlinedIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText primary="Exercises" primaryTypographyProps={{ fontSize: "0.875rem", fontWeight: 600 }} />
          </ListItemButton>
        </ListItem>

        {user?.role === "teacher" ? (
          <ListItem disablePadding sx={{ mb: 0.5 }}>
            <ListItemButton
              selected={location.pathname === "/reports"}
              onClick={() => {
                onNavigateReports?.();
                handleNavigate("/reports");
              }}
              sx={{
                borderRadius: "8px",
                bgcolor: location.pathname === "/reports" ? "#EFF6FF" : "transparent",
                color: location.pathname === "/reports" ? "#1E3A8A" : "#4B5563",
                py: 1.2,
                px: 2,
                "&.Mui-selected": {
                  bgcolor: "#EFF6FF",
                  color: "#1E3A8A",
                  "&:hover": { bgcolor: "#E0EFFF" },
                },
                "&:hover": { bgcolor: "#F3F4F6" },
              }}
            >
              <ListItemIcon sx={{ minWidth: 36, color: "inherit" }}>
                <SettingsOutlinedIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText
                primary="Reportes"
                primaryTypographyProps={{ fontSize: "0.875rem", fontWeight: location.pathname === "/reports" ? 700 : 600 }}
              />
            </ListItemButton>
          </ListItem>
        ) : null}
      </List>

      <Box sx={{ p: 2, pb: 4 }}>
        <Button
          variant="contained"
          fullWidth
          onClick={onOpenAttach}
          startIcon={<AddIcon />}
          sx={{
            bgcolor: "#1E3A8A",
            color: "#fff",
            borderRadius: "10px",
            textTransform: "none",
            fontWeight: 700,
            py: 1.2,
            boxShadow: "0 10px 20px rgba(30, 58, 138, 0.15)",
            "&:hover": { bgcolor: "#1E40AF", boxShadow: "0 10px 20px rgba(30, 58, 138, 0.25)" },
          }}
        >
          New Exercise
        </Button>
      </Box>
    </Box>
  );
}
