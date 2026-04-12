import React from "react";
import AddIcon from "@mui/icons-material/Add";
import CalculateOutlinedIcon from "@mui/icons-material/CalculateOutlined";
import ChatBubbleOutlineIcon from "@mui/icons-material/ChatBubbleOutline";
import HistoryIcon from "@mui/icons-material/History";
import KeyboardDoubleArrowLeftRoundedIcon from "@mui/icons-material/KeyboardDoubleArrowLeftRounded";
import KeyboardDoubleArrowRightRoundedIcon from "@mui/icons-material/KeyboardDoubleArrowRightRounded";
import InsightsOutlinedIcon from "@mui/icons-material/InsightsOutlined";
import {
  Box,
  Button,
  Divider,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Tooltip,
  Typography,
} from "@mui/material";
import type { SxProps, Theme } from "@mui/material/styles";
import { useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../../context";
import { BrandIcon } from "../Icons";

interface SidebarProps {
  collapsed?: boolean;
  onOpenHistory?: () => void;
  onOpenAttach?: () => void;
  onNavigateReports?: () => void;
  onToggleCollapsed?: () => void;
}

interface NavItemConfig {
  key: string;
  label: string;
  icon: React.ReactNode;
  selected: boolean;
  onClick: () => void;
}

export function Sidebar({
  collapsed = false,
  onOpenHistory,
  onOpenAttach,
  onNavigateReports,
  onToggleCollapsed,
}: SidebarProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();

  const navItems: NavItemConfig[] = [
    {
      key: "chat",
      label: "Chat",
      icon: <ChatBubbleOutlineIcon fontSize="small" />,
      selected: location.pathname === "/",
      onClick: () => navigate("/"),
    },
    {
      key: "history",
      label: "Historial",
      icon: <HistoryIcon fontSize="small" />,
      selected: false,
      onClick: () => onOpenHistory?.(),
    },
    {
      key: "attach",
      label: "Ejercicios",
      icon: <CalculateOutlinedIcon fontSize="small" />,
      selected: false,
      onClick: () => onOpenAttach?.(),
    },
  ];

  if (user?.role === "teacher") {
    navItems.push({
      key: "reports",
      label: "Reportes",
      icon: <InsightsOutlinedIcon fontSize="small" />,
      selected: location.pathname === "/reports",
      onClick: () => {
        onNavigateReports?.();
        navigate("/reports");
      },
    });
  }

  const itemBaseSx: SxProps<Theme> = {
    minHeight: 44,
    borderRadius: 2,
    px: collapsed ? 1.25 : 1.5,
    justifyContent: collapsed ? "center" : "flex-start",
    gap: collapsed ? 0 : 1.25,
    color: "text.secondary",
    "&:hover": {
      bgcolor: "background.default",
    },
  };

  function renderNavItem(item: NavItemConfig) {
    const button = (
      <ListItemButton
        selected={item.selected}
        onClick={item.onClick}
        sx={{
          ...itemBaseSx,
          bgcolor: item.selected ? "primary.light" : "transparent",
          color: item.selected ? "primary.main" : "text.secondary",
          "&.Mui-selected": {
            bgcolor: "primary.light",
            color: "primary.main",
            "&:hover": {
              bgcolor: "primary.light",
            },
          },
        }}
      >
        <ListItemIcon
          sx={{
            minWidth: 0,
            color: "inherit",
            justifyContent: "center",
          }}
        >
          {item.icon}
        </ListItemIcon>
        {!collapsed ? (
          <ListItemText
            primary={item.label}
            primaryTypographyProps={{
              fontSize: "0.95rem",
              fontWeight: item.selected ? 700 : 600,
            }}
          />
        ) : null}
      </ListItemButton>
    );

    if (collapsed) {
      return (
        <Tooltip key={item.key} title={item.label} placement="right">
          {button}
        </Tooltip>
      );
    }

    return <React.Fragment key={item.key}>{button}</React.Fragment>;
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "column", height: "100%", bgcolor: "background.paper" }}>
      <Box
        sx={{
          px: collapsed ? 1.5 : 2.5,
          py: 2.5,
          display: "flex",
          alignItems: "center",
          justifyContent: collapsed ? "center" : "space-between",
          gap: 1.5,
        }}
      >
        <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, minWidth: 0 }}>
          <Box
            sx={{
              width: 40,
              height: 40,
              borderRadius: 2,
              bgcolor: "primary.light",
              display: "grid",
              placeItems: "center",
              color: "primary.main",
              flexShrink: 0,
            }}
          >
            <BrandIcon style={{ width: 20, height: 20 }} />
          </Box>
          {!collapsed ? (
            <Box sx={{ minWidth: 0 }}>
              <Typography variant="subtitle1" sx={{ color: "text.primary", whiteSpace: "nowrap" }}>
                Scholar Pro
              </Typography>
              <Typography variant="caption" sx={{ color: "text.secondary", letterSpacing: "0.04em" }}>
                Cubik IA
              </Typography>
            </Box>
          ) : null}
        </Box>

        {onToggleCollapsed ? (
          <IconButton
            onClick={onToggleCollapsed}
            size="small"
            sx={{
              borderRadius: 2,
              border: "1px solid",
              borderColor: "divider",
              display: { xs: "none", md: "inline-flex" },
            }}
          >
            {collapsed ? (
              <KeyboardDoubleArrowRightRoundedIcon fontSize="small" />
            ) : (
              <KeyboardDoubleArrowLeftRoundedIcon fontSize="small" />
            )}
          </IconButton>
        ) : null}
      </Box>

      <Divider />

      <List sx={{ px: collapsed ? 1 : 1.5, py: 2, display: "grid", gap: 0.75, flexGrow: 1 }}>
        {navItems.map((item) => (
          <ListItem key={item.key} disablePadding>
            {renderNavItem(item)}
          </ListItem>
        ))}
      </List>

      <Box sx={{ px: collapsed ? 1 : 2, pb: 2.5 }}>
        {collapsed ? (
          <Tooltip title="Nuevo ejercicio" placement="right">
            <Button variant="contained" fullWidth onClick={onOpenAttach} sx={{ minWidth: 0, px: 0 }}>
              <AddIcon />
            </Button>
          </Tooltip>
        ) : (
          <Button variant="contained" fullWidth onClick={onOpenAttach} startIcon={<AddIcon />}>
            Nuevo ejercicio
          </Button>
        )}
      </Box>
    </Box>
  );
}
