import { describe, expect, it } from "vitest";

import { buildQuery, formatErrorDetail } from "../client";

// ---------------------------------------------------------------------------
// PU-23: formatErrorDetail
// ---------------------------------------------------------------------------

describe("formatErrorDetail", () => {
  describe("casos normales", () => {
    it("retorna el string para mensaje de texto plano", () => {
      expect(formatErrorDetail("Credenciales inválidas")).toBe("Credenciales inválidas");
    });

    it("extrae msg de objeto de error de validación FastAPI", () => {
      const detail = { msg: "field required", loc: ["body", "email"] };
      expect(formatErrorDetail(detail)).toContain("field required");
    });

    it("incluye la ruta (loc) en el mensaje", () => {
      const detail = { msg: "field required", loc: ["body", "email"] };
      expect(formatErrorDetail(detail)).toContain("body.email");
    });

    it("aplana array de mensajes de error", () => {
      const detail = ["Error A", "Error B"];
      const result = formatErrorDetail(detail);
      expect(result).toContain("Error A");
      expect(result).toContain("Error B");
    });
  });

  describe("casos limite", () => {
    it("deduplica mensajes idénticos en array", () => {
      expect(formatErrorDetail(["mismo error", "mismo error"])).toBe("mismo error");
    });

    it("extrae campo 'detail' de objeto anidado", () => {
      expect(formatErrorDetail({ detail: "error anidado" })).toBe("error anidado");
    });

    it("extrae campo 'error' si no hay 'detail'", () => {
      expect(formatErrorDetail({ error: "algo salió mal" })).toBe("algo salió mal");
    });

    it("extrae campo 'message' como último recurso", () => {
      expect(formatErrorDetail({ message: "mensaje de error" })).toBe("mensaje de error");
    });

    it("retorna msg sin prefijo de loc cuando loc está ausente", () => {
      expect(formatErrorDetail({ msg: "valor inválido" })).toBe("valor inválido");
    });
  });

  describe("caso erroneo", () => {
    it("retorna null para null", () => {
      expect(formatErrorDetail(null)).toBeNull();
    });

    it("retorna null para undefined", () => {
      expect(formatErrorDetail(undefined)).toBeNull();
    });

    it("retorna null para string vacío", () => {
      expect(formatErrorDetail("")).toBeNull();
    });

    it("retorna null para string de solo espacios", () => {
      expect(formatErrorDetail("   ")).toBeNull();
    });

    it("retorna null para array de strings vacíos", () => {
      expect(formatErrorDetail(["", "  "])).toBeNull();
    });
  });
});

// ---------------------------------------------------------------------------
// PU-24: buildQuery
// ---------------------------------------------------------------------------

describe("buildQuery", () => {
  describe("casos normales", () => {
    it("construye query string con un parámetro", () => {
      expect(buildQuery({ start: "2024-01-01" })).toBe("?start=2024-01-01");
    });

    it("incluye múltiples parámetros en la query", () => {
      const result = buildQuery({ start: "2024-01-01", end: "2024-12-31" });
      expect(result).toContain("start=2024-01-01");
      expect(result).toContain("end=2024-12-31");
      expect(result.startsWith("?")).toBe(true);
    });

    it("retorna string que empieza con ?", () => {
      expect(buildQuery({ key: "value" }).startsWith("?")).toBe(true);
    });
  });

  describe("casos limite", () => {
    it("omite parámetros con valor undefined", () => {
      const result = buildQuery({ start: "2024-01-01", search: undefined });
      expect(result).not.toContain("search");
      expect(result).toContain("start=2024-01-01");
    });

    it("omite parámetros con string vacío", () => {
      const result = buildQuery({ start: "2024-01-01", search: "" });
      expect(result).not.toContain("search");
    });

    it("omite parámetros con solo espacios", () => {
      const result = buildQuery({ search: "   " });
      expect(result).toBe("");
    });
  });

  describe("caso erroneo", () => {
    it("retorna string vacío para objeto vacío", () => {
      expect(buildQuery({})).toBe("");
    });

    it("retorna string vacío cuando todos los parámetros son undefined", () => {
      expect(buildQuery({ start: undefined, end: undefined })).toBe("");
    });
  });
});
