# 04-decisions.md — Índice de ADRs

| ADR | Decisión | Estado |
|---|---|---|
| [ADR-000](../decisions/ADR-000-source-of-truth.md) | El código implementado y probado es la fuente de verdad | Aceptado 2026-09-12 |
| [ADR-001](../decisions/ADR-001-tech-stack.md) | SvelteKit 2 + FastAPI + PG16 + Podman en VPS | Aceptado 2026-10-12 |
| [ADR-002](../decisions/ADR-002-database.md) | PostgreSQL 16, SQLAlchemy async, Alembic; sin triggers | Aceptado 2026-10-12 |
| [ADR-003](../decisions/ADR-003-auth.md) | JWT HS256 + refresh rotado con detección de reuso; rol en DB | Aceptado 2026-10-12 |
| [ADR-004](../decisions/ADR-004-search.md) | ILIKE + JSONB contains; trigram v2 | Aceptado 2026-10-12 |
| [ADR-005](../decisions/ADR-005-deployment.md) | Monorepo + compose de 4 servicios, deploy manual | Aceptado 2026-10-12 |
| [ADR-006](../decisions/ADR-006-orm.md) | SQLAlchemy 2.0 asyncio + seeds en código | Aceptado 2026-10-12 |

Reglas: un ADR se escribe al tomar la decisión; son inmutables (el cambio
va en un ADR nuevo). Ver `decisions/README.md`.
