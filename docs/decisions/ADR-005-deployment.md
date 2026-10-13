# ADR-005: Deployment y estructura de repos

## Estado

Aceptado — 2026-10-12. Registra Q10 + Q21 (opción A en ambas).

## Contexto

Un repo con tres superficies, un solo desarrollador, deploy en un VPS con
Podman y sin pipeline de CD: el deploy es `compose up` contra `master`.

## Decisión

- **Monorepo**: `frontend/`, `admin/`, `backend/` en `lucho-39/sdd-recetas`, un
  workflow de CI con tres jobs (backend-tests, frontend-checks, admin-checks).
- **Compose con 4 servicios**: `postgres:16-alpine` (ECR Public, volumen de
  datos, healthcheck `pg_isready`), `backend` (uvicorn `socket_app:8000`,
  espera a postgres sano), `frontend` (:3000) y `admin` (:3001), cada uno
  buildeado de su `Containerfile`, en `recetario-network`, `restart:
  unless-stopped`.
- **Admin separada pero dentro del monorepo**: contenedor y puerto propios,
  sin imports cruzados con `frontend/`. Compartir tipos vía OpenAPI queda v2.
- Configuración por entorno (`.env`): `ENVIRONMENT`, `JWT_*`, credenciales de
  bootstrap admin, SMTP, VAPID, `FRONTEND_URL`. Uploads en volumen
  (`./.data/uploads`), fuera del código.
- Documentación pública (`/docs`, `/redoc`) apagada en producción.

## Alternativas

- **Multi-repo (3 repos)**: descartado; triple CI y versionado cruzado sin
  beneficio a esta escala.
- **Admin en repo aparte**: descartado por lo mismo; el aislamiento que pide
  es de runtime (contenedor + auth por rol), no de repo.
- **Orquestador gestionado / PaaS**: descartado por costo y por Q6 (VPS).

## Consecuencias

**Positivas**
- Un push a `master`, un CI, un compose: el deploy entero cabe en la cabeza.

**Negativas / deuda aceptada**
- Sin CD: el deploy es manual. Sin réplicas ni balanceador: un solo nodo.
- Los bind mounts de `frontend/`/`admin/` en el compose son de desarrollo;
  una imagen prod autocontenida queda v2.
