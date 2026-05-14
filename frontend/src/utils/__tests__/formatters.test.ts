import { describe, expect, it } from "vitest";

import { formatTimestamp, labelForProblemType } from "../formatters";

// ---------------------------------------------------------------------------
// PU-18: formatTimestamp
// ---------------------------------------------------------------------------

describe("formatTimestamp", () => {
  describe("casos normales", () => {
    it("retorna string no vacío para timestamp ISO válido", () => {
      const result = formatTimestamp("2024-05-15T10:30:00.000Z");
      expect(typeof result).toBe("string");
      expect(result.length).toBeGreaterThan(0);
    });

    it("produce salida diferente para timestamps distintos", () => {
      const r1 = formatTimestamp("2024-01-01T08:00:00.000Z");
      const r2 = formatTimestamp("2024-06-15T20:00:00.000Z");
      expect(r1).not.toBe(r2);
    });

    it("incluye dígitos de hora y minuto en la salida", () => {
      const result = formatTimestamp("2024-05-15T14:45:00.000Z");
      expect(result).toMatch(/\d{1,2}[:\s.]\d{2}/);
    });
  });

  describe("casos limite", () => {
    it("maneja timestamps de inicio y fin de día", () => {
      const midnight = formatTimestamp("2024-03-10T00:00:00.000Z");
      const endOfDay = formatTimestamp("2024-03-10T23:59:00.000Z");
      expect(midnight).not.toBe(endOfDay);
    });

    it("produce salidas distintas para meses distintos", () => {
      const enero = formatTimestamp("2024-01-15T12:00:00.000Z");
      const junio = formatTimestamp("2024-06-15T12:00:00.000Z");
      expect(enero).not.toBe(junio);
    });
  });

  describe("caso erroneo", () => {
    it("lanza RangeError para string vacío", () => {
      expect(() => formatTimestamp("")).toThrow(RangeError);
    });

    it("lanza RangeError para string no fecha", () => {
      expect(() => formatTimestamp("no-es-una-fecha")).toThrow(RangeError);
    });
  });
});

// ---------------------------------------------------------------------------
// PU-19: labelForProblemType
// ---------------------------------------------------------------------------

describe("labelForProblemType", () => {
  describe("casos normales", () => {
    it("retorna 'Derivada' para derivative", () => {
      expect(labelForProblemType("derivative")).toBe("Derivada");
    });

    it("retorna 'Integral' para integral", () => {
      expect(labelForProblemType("integral")).toBe("Integral");
    });

    it("retorna 'Límite' para limit", () => {
      expect(labelForProblemType("limit")).toBe("Límite");
    });

    it("retorna 'Ecuación' para equation", () => {
      expect(labelForProblemType("equation")).toBe("Ecuación");
    });

    it("retorna 'Simplificación' para simplification", () => {
      expect(labelForProblemType("simplification")).toBe("Simplificación");
    });
  });

  describe("casos limite", () => {
    it("retorna 'No identificado' para tipo 'unknown'", () => {
      expect(labelForProblemType("unknown")).toBe("No identificado");
    });
  });

  describe("caso erroneo", () => {
    it("retorna 'No identificado' para null", () => {
      expect(labelForProblemType(null)).toBe("No identificado");
    });
  });
});
