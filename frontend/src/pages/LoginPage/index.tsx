import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  MenuItem,
  Stack,
  Tab,
  Tabs,
  TextField,
  Typography,
} from "@mui/material";
import { Navigate } from "react-router-dom";

import { useAuth } from "../../context";
import { useAuthPage } from "./hooks/useAuthPage";

type AuthTab = "login" | "register";
type Role = "student" | "teacher";

export function LoginPage() {
  const { isAuthenticated, user } = useAuth();
  const {
    error,
    isSubmitting,
    loginForm,
    registerForm,
    subtitle,
    tab,
    clearError,
    handleSubmit,
    setLoginForm,
    setRegisterForm,
    setTab,
  } = useAuthPage();

  if (isAuthenticated && user) {
    return <Navigate to={user.role === "teacher" ? "/reports" : "/"} replace />;
  }

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "grid",
        placeItems: "center",
        px: 2,
        py: 4,
        background: "linear-gradient(180deg, #EFF6FF 0%, #F9FAFB 100%)",
      }}
    >
      <Card
        sx={{
          width: "100%",
          maxWidth: 460,
          borderRadius: 4,
          boxShadow: "0 24px 60px rgba(15,23,42,0.08)",
        }}
      >
        <CardContent sx={{ p: 4 }}>
          <Stack spacing={1.5} sx={{ mb: 3 }}>
            <Typography
              variant="overline"
              sx={{ color: "#1E3A8A", fontWeight: 800, letterSpacing: "0.12em" }}
            >
              Cubik IA
            </Typography>
            <Typography variant="h4" sx={{ fontWeight: 800, color: "#111827" }}>
              {tab === "login" ? "Bienvenido de nuevo" : "Crea tu cuenta"}
            </Typography>
            <Typography variant="body2" sx={{ color: "#6B7280", fontWeight: 500 }}>
              {subtitle}
            </Typography>
          </Stack>

          <Tabs
            value={tab}
            onChange={(_, value: AuthTab) => {
              clearError();
              setTab(value);
            }}
            sx={{ mb: 3 }}
          >
            <Tab label="Iniciar sesion" value="login" />
            <Tab label="Registrarse" value="register" />
          </Tabs>

          {error ? <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert> : null}

          <Stack spacing={2.5}>
            {tab === "login" ? (
              <>
                <TextField
                  label="Correo"
                  type="email"
                  value={loginForm.email}
                  onChange={(event) =>
                    setLoginForm((current) => ({ ...current, email: event.target.value }))
                  }
                  fullWidth
                />
                <TextField
                  label="Contrasena"
                  type="password"
                  value={loginForm.password}
                  onChange={(event) =>
                    setLoginForm((current) => ({ ...current, password: event.target.value }))
                  }
                  fullWidth
                />
              </>
            ) : (
              <>
                <TextField
                  label="Nombre"
                  value={registerForm.displayName}
                  onChange={(event) =>
                    setRegisterForm((current) => ({
                      ...current,
                      displayName: event.target.value,
                    }))
                  }
                  fullWidth
                />
                <TextField
                  label="Correo"
                  type="email"
                  value={registerForm.email}
                  onChange={(event) =>
                    setRegisterForm((current) => ({ ...current, email: event.target.value }))
                  }
                  fullWidth
                />
                <TextField
                  label="Contrasena"
                  type="password"
                  value={registerForm.password}
                  onChange={(event) =>
                    setRegisterForm((current) => ({ ...current, password: event.target.value }))
                  }
                  fullWidth
                />
                <TextField
                  select
                  label="Rol"
                  value={registerForm.role}
                  onChange={(event) =>
                    setRegisterForm((current) => ({
                      ...current,
                      role: event.target.value as Role,
                    }))
                  }
                  fullWidth
                >
                  <MenuItem value="student">Estudiante</MenuItem>
                  <MenuItem value="teacher">Profesor</MenuItem>
                </TextField>
                <Typography variant="caption" sx={{ color: "#6B7280", mt: -1 }}>
                  {registerForm.role === "teacher"
                    ? "Estas creando una cuenta de profesor con acceso a reportes."
                    : "Estas creando una cuenta de estudiante sin acceso a reportes."}
                </Typography>
                {registerForm.role === "teacher" ? (
                  <TextField
                    label="Codigo de acceso para profesor"
                    value={registerForm.teacherAccessCode}
                    onChange={(event) =>
                      setRegisterForm((current) => ({
                        ...current,
                        teacherAccessCode: event.target.value,
                      }))
                    }
                    fullWidth
                  />
                ) : null}
              </>
            )}

            <Button
              variant="contained"
              onClick={() => void handleSubmit()}
              disabled={isSubmitting}
              sx={{
                mt: 1,
                py: 1.4,
                borderRadius: 3,
                textTransform: "none",
                fontWeight: 700,
                bgcolor: "#1E3A8A",
                "&:hover": { bgcolor: "#1E40AF" },
              }}
            >
              {isSubmitting ? "Procesando..." : tab === "login" ? "Entrar" : "Crear cuenta"}
            </Button>
          </Stack>
        </CardContent>
      </Card>
    </Box>
  );
}
