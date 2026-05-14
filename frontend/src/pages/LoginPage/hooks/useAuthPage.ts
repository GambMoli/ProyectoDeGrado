import { useMemo, useState } from "react";

import { useAuth } from "../../../context";
import { isValidEmail, matchesPasswordStandard } from "../../../utils/validators";

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
  confirmPassword: string;
  role: Role;
  teacherAccessCode: string;
}

interface FormFieldErrors {
  displayName?: string;
  email?: string;
  password?: string;
  confirmPassword?: string;
  teacherAccessCode?: string;
}

const PASSWORD_STANDARD_MESSAGE =
  "La contrase\u00f1a debe tener al menos 8 caracteres, una may\u00fascula, una min\u00fascula, un n\u00famero y un car\u00e1cter especial.";

const initialLoginState: LoginFormState = {
  email: "",
  password: "",
};

const initialRegisterState: RegisterFormState = {
  displayName: "",
  email: "",
  password: "",
  confirmPassword: "",
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
  const [loginErrors, setLoginErrors] = useState<FormFieldErrors>({});
  const [registerErrors, setRegisterErrors] = useState<FormFieldErrors>({});

  const subtitle = useMemo(
    () =>
      tab === "login"
        ? "Inicia sesi\u00f3n para acceder al tutor y a tu historial."
        : "Crea una cuenta para usar el tutor. Los profesores pueden ver reportes.",
    [tab],
  );

  function validateLoginForm(values: LoginFormState): FormFieldErrors {
    const nextErrors: FormFieldErrors = {};

    if (!values.email.trim()) {
      nextErrors.email = "El correo es obligatorio.";
    } else if (!isValidEmail(values.email)) {
      nextErrors.email = "Ingresa un correo v\u00e1lido.";
    }

    if (!values.password.trim()) {
      nextErrors.password = "La contrase\u00f1a es obligatoria.";
    } else if (values.password.trim().length < 8) {
      nextErrors.password = "La contrase\u00f1a debe tener al menos 8 caracteres.";
    }

    return nextErrors;
  }

  function validateRegisterForm(values: RegisterFormState): FormFieldErrors {
    const nextErrors: FormFieldErrors = {};

    if (values.displayName.trim().length < 2) {
      nextErrors.displayName = "Ingresa un nombre v\u00e1lido.";
    }

    if (!values.email.trim()) {
      nextErrors.email = "El correo es obligatorio.";
    } else if (!isValidEmail(values.email)) {
      nextErrors.email = "Ingresa un correo v\u00e1lido.";
    }

    if (!values.password.trim()) {
      nextErrors.password = "La contrase\u00f1a es obligatoria.";
    } else if (!matchesPasswordStandard(values.password)) {
      nextErrors.password = PASSWORD_STANDARD_MESSAGE;
    }

    if (!values.confirmPassword.trim()) {
      nextErrors.confirmPassword = "Confirma tu contrase\u00f1a.";
    } else if (values.password !== values.confirmPassword) {
      nextErrors.confirmPassword = "Las contrase\u00f1as no coinciden.";
    }

    if (values.role === "teacher" && !values.teacherAccessCode.trim()) {
      nextErrors.teacherAccessCode = "Ingresa el c\u00f3digo de acceso para profesor.";
    }

    return nextErrors;
  }

  function getFirstErrorMessage(errors: FormFieldErrors): string | null {
    return Object.values(errors).find((value) => Boolean(value)) ?? null;
  }

  async function handleSubmit() {
    setError(null);

    if (tab === "login") {
      const nextErrors = validateLoginForm(loginForm);
      setLoginErrors(nextErrors);
      const validationError = getFirstErrorMessage(nextErrors);
      if (validationError) {
        setError(validationError);
        return;
      }
    } else {
      const nextErrors = validateRegisterForm(registerForm);
      setRegisterErrors(nextErrors);
      const validationError = getFirstErrorMessage(nextErrors);
      if (validationError) {
        setError(validationError);
        return;
      }
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
          : "No se pudo completar la autenticaci\u00f3n.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return {
    error,
    isSubmitting,
    loginForm,
    loginErrors,
    registerForm,
    registerErrors,
    subtitle,
    tab,
    clearError: () => setError(null),
    handleSubmit,
    validateLoginForm,
    validateRegisterForm,
    setLoginForm,
    setLoginErrors,
    setRegisterForm,
    setRegisterErrors,
    setTab,
  };
}
