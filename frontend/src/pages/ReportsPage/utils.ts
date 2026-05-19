import type { TopicReportSummary } from "../../types/api";

export function formatDateInput(value: Date): string {
  return value.toISOString().slice(0, 10);
}

export function formatDateRange(start: string, end: string): string {
  const formatter = new Intl.DateTimeFormat("es-CO", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
  return `${formatter.format(new Date(`${start}T00:00:00`))} - ${formatter.format(
    new Date(`${end}T00:00:00`),
  )}`;
}

export function formatWholeNumber(value: number): string {
  return new Intl.NumberFormat("es-CO").format(value);
}

export function formatOneDecimal(value: number): string {
  return new Intl.NumberFormat("es-CO", {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  }).format(value);
}

export function formatPercentage(value: number): string {
  return `${Math.round(value * 100)}%`;
}

export function formatChange(value: number | null): string {
  if (value === null) {
    return "Sin período previo";
  }
  const sign = value >= 0 ? "+" : "";
  return `${sign}${Math.round(value * 100)}% vs tema anterior`;
}

export function interactionLevelLabel(value: TopicReportSummary["interaction_level"]): string {
  if (value === "high") {
    return "Alto";
  }
  if (value === "medium") {
    return "Medio";
  }
  return "Bajo";
}

export function initialsForName(name: string): string {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? "")
    .join("");
}
