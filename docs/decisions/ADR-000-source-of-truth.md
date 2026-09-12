# ADR-000: Fuente de verdad y reconciliación documentación ↔ implementación

## Estado

Aceptado — 2026-09-12

## Contexto

Al auditar `docs/` contra el código aparecieron incongruencias entre lo
documentado y lo implementado (categorías 8 vs 10, RS256 vs HS256, refresh
opaque vs JWT, `ADMIN_INITIAL_EMAIL` vs `ADMIN_INITIAL_USER`, slug nanoid vs
numérico, trigram vs ILIKE, triggers vs cálculo en app, tablas en español vs
inglés), además de contradicciones internas entre documentos y un
`data-model.md` con SQL no ejecutable.

El proyecto declaraba SDD (spec antes que código) pero se implementó un MVP
completo sin delta specs ni ADRs. Para seguir avanzando sin arrastrar deuda
documental, se necesita una única fuente de verdad.

## Decisión

**El código implementado y probado es la fuente de verdad.** La documentación
se reconcilia para describir el sistema real. Todo lo que está documentado como
MVP pero no está implementado se reclasifica explícitamente como **v2 / post-MVP**.

Resoluciones canónicas:

| # | Tema | Decisión |
|---|------|----------|
| 1 | Categorías de receta | **10** slugs: `postre, entrada, snack, plato-principal, acompañamiento, bebida, desayuno, sopa-crema, ensalada, horneados`. Sin `otro`. |
| 2 | Algoritmo JWT | **HS256** con secreto simétrico (`JWT_SECRET`) en desarrollo/MVP. RS256 con par de claves queda como mejora v2. |
| 3 | Refresh token | **JWT firmado** (HS256) con `jti`, en cookie HttpOnly, rotación por reuso y blacklist en memoria. Refresh opaque queda v2. |
| 4 | Bootstrap admin | Variables **`ADMIN_INITIAL_USER` / `ADMIN_INITIAL_PASSWORD`**; campo `must_change_password` (no `force_password_change`). |
| 5 | Nombres físicos | Tablas/columnas en **inglés** (`users`, `recipes`, `categories`, `ingredients`, `tags`, `recipe_tags`, `favorites`, `visits`, `ratings`). Los docs de dominio pueden usar términos en español pero deben referenciar el nombre físico. |
| 6 | Slug de receta | **`slugify(title)` + desambiguación numérica** (`-2`, `-3`). `nanoid` descartado. |
| 7 | Búsqueda | **ILIKE** para texto e ingredientes + JSONB `contains` por `ingredient_id`. `pg_trgm` / `jsonb_path_query` quedan v2. |
| 8 | Panel admin | **Existe** como proyecto SvelteKit separado con auth propia. Los endpoints `/api/admin/*` están **pendientes**. |
| 9 | Contadores denormalizados | `visit_count` y `avg_rating`/`rating_count` se actualizan en la capa de aplicación. `save_count` **no se actualiza aún** (pendiente). No hay triggers de BD. |
| 10 | Ingredientes en receta | JSONB con `{ingredient_id, amount, unit, notes}`; `ingredient_id` referencia al catálogo. |
| 11 | Seed de ingredientes | Objetivo 300; el seed documentado está incompleto (257 filas, con slugs duplicados). Debe completarse. |

## Reclasificado a v2 / post-MVP

OAuth Google/GitHub · Generación de recetas por IA · Modo "Cocinando" · PWA
offline · Rate limiting · Verificación de email y reset de contraseña reales ·
Triggers de BD · Búsqueda trigram · Redis · Read replicas · CDN ·
Observabilidad (Prometheus/OpenTelemetry) · Deactivate/Reactivate/Delete-account.

## Alternativas

- **La documentación manda** (cambiar el código): descartada por costo/riesgo;
  el backend ya está probado (81 tests) y el costo de migrar a RS256, refresh
  opaque, triggers, trigram y naming en español es alto y sin valor inmediato.
- **No reconciliar**: descartada; perpetúa contradicciones que ya causaron bugs
  (p. ej. `JWT_ALGORITHM=RS256` con secreto simétrico).

## Consecuencias

**Positivas**
- Una sola fuente de verdad; se elimina la ambigüedad que ya generó defectos.
- El alcance real del MVP queda explícito; el backlog v2 queda identificado.

**Negativas / deuda aceptada**
- `docs/specs/`, `docs/architecture/` y ADRs llegarán tarde (se generan después
  del código). Se acepta como deuda documental a saldar.
- `data-model.md` requiere reescritura para reflejar el esquema físico real.
