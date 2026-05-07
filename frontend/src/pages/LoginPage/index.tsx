import VisibilityOffOutlinedIcon from "@mui/icons-material/VisibilityOffOutlined";
import VisibilityOutlinedIcon from "@mui/icons-material/VisibilityOutlined";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  IconButton,
  InputAdornment,
  MenuItem,
  Stack,
  Tab,
  Tabs,
  TextField,
  Typography,
} from "@mui/material";
import { useState } from "react";
import { Navigate } from "react-router-dom";

import { useAuth } from "../../context";
import { useAuthPage } from "./hooks/useAuthPage";

type AuthTab = "login" | "register";
type Role = "student" | "teacher";

export function LoginPage() {
  const [showLoginPassword, setShowLoginPassword] = useState(false);
  const [showRegisterPassword, setShowRegisterPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const { isAuthenticated, user } = useAuth();
  const {
    error,
    isSubmitting,
    loginForm,
    loginErrors,
    registerForm,
    registerErrors,
    subtitle,
    tab,
    clearError,
    handleSubmit,
    setLoginErrors,
    setLoginForm,
    setRegisterErrors,
    setRegisterForm,
    setTab,
    validateLoginForm,
    validateRegisterForm,
  } = useAuthPage();

  if (isAuthenticated && user) {
    return <Navigate to={user.role === "teacher" ? "/reports" : "/"} replace />;
  }

  function getPasswordAdornment(isVisible: boolean, onToggle: () => void) {
    return (
      <InputAdornment position="end">
        <IconButton edge="end" onClick={onToggle} onMouseDown={(event) => event.preventDefault()}>
          {isVisible ? <VisibilityOffOutlinedIcon /> : <VisibilityOutlinedIcon />}
        </IconButton>
      </InputAdornment>
    );
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
      <Box
        sx={{
          width: "100%",
          maxWidth: 1100,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <Card
          sx={{
            width: "100%",
            maxWidth: 520,
            justifySelf: "center",
            alignSelf: "center",
            borderRadius: 6,
          }}
        >
          <CardContent sx={{ p: { xs: 3, md: 4 }, "&:last-child": { pb: { xs: 3, md: 4 } } }}>
            <Stack spacing={1.5} sx={{ mb: 3 }}>
              <Typography
                variant="overline"
                sx={{ color: "primary.main", fontWeight: 800, letterSpacing: "0.12em" }}
              >
                Cubik IA
              </Typography>
              <Typography variant="h4" sx={{ color: "text.primary" }}>
                {tab === "login" ? "Accede a tu espacio académico" : "Crea tu cuenta institucional"}
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
              <Tab label="Iniciar sesión" value="login" />
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
                    onChange={(event) => {
                      const nextForm = { ...loginForm, email: event.target.value };
                      setLoginForm(nextForm);
                      setLoginErrors(validateLoginForm(nextForm));
                    }}
                    onBlur={() => setLoginErrors(validateLoginForm(loginForm))}
                    error={Boolean(loginErrors.email)}
                    helperText={loginErrors.email}
                    fullWidth
                  />
                  <TextField
                    label="Contraseña"
                    type={showLoginPassword ? "text" : "password"}
                    value={loginForm.password}
                    onChange={(event) => {
                      const nextForm = { ...loginForm, password: event.target.value };
                      setLoginForm(nextForm);
                      setLoginErrors(validateLoginForm(nextForm));
                    }}
                    onBlur={() => setLoginErrors(validateLoginForm(loginForm))}
                    error={Boolean(loginErrors.password)}
                    helperText={loginErrors.password}
                    InputProps={{
                      endAdornment: getPasswordAdornment(showLoginPassword, () =>
                        setShowLoginPassword((current) => !current),
                      ),
                    }}
                    fullWidth
                  />
                </>
              ) : (
                <>
                  <TextField
                    label="Nombre"
                    value={registerForm.displayName}
                    onChange={(event) => {
                      const nextForm = { ...registerForm, displayName: event.target.value };
                      setRegisterForm(nextForm);
                      setRegisterErrors(validateRegisterForm(nextForm));
                    }}
                    onBlur={() => setRegisterErrors(validateRegisterForm(registerForm))}
                    error={Boolean(registerErrors.displayName)}
                    helperText={registerErrors.displayName}
                    fullWidth
                  />
                  <TextField
                    label="Correo"
                    type="email"
                    value={registerForm.email}
                    onChange={(event) => {
                      const nextForm = { ...registerForm, email: event.target.value };
                      setRegisterForm(nextForm);
                      setRegisterErrors(validateRegisterForm(nextForm));
                    }}
                    onBlur={() => setRegisterErrors(validateRegisterForm(registerForm))}
                    error={Boolean(registerErrors.email)}
                    helperText={registerErrors.email}
                    fullWidth
                  />
                  <TextField
                    label="Contraseña"
                    type={showRegisterPassword ? "text" : "password"}
                    value={registerForm.password}
                    onChange={(event) => {
                      const nextForm = { ...registerForm, password: event.target.value };
                      setRegisterForm(nextForm);
                      setRegisterErrors(validateRegisterForm(nextForm));
                    }}
                    onBlur={() => setRegisterErrors(validateRegisterForm(registerForm))}
                    error={Boolean(registerErrors.password)}
                    helperText={registerErrors.password}
                    InputProps={{
                      endAdornment: getPasswordAdornment(showRegisterPassword, () =>
                        setShowRegisterPassword((current) => !current),
                      ),
                    }}
                    fullWidth
                  />
                  <TextField
                    label="Confirmar contraseña"
                    type={showConfirmPassword ? "text" : "password"}
                    value={registerForm.confirmPassword}
                    onChange={(event) => {
                      const nextForm = { ...registerForm, confirmPassword: event.target.value };
                      setRegisterForm(nextForm);
                      setRegisterErrors(validateRegisterForm(nextForm));
                    }}
                    onBlur={() => setRegisterErrors(validateRegisterForm(registerForm))}
                    error={Boolean(registerErrors.confirmPassword)}
                    helperText={registerErrors.confirmPassword}
                    InputProps={{
                      endAdornment: getPasswordAdornment(showConfirmPassword, () =>
                        setShowConfirmPassword((current) => !current),
                      ),
                    }}
                    fullWidth
                  />
                  <TextField
                    select
                    label="Rol"
                    value={registerForm.role}
                    onChange={(event) => {
                      const nextForm = { ...registerForm, role: event.target.value as Role };
                      setRegisterForm(nextForm);
                      setRegisterErrors(validateRegisterForm(nextForm));
                    }}
                    fullWidth
                  >
                    <MenuItem value="student">Estudiante</MenuItem>
                    <MenuItem value="teacher">Profesor</MenuItem>
                  </TextField>
                  <Typography variant="caption" sx={{ color: "text.secondary", mt: -1 }}>
                    {registerForm.role === "teacher"
                      ? "Estás creando una cuenta de profesor con acceso a reportes."
                      : "Estás creando una cuenta de estudiante sin acceso a reportes."}
                  </Typography>
                  {registerForm.role === "teacher" ? (
                    <TextField
                      label="Código de acceso para profesor"
                      value={registerForm.teacherAccessCode}
                      onChange={(event) => {
                        const nextForm = {
                          ...registerForm,
                          teacherAccessCode: event.target.value,
                        };
                        setRegisterForm(nextForm);
                        setRegisterErrors(validateRegisterForm(nextForm));
                      }}
                      onBlur={() => setRegisterErrors(validateRegisterForm(registerForm))}
                      error={Boolean(registerErrors.teacherAccessCode)}
                      helperText={registerErrors.teacherAccessCode}
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
