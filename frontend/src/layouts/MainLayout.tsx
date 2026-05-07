import React, { useState } from "react";
import LogoutIcon from "@mui/icons-material/Logout";
import MenuIcon from "@mui/icons-material/Menu";
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
  onNewChat?: () => void;
}

export function MainLayout({ children, onOpenHistory, onOpenAttach, onNewChat }: MainLayoutProps) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const theme = useTheme();
  const isDesktop = useMediaQuery(theme.breakpoints.up("md"));
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
    <Box sx={{ display: "flex", height: "100vh", overflow: "hidden", bgcolor: "background.default" }}>
      <Box component="nav" sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}>
        <Drawer
          variant={isDesktop ? "permanent" : "temporary"}
          open={isDesktop ? true : mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{ keepMounted: true }}
          sx={{
            "& .MuiDrawer-paper": {
              boxSizing: "border-box",
              width: drawerWidth,
              borderRight: "1px solid",
              borderColor: "divider",
              bgcolor: "background.paper",
            },
          }}
        >
          <Sidebar onOpenHistory={onOpenHistory} onOpenAttach={onOpenAttach} onNewChat={onNewChat} />
        </Drawer>
      </Box>

      <Box
        sx={{
          flexGrow: 1,
          display: "flex",
          flexDirection: "column",
          width: { md: `calc(100% - ${drawerWidth}px)` },
          minWidth: 0,
        }}
      >
        <AppBar
          position="sticky"
          elevation={0}
          sx={{
            bgcolor: "background.paper",
            color: "text.primary",
            borderBottom: "1px solid",
            borderColor: "divider",
          }}
        >
          <Toolbar
            sx={{
              justifyContent: "space-between",
              minHeight: { xs: "56px !important", sm: "64px !important" },
              px: { xs: 1.5, sm: 2, md: 3 },
            }}
          >
            <Box sx={{ display: "flex", alignItems: "center", gap: { xs: 1, sm: 2 } }}>
              {!isDesktop ? (
                <IconButton color="inherit" edge="start" onClick={handleDrawerToggle}>
                  <MenuIcon />
                </IconButton>
              ) : null}

              <Typography
                variant="h6"
                sx={{
                  fontWeight: 800,
                  color: "primary.main",
                  fontFamily: "Manrope, Inter, sans-serif",
                  fontSize: { xs: "1rem", sm: "1.1rem", md: "1.25rem" },
                }}
              >
                Cubik IA
              </Typography>
            </Box>

            <Box sx={{ display: "flex", alignItems: "center", gap: { xs: 1, sm: 1.5 } }}>
              <Button
                onClick={() => void handleLogout()}
                size="small"
                startIcon={<LogoutIcon fontSize="small" />}
                sx={{
                  textTransform: "none",
                  color: "text.secondary",
                  fontWeight: 700,
                  fontFamily: "Inter, Segoe UI, system-ui, sans-serif",
                  minWidth: "unset",
                  px: { xs: 1, sm: 1.5 },
                  fontSize: { xs: "0.8rem", sm: "0.875rem" },
                  "&:hover": {
                    color: "error.main",
                    bgcolor: "rgba(211, 47, 47, 0.08)",
                  },
                }}
              >
                Salir
              </Button>

              <Avatar
                sx={{
                  width: { xs: 28, sm: 32 },
                  height: { xs: 28, sm: 32 },
                  bgcolor: "primary.light",
                  fontSize: { xs: "0.75rem", sm: "0.875rem" },
                  fontWeight: 700,
                  fontFamily: "Inter, Segoe UI, system-ui, sans-serif",
                  color: "primary.dark",
                }}
              >
                {(user?.display_name ?? "US").slice(0, 2).toUpperCase()}
              </Avatar>
            </Box>
          </Toolbar>
        </AppBar>

        <Box
          component="main"
          sx={{
            flexGrow: 1,
            height: "100%",
            overflow: "auto",
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
