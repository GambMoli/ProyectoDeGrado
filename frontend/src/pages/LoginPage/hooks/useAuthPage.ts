import { useMemo, useState } from "react";

import { useAuth } from "../../../context";

type AuthTab = "login" | "register";
type Role = "student" | "teacher";

interface LoginFormState {
  email: string;
  password: string;
}

interface RegisterFormState {
  displayName: string;
  email: string;
  password: string;
  role: Role;
  teacherAccessCode: string;
}

function isValidEmail(value: string): boolean {
  const normalized = value.trim();
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(normalized);
}

const initialLoginState: LoginFormState = {
  email: "",
  password: "",
};

const initialRegisterState: RegisterFormState = {
  displayName: "",
  email: "",
  password: "",
  role: "student",
  teacherAccessCode: "",
};

export function useAuthPage() {
  const { login, register } = useAuth();
  const [tab, setTab] = useState<AuthTab>("login");
  const [loginForm, setLoginForm] = useState(initialLoginState);
  const [registerForm, setRegisterForm] = useState(initialRegisterState);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const subtitle = useMemo(
    () =>
      tab === "login"
        ? "Inicia sesion para acceder al tutor y a tu historial."
        : "Crea una cuenta para usar el tutor. Los profesores pueden ver reportes.",
    [tab],
  );

  function validateCurrentForm(): string | null {
    if (tab === "login") {
      if (!isValidEmail(loginForm.email)) {
        return "Ingresa un correo valido para iniciar sesion.";
      }
      if (loginForm.password.trim().length < 8) {
        return "La contrasena debe tener al menos 8 caracteres.";
      }
      return null;
    }

    if (registerForm.displayName.trim().length < 2) {
      return "Ingresa un nombre valido.";
    }
    if (!isValidEmail(registerForm.email)) {
      return "Ingresa un correo valido para registrarte.";
    }
    if (registerForm.password.trim().length < 8) {
      return "La contrasena debe tener al menos 8 caracteres.";
    }
    if (registerForm.role === "teacher" && !registerForm.teacherAccessCode.trim()) {
      return "Para crear un profesor debes ingresar el codigo de acceso.";
    }
    return null;
  }

  async function handleSubmit() {
    setError(null);
    const validationError = validateCurrentForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setIsSubmitting(true);
    try {
      if (tab === "login") {
        await login(loginForm);
        return;
      }

      await register({
        display_name: registerForm.displayName,
        email: registerForm.email,
        password: registerForm.password,
        role: registerForm.role,
        teacher_access_code:
          registerForm.role === "teacher" ? registerForm.teacherAccessCode : undefined,
      });
    } catch (nextError) {
      setError(
        nextError instanceof Error
          ? nextError.message
          : "No se pudo completar la autenticacion.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return {
    error,
    isSubmitting,
    loginForm,
    registerForm,
    subtitle,
    tab,
    clearError: () => setError(null),
    handleSubmit,
    setLoginForm,
    setRegisterForm,
    setTab,
  };
}
