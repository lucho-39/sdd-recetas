# ADR-001: Stack tecnológico

## Estado

Aceptado — 2026-10-12. Registra la decisión tomada el 2026-09-05 (Q3).

## Contexto

MVP mobile-first PWA con tres superficies (frontend público, admin, API) para un equipo chico, deploy en VPS con Podman y sin apps nativas.

## Decisión

- **Frontend y admin**: SvelteKit 2 + Vite 5 + TypeScript, dos apps separadas en el mismo repo (`frontend/`, `admin/`). PWA instalable con service worker.
- **Backend**: FastAPI ≥0.115, Python ≥3.12, Pydantic v2, REST con OpenAPI autogenerado.
- **Base de datos**: PostgreSQL 16 (imagen `public.ecr.aws/docker/library/postgres:16-alpine`).
- **Auth**: JWT HS256 + refresh en cookie HttpOnly (ver ADR-003).
- **Contenedores**: Podman + Compose en VPS. Nada de Docker Hub.

## Alternativas

- **Next.js + NestJS**: descartado; RSC complica el offline y el overhead no se justifica para el alcance.
- **Remix + Go**: descartado; curva de Go sin beneficio para un CRUD con realtime liviano.

## Consecuencias

**Positivas**
- Un solo lenguaje en frontend, bundle chico, PWA nativo de Vite.
- Un repo, un compose, un CI: costo operativo mínimo.

**Negativas / deuda aceptada**
- `frontend/` y `admin/` duplican `lib/api.ts`, tipos y utils: no hay `packages/` compartido. Compartir tipos generados desde OpenAPI queda v2.
- Ecosistema/hiring menor que React.
