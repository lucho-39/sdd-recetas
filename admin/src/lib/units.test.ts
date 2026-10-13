import { describe, expect, it } from "vitest";
import { REJECTION_REASONS, VALID_CATEGORIES, VALID_UNITS } from "./units";

describe("listas del catálogo (espejo de backend/app/core/units.py)", () => {
  it("unidades con la whitelist de UC-ADMIN-019 AC2", () => {
    expect([...VALID_UNITS]).toEqual([
      "g",
      "kg",
      "ml",
      "l",
      "unidad",
      "cucharada",
      "cucharadita",
      "taza",
      "pizca",
    ]);
  });

  it("sin duplicados", () => {
    expect(new Set(VALID_UNITS).size).toBe(VALID_UNITS.length);
    expect(new Set(VALID_CATEGORIES).size).toBe(VALID_CATEGORIES.length);
  });

  it("razones de rechazo de UC-ADMIN-016 AC1", () => {
    expect([...REJECTION_REASONS]).toEqual([
      "Inapropiado",
      "Duplicado",
      "Spam",
      "Otro",
    ]);
  });
});
