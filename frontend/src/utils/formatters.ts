import type { ExerciseStatus, MessageRole, ProblemType } from "../types/api";

export function formatTimestamp(value: string): string {
  const date = new Date(value);
  return new Intl.DateTimeFormat("es-CO", {
    hour: "2-digit",
    minute: "2-digit",
    day: "2-digit",
    month: "short",
  }).format(date);
}

export function labelForProblemType(problemType: ProblemType | null): string {
  switch (problemType) {
    case "derivative":
      return "Derivada";
    case "integral":
      return "Integral";
    case "limit":
      return "Límite";
    case "equation":
      return "Ecuación";
    case "simplification":
      return "Simplificación";
    default:
      return "No identificado";
  }
}

export function labelForExerciseStatus(status: ExerciseStatus): string {
  switch (status) {
    case "solved":
      return "Resuelto";
    case "ocr_failed":
      return "OCR falló";
    case "parse_failed":
      return "No se pudo interpretar";
    case "solver_failed":
      return "No se pudo resolver";
    default:
      return "Recibido";
  }
}

export function labelForRole(role: MessageRole): string {
  switch (role) {
    case "assistant":
      return "Tutor IA";
    case "system":
      return "Sistema";
    default:
      return "Tú";
  }
}
