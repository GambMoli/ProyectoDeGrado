import { describe, expect, it } from "vitest";

import { isValidEmail, matchesPasswordStandard } from "../validators";

// ---------------------------------------------------------------------------
// PU-01: isValidEmail
// ---------------------------------------------------------------------------

describe("isValidEmail", () => {
  describe("casos normales", () => {
    it("retorna true para email válido", () => {
      expect(isValidEmail("user@example.com")).toBe(true);
    });

    it("retorna true para email con subdominio", () => {
      expect(isValidEmail("user@mail.example.co")).toBe(true);
    });

    it("retorna true para email institucional", () => {
      expect(isValidEmail("jose.martinez@universidad.edu.co")).toBe(true);
    });
  });

  describe("casos limite", () => {
    it("retorna true ignorando espacios al inicio y final", () => {
      expect(isValidEmail("  user@example.com  ")).toBe(true);
    });

    it("retorna false para email sin dominio después del @", () => {
      expect(isValidEmail("user@")).toBe(false);
    });

    it("retorna false para email sin TLD (sin punto en dominio)", () => {
      expect(isValidEmail("user@example")).toBe(false);
    });
  });

  describe("caso erroneo", () => {
    it("retorna false para string vacío", () => {
      expect(isValidEmail("")).toBe(false);
    });

    it("retorna false para email sin @", () => {
      expect(isValidEmail("userexample.com")).toBe(false);
    });

    it("retorna false para email con espacio interno", () => {
      expect(isValidEmail("user @example.com")).toBe(false);
    });
  });
});

// ---------------------------------------------------------------------------
// PU-02: matchesPasswordStandard
// ---------------------------------------------------------------------------

describe("matchesPasswordStandard", () => {
  describe("casos normales", () => {
    it("retorna true para contraseña que cumple todos los requisitos", () => {
      expect(matchesPasswordStandard("Secure1!")).toBe(true);
    });

    it("retorna true para contraseña con múltiples especiales", () => {
      expect(matchesPasswordStandard("P@$$w0rd!")).toBe(true);
    });

    it("retorna true para contraseña exactamente de 8 caracteres", () => {
      expect(matchesPasswordStandard("Abcde1!x")).toBe(true);
    });
  });

  describe("casos limite", () => {
    it("retorna true ignorando espacios al inicio y final", () => {
      expect(matchesPasswordStandard("  Secure1!  ")).toBe(true);
    });

    it("retorna false para contraseña de 7 caracteres (un menos del mínimo)", () => {
      expect(matchesPasswordStandard("Abc1!xy")).toBe(false);
    });

    it("retorna false si falta solo el carácter especial", () => {
      expect(matchesPasswordStandard("Secure123")).toBe(false);
    });
  });

  describe("caso erroneo", () => {
    it("retorna false para string vacío", () => {
      expect(matchesPasswordStandard("")).toBe(false);
    });

    it("retorna false para contraseña solo minúsculas", () => {
      expect(matchesPasswordStandard("password1!")).toBe(false);
    });

    it("retorna false para contraseña solo mayúsculas", () => {
      expect(matchesPasswordStandard("PASSWORD1!")).toBe(false);
    });

    it("retorna false para contraseña sin dígito", () => {
      expect(matchesPasswordStandard("SecurePass!")).toBe(false);
    });
  });
});
