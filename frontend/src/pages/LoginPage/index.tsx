import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  MenuItem,
  Paper,
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
        bgcolor: "background.default",
        backgroundImage:
          "radial-gradient(circle at top left, rgba(21,71,161,0.12), transparent 34%), radial-gradient(circle at bottom right, rgba(21,71,161,0.08), transparent 28%)",
      }}
    >
      <Box sx={{ width: "100%", maxWidth: 1100, display: "flex", flexDirection:"column", alignItems:"center", justifyContent:"center" }}>

        <Card sx={{ width: "100%", maxWidth: 520, justifySelf: "center", alignSelf: "center", borderRadius:6}}>
          <CardContent sx={{ p: { xs: 3, md: 4 }, "&:last-child": { pb: { xs: 3, md: 4 } } }}>
            <Stack spacing={1.5} sx={{ mb: 3 }}>
              <Typography variant="overline" sx={{ color: "primary.main", fontWeight: 800, letterSpacing: "0.12em" }}>
                Cubik IA
              </Typography>
              <Typography variant="h4" sx={{ color: "text.primary" }}>
                {tab === "login" ? "Accede a tu espacio academico" : "Crea tu cuenta institucional"}
              </Typography>
              <Typography variant="body2" sx={{ color: "text.secondary", fontWeight: 500 }}>
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
                    label="Contraseña"
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
                    label="Contraseña"
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
                  <Typography variant="caption" sx={{ color: "text.secondary", mt: -1 }}>
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

              <Button variant="contained" onClick={() => void handleSubmit()} disabled={isSubmitting}>
                {isSubmitting ? "Procesando..." : tab === "login" ? "Entrar" : "Crear cuenta"}
              </Button>
            </Stack>
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
}
