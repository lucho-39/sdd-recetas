/**
 * Espejo de `backend/app/core/units.py`.
 *
 * El admin las necesita para los selectores de UC-ADMIN-019 AC2 sin una
 * llamada extra al backend, pero la autoridad sigue siendo la del backend:
 * `normalize` devuelve 400 si el valor no está en su lista, así que una
 * desincronización se ve al guardar, nunca se esconde.
 */
export const VALID_UNITS = [
  "g",
  "kg",
  "ml",
  "l",
  "unidad",
  "cucharada",
  "cucharadita",
  "taza",
  "pizca",
] as const;

export const VALID_CATEGORIES = [
  "proteina",
  "verdura",
  "fruta",
  "lacteo",
  "grano",
  "condimento",
  "grasa",
  "otro",
] as const;

/** Razones predefinidas de UC-ADMIN-016 AC1; "Otro" habilita el texto libre. */
export const REJECTION_REASONS = [
  "Inapropiado",
  "Duplicado",
  "Spam",
  "Otro",
] as const;
