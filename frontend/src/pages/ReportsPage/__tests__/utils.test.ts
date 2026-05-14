import { describe, expect, it } from "vitest";

import { formatChange, formatDateInput, formatPercentage, initialsForName } from "../utils";

// ---------------------------------------------------------------------------
// PU-18 (complemento): formatDateInput
// ---------------------------------------------------------------------------

describe("formatDateInput", () => {
  describe("casos normales", () => {
    it("formatea fecha a YYYY-MM-DD", () => {
      const result = formatDateInput(new Date("2024-05-15T12:00:00.000Z"));
      expect(result).toBe("2024-05-15");
    });

    it("retorna string de exactamente 10 caracteres", () => {
      expect(formatDateInput(new Date("2024-01-01T00:00:00.000Z"))).toHaveLength(10);
    });
  });

  describe("casos limite", () => {
    it("formatea correctamente el primer día del año", () => {
      const result = formatDateInput(new Date("2024-01-01T00:00:00.000Z"));
      expect(result).toBe("2024-01-01");
    });

    it("formatea correctamente el último día del año", () => {
      const result = formatDateInput(new Date("2024-12-31T00:00:00.000Z"));
      expect(result).toBe("2024-12-31");
    });
  });

  describe("caso erroneo", () => {
    it("lanza RangeError para fecha inválida", () => {
      expect(() => formatDateInput(new Date("invalid"))).toThrow(RangeError);
    });
  });
});

// ---------------------------------------------------------------------------
// PU-20: formatPercentage
// ---------------------------------------------------------------------------

describe("formatPercentage", () => {
  describe("casos normales", () => {
    it("convierte 0.75 a '75%'", () => {
      expect(formatPercentage(0.75)).toBe("75%");
    });

    it("convierte 1.0 a '100%'", () => {
      expect(formatPercentage(1.0)).toBe("100%");
    });

    it("convierte 0.5 a '50%'", () => {
      expect(formatPercentage(0.5)).toBe("50%");
    });
  });

  describe("casos limite", () => {
    it("convierte 0 a '0%'", () => {
      expect(formatPercentage(0)).toBe("0%");
    });

    it("redondea decimales (0.333 → '33%')", () => {
      expect(formatPercentage(0.333)).toBe("33%");
    });

    it("formatea valor mayor a 1 (1.5 → '150%')", () => {
      expect(formatPercentage(1.5)).toBe("150%");
    });
  });

  describe("caso erroneo", () => {
    it("formatea valor negativo con signo menos", () => {
      expect(formatPercentage(-0.5)).toBe("-50%");
    });
  });
});

// ---------------------------------------------------------------------------
// PU-21: formatChange
// ---------------------------------------------------------------------------

describe("formatChange", () => {
  describe("casos normales", () => {
    it("formatea cambio positivo con signo +", () => {
      expect(formatChange(0.5)).toBe("+50% vs tema anterior");
    });

    it("formatea cambio negativo con signo -", () => {
      expect(formatChange(-0.3)).toBe("-30% vs tema anterior");
    });

    it("incluye texto 'vs tema anterior'", () => {
      expect(formatChange(0.2)).toContain("vs tema anterior");
    });
  });

  describe("casos limite", () => {
    it("formatea cero como +0%", () => {
      expect(formatChange(0)).toBe("+0% vs tema anterior");
    });

    it("redondea decimales (0.333 → +33%)", () => {
      expect(formatChange(0.333)).toBe("+33% vs tema anterior");
    });
  });

  describe("caso erroneo", () => {
    it("retorna 'Sin periodo previo' para null", () => {
      expect(formatChange(null)).toBe("Sin periodo previo");
    });
  });
});

// ---------------------------------------------------------------------------
// PU-22: initialsForName
// ---------------------------------------------------------------------------

describe("initialsForName", () => {
  describe("casos normales", () => {
    it("extrae dos iniciales de nombre completo", () => {
      expect(initialsForName("Juan Pérez")).toBe("JP");
    });

    it("retorna iniciales en mayúsculas", () => {
      expect(initialsForName("ana garcía")).toBe("AG");
    });

    it("retorna una sola inicial para nombre de una palabra", () => {
      expect(initialsForName("Carlos")).toBe("C");
    });
  });

  describe("casos limite", () => {
    it("retorna máximo dos iniciales para nombre con más de dos palabras", () => {
      expect(initialsForName("María del Carmen López")).toBe("MD");
    });

    it("maneja espacios extra entre palabras", () => {
      expect(initialsForName("  Juan   Pérez  ")).toBe("JP");
    });
  });

  describe("caso erroneo", () => {
    it("retorna string vacío para nombre vacío", () => {
      expect(initialsForName("")).toBe("");
    });

    it("retorna string vacío para solo espacios", () => {
      expect(initialsForName("   ")).toBe("");
    });
  });
});
