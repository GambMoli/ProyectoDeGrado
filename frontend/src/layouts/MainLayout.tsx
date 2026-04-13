import React, { useState } from "react";
import ChatBubbleOutlineIcon from "@mui/icons-material/ChatBubbleOutline";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import MenuIcon from "@mui/icons-material/Menu";
import NotificationsNoneOutlinedIcon from "@mui/icons-material/NotificationsNoneOutlined";
import {
  AppBar,
  Avatar,
  Box,
  Button,
  Collapse,
  Drawer,
  IconButton,
  List,
  ListItemButton,
  ListItemText,
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

const NAV_LINKS = ["Curso", "Participantes", "Calificaciones", "Banco de contenido"];

export function MainLayout({ children, onOpenHistory, onOpenAttach }: MainLayoutProps) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [secondaryNavOpen, setSecondaryNavOpen] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
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
    <Box sx={{ display: "flex", minHeight: "100vh", bgcolor: "background.default" }}>
      {/* Sidebar */}
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
          <Sidebar onOpenHistory={onOpenHistory} onOpenAttach={onOpenAttach} />
        </Drawer>
      </Box>

      {/* Content area */}
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
          {/* Primary toolbar */}
          <Toolbar
            sx={{
              justifyContent: "space-between",
              minHeight: { xs: "56px !important", sm: "64px !important" },
              px: { xs: 1.5, sm: 2, md: 3 },
            }}
          >
            {/* Left side */}
            <Box sx={{ display: "flex", alignItems: "center", gap: { xs: 1, sm: 2, md: 3 } }}>
              {/* Hamburger — hidden on desktop */}
              {!isDesktop ? (
                <IconButton color="inherit" edge="start" onClick={handleDrawerToggle}>
                  <MenuIcon />
                </IconButton>
              ) : null}

              {/* Logo */}
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

              {/* Top nav links — tablet and up */}
              {!isMobile ? (
                <Box sx={{ display: "flex", gap: { sm: 2, md: 3 } }}>
                  {["Pagina Principal", "Mis cursos"].map((label) => (
                    <Typography
                      key={label}
                      variant="body2"
                      sx={{
                        fontWeight: 700,
                        cursor: "pointer",
                        color: "text.secondary",
                        fontFamily: "Inter, Segoe UI, system-ui, sans-serif",
                        fontSize: { sm: "0.8rem", md: "0.875rem" },
                        "&:hover": { color: "primary.main" },
                      }}
                    >
                      {label}
                    </Typography>
                  ))}
                </Box>
              ) : null}
            </Box>

            {/* Right side */}
            <Box sx={{ display: "flex", alignItems: "center", gap: { xs: 0.5, sm: 1, md: 2 } }}>
              <IconButton size="small" sx={{ color: "text.secondary" }}>
                <NotificationsNoneOutlinedIcon fontSize={isMobile ? "small" : "medium"} />
              </IconButton>

              {!isMobile ? (
                <IconButton size="small" sx={{ color: "text.secondary" }}>
                  <ChatBubbleOutlineIcon fontSize="small" />
                </IconButton>
              ) : null}

              <Button
                onClick={() => void handleLogout()}
                size="small"
                sx={{
                  textTransform: "none",
                  color: "text.secondary",
                  fontWeight: 700,
                  fontFamily: "Inter, Segoe UI, system-ui, sans-serif",
                  minWidth: "unset",
                  px: { xs: 1, sm: 1.5 },
                  fontSize: { xs: "0.8rem", sm: "0.875rem" },
                  "&:hover": { color: "primary.main" },
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

          {/* Secondary nav */}
          <Box sx={{ bgcolor: "primary.main", color: "#fff" }}>
            {isMobile ? (
              /* Mobile: collapsible dropdown */
              <>
                <Box
                  onClick={() => setSecondaryNavOpen((o) => !o)}
                  sx={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    px: 2,
                    py: 1,
                    cursor: "pointer",
                    userSelect: "none",
                  }}
                >
                  <Typography
                    variant="body2"
                    sx={{ fontFamily: "Inter, Segoe UI, system-ui, sans-serif", fontWeight: 600 }}
                  >
                    Navegación del curso
                  </Typography>
                  <ExpandMoreIcon
                    fontSize="small"
                    sx={{
                      transition: "transform 0.25s",
                      transform: secondaryNavOpen ? "rotate(180deg)" : "rotate(0deg)",
                    }}
                  />
                </Box>

                <Collapse in={secondaryNavOpen}>
                  <List disablePadding sx={{ pb: 1 }}>
                    {NAV_LINKS.map((label) => (
                      <ListItemButton
                        key={label}
                        sx={{ px: 3, py: 0.75, "&:hover": { bgcolor: "rgba(255,255,255,0.1)" } }}
                      >
                        <ListItemText
                          primary={label}
                          primaryTypographyProps={{
                            fontSize: "0.875rem",
                            fontFamily: "Inter, Segoe UI, system-ui, sans-serif",
                            color: "#fff",
                          }}
                        />
                      </ListItemButton>
                    ))}

                    {user?.role === "teacher" ? (
                      <ListItemButton
                        sx={{ px: 3, py: 0.75, "&:hover": { bgcolor: "rgba(255,255,255,0.1)" } }}
                      >
                        <ListItemText
                          primary="Reportes"
                          primaryTypographyProps={{
                            fontSize: "0.875rem",
                            fontWeight: 700,
                            fontFamily: "Manrope, Inter, sans-serif",
                            color: "#fff",
                          }}
                        />
                      </ListItemButton>
                    ) : null}

                    <ListItemButton
                      sx={{ px: 3, py: 0.75, "&:hover": { bgcolor: "rgba(255,255,255,0.1)" } }}
                    >
                      <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                        <ChatBubbleOutlineIcon fontSize="small" />
                        <Typography
                          variant="body2"
                          sx={{ fontFamily: "Inter, Segoe UI, system-ui, sans-serif", color: "#fff" }}
                        >
                          Chatbot
                        </Typography>
                      </Box>
                    </ListItemButton>
                  </List>
                </Collapse>
              </>
            ) : (
              /* Tablet & desktop: horizontal scrollable row */
              <Box
                sx={{
                  display: "flex",
                  gap: { sm: 2, md: 4 },
                  alignItems: "center",
                  py: 1.5,
                  px: { sm: 2, md: 4 },
                  overflowX: "auto",
                  whiteSpace: "nowrap",
                  "&::-webkit-scrollbar": { display: "none" },
                  scrollbarWidth: "none",
                }}
              >
                {NAV_LINKS.map((label) => (
                  <Typography
                    key={label}
                    variant="body2"
                    sx={{
                      cursor: "pointer",
                      opacity: 0.8,
                      fontFamily: "Inter, Segoe UI, system-ui, sans-serif",
                      fontSize: { sm: "0.8rem", md: "0.875rem" },
                      "&:hover": { opacity: 1 },
                    }}
                  >
                    {label}
                  </Typography>
                ))}

                {user?.role === "teacher" ? (
                  <Typography
                    variant="body2"
                    sx={{
                      cursor: "pointer",
                      fontWeight: 700,
                      fontFamily: "Manrope, Inter, sans-serif",
                      borderBottom: "2px solid #fff",
                      pb: 0.5,
                      fontSize: { sm: "0.8rem", md: "0.875rem" },
                    }}
                  >
                    REPORTES
                  </Typography>
                ) : null}

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
                  <Typography
                    variant="body2"
                    sx={{
                      fontFamily: "Inter, Segoe UI, system-ui, sans-serif",
                      fontSize: { sm: "0.8rem", md: "0.875rem" },
                    }}
                  >
                    Chatbot
                  </Typography>
                </Box>
              </Box>
            )}
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