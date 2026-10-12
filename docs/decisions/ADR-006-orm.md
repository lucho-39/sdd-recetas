# ADR-006: ORM

## Estado

Aceptado — 2026-10-12. Registra la decisión tomada (Q7, opción A); separada de ADR-002 porque el acceso a datos tiene alternativas propias.

## Contexto

Ver ADR-002. Esta decisión cubre solo la capa de acceso: modelos, sesiones y migraciones en código.

## Decisión

- Modelos con `Mapped`/`mapped_column`, sesiones `AsyncSession` con `expire_on_commit=False`, engine único con `pool_pre_ping` y `pool_recycle`.
- Migraciones Alembic versionadas junto al backend; datos de catálogo (317 ingredientes, categorías) como seeds idempotentes en código, no en SQL.
- Sin triggers ni funciones de negocio en la BD: la BD guarda, la app decide.

## Alternativas

- Ver Q7 en `02-open-questions.md` (SQLModel, raw SQL, Prisma/Drizzle): mismos descartes que ADR-002.

## Consecuencias

**Positivas**
- Todo el esquema nace del código: un `alembic upgrade head` reproduce la BD.

**Negativas / deuda aceptada**
- `datetime.utcnow()` en 30 llamadas (rule diferida en `pyproject.toml`): migrar a aware cambia comparaciones y va como cambio propio.
- Sin `ruff format` en CI: el estilo lo sostiene el linter, no el formateador.
