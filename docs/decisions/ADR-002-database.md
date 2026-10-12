# ADR-002: Base de datos y acceso a datos

## Estado

Aceptado — 2026-10-12. Registra la decisión tomada el 2026-09-05 (Q7, opción A).

## Contexto

Se necesitaba ORM async para FastAPI con migraciones versionadas y type hints, sin acoplar la lógica a SQL crudo.

## Decisión

- **PostgreSQL 16** como único datastore (relacional + JSONB).
- **SQLAlchemy 2.0 asyncio** para modelos y queries; **Alembic** para migraciones (4 a la fecha: baseline, notificaciones nullable, `merged_into`, `allowed_units`).
- Ingredientes por receta en **JSONB** (`{ingredient_id, amount, unit, notes}`); contadores denormalizados actualizados en la capa de aplicación, sin triggers (ADR-000 §9).
- Las extensiones `pg_trgm` / `pgcrypto` / `btree_gin` figuran en `data-model.md` pero **ninguna migración las crea**: la búsqueda usa ILIKE (ver ADR-004). Habilitarlas es v2.

## Alternativas

- **SQLModel**: descartado; integra bien con FastAPI pero es más joven y menos flexible que SQLAlchemy puro para queries complejas.
- **Raw SQL + asyncpg + migraciones manuales**: descartado; control total a cambio de perder modelos tipados y DX.
- **Prisma/Drizzle**: descartado; no son Python-native.

## Consecuencias

**Positivas**
- Modelos tipados, migraciones reproducibles, async de punta a punta.

**Negativas / deuda aceptada**
- `data-model.md` describe SQL no ejecutable (extensiones, funciones, triggers): requiere reescritura al esquema físico real.
- El conteo de uso de ingredientes es calculado en lectura por el JSONB sin tabla de unión (decisión documentada en UC-012).
