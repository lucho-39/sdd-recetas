# 00-architecture.md — Mapa del sistema (C4 nivel 1-2)

## Nivel 1: contexto

```
                ┌─────────────────────────────────────────┐
                │            Recetario IA (sdd-recetas)   │
                │                                         │
visitante ─────▶│  web pública + panel admin + API + DB   │─────▶ SMTP (opcional)
(anon/auth/     │                                         │──▶ Google/GitHub OAuth
 admin)         │                                         │──▶ Push API del navegador
                └─────────────────────────────────────────┘
                              ▲
                    Caddy + Let's Encrypt (TLS)
                    DuckDNS: app.* / admin.*
```

Actores: visitante anónimo (lee y busca), usuario autenticado (crea,
guarda, califica), admin (modera y opera). Externos opcionales: SMTP (sin
él los correos caen en `email_outbox`), OAuth y la Push API del navegador.

## Nivel 2: contenedores

| Contenedor | Puerto | Rol |
|---|---|---|
| `caddy` (host, prod) | 80/443 | TLS + reparte por host |
| `frontend` (preview) | 3000 | SPA pública; proxea `/api`, `/uploads`, `/socket.io` al backend |
| `admin` (preview) | 3001 | SPA admin; proxea `/api` al backend |
| `backend` (uvicorn `socket_app`) | 8000 | REST `/api/v1/*` + `/api/admin/*`, Socket.IO, `/uploads`, `/health` |
| `postgres` | 5432 | PostgreSQL 16, volumen persistente |

Red `recetario-network`; healthchecks encadenados (postgres → backend →
frontends). Clave del diseño: **el browser nunca habla con el backend por
otro host**. Todo sale del mismo origen, así que no hay CORS cross-site y
las cookies viajan same-origin (ver `01-api-design.md` y ADR-005).

## Dónde vive cada responsabilidad

- **Auth y sesiones**: backend (`security.py`, `auth.py`); el frontend guarda
  el access token, el refresh vive en cookie HttpOnly.
- **Realtime**: Socket.IO en el mismo puerto (`socket_app` envuelve la app);
  rooms `user:<id>`, sin token no hay conexión.
- **Archivos**: disco local (`/uploads` servido por el backend, volumen
  `./.data/uploads`).
- **Config operativa**: tabla `app_settings` + caché en caliente (flags,
  rate limit, mantenimiento, 3 plantillas de email).
- **Observabilidad mínima**: audit log, error log 5xx y middleware de rate
  limit/mantenimiento en `main.py`. Sin Prometheus ni tracing (v2).
