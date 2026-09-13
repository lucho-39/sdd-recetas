# Changelog

Todos los cambios relevantes del proyecto Recetario IA.

El formato sigue, de manera simplificada, [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).
El proyecto está en fase **MVP (0.x)**.

## [Unreleased]

### Added — Autenticación y cuenta
- Registro/login/logout/refresh con **JWT HS256** (access 15 min) + refresh JWT con `jti` en cookie HttpOnly.
- Páginas `/login`, `/register`, `/forgot-password`, `/verify-email`.
- **Verificación de email**: token de 24 h (`POST /auth/verify-email`), `POST /auth/request-verification`
  (público, por email) y reenvío desde el login. En el MVP el registro auto-verifica
  (`require_email_verification=false`); el envío real de email depende de SMTP.
- Perfil privado (`/perfil`) y **perfil público** (`/usuario/:id`) sin datos sensibles.

### Added — Recetas
- CRUD completo: crear/editar/borrar (soft delete) y **restaurar**; detalle por slug con
  contador de visitas; generación de slug con desambiguación.
- **Ingredientes**: catálogo con autocomplete, nombres resueltos en el detalle, cantidad/unidad/notas.
- **Tags**: asociación por slug al crear/editar, con `usage_count` sincronizado.
- **Favoritos y colecciones**: guardar/quitar, mover, renombrar y borrar colecciones.
- **Calificaciones y reseñas**: 1–5 estrellas, reseña textual, promedio y **distribución**,
  "mi calificación" y eliminación de la propia.
- **Subida de imágenes** a disco local (`POST /api/v1/uploads`, servidas en `/uploads`), o URL externa.
- **`/buscar`**: filtros de texto, categoría, tags, ingredientes, dificultad y tiempo; orden,
  deep links por URL e infinite scroll.
- **`/mis-recetas`**: tabs Publicadas/Privadas/Borradas, toggle de visibilidad, editar y restaurar.
- **Modo Cocinando** (`/cooking/:slug`): wake lock, swipe, teclado, voz, timer por paso y fullscreen.

### Added — Notificaciones en tiempo real
- **Socket.IO** (`python-socketio` + `socket.io-client`): al guardar o calificar una receta, el autor
  recibe la notificación al instante.
- **Campanita** en el navbar con badge de no leídas, dropdown, marcar leída + navegar a la receta,
  borrar una o todas.
- **Preferencias por usuario**: eventos (favoritos/calificaciones) y canales
  (in-app, email, push), incluida la opción de no recibir nada.
- **Email** vía SMTP configurable (`SMTP_HOST`, …) con `email_outbox` persistente como fallback.
- **Push**: notificación del navegador vía Service Worker (`showNotification`).
- Mensaje de calificación: `Tu receta '{título}' recibió una calificación de {n} estrellas de parte
  de '{usuario}'`.

### Added — Panel de administración
- API `/api/admin` con guard de rol `admin` y UI SvelteKit (shell colapsable, header con usuario/logout).
- **Dashboard** con KPIs y charts de recetas por mes/semana.
- **Métricas** (`/metricas`): crecimiento de usuarios, recetas por categoría, distribución de
  calificaciones y recetas más visitadas.
- **Usuarios**, **Recetas**, **Ingredientes** (validar/rechazar/normalizar), **Categorías** y **Tags**.
- **Configuración** (`/config`): flags `registration_open`, `require_email_verification`,
  `max_upload_size_mb`.
- **Audit log** (`/audit-log`): registro de acciones administrativas.

### Added — PWA
- Manifest, ícono, service worker (con fallback offline), botón de instalación y `orientation.lock`
  en el Modo Cocinando.

### Added — API (endpoints destacados)
- `GET/PUT /api/v1/users/me/notification-preferences`.
- `GET /api/v1/notifications`, `/unread-count`, `POST /{id}/read`, `/read-all`, `DELETE /{id}`, `DELETE`.
- `POST /api/v1/recipes/{slug}/restore`; filtros `difficulty` y `max_time` en el listado.
- `GET /api/v1/ratings/{id}/mine`; `DELETE /api/v1/ratings/{id}`.
- `POST /api/v1/uploads`; lectura pública de `tags`, `ingredients` y `categories`.

### Added — Datos y seed
- Seed idempotente de 10 categorías y recetas demo; bootstrap del usuario admin.

### Infraestructura
- `podman-compose` con **postgres + backend + frontend + admin**, healthchecks y bind mounts persistentes
  (`./.data/postgres`, `./.data/uploads`).
- Backend servido como `app.main:socket_app` (HTTP + Socket.IO en el mismo puerto).
- Frontends en modo **build + preview** (sin HMR en contenedor).

### CI
- `.github/workflows/ci.yml`: job de backend (Postgres + `uv sync` + `pytest`, incluida la suite) y
  job de build del frontend.
- **Test de integración de Socket.IO** (`tests/test_realtime_socket.py`): levanta un servidor ASGI real
  y valida autenticación, unión al room y entrega del evento.

### Fixed
- 10 bugs reales de endpoints detectados al escribir la suite de tests.
- Build del frontend por markup inválido en `CategoryFilter`/`TagAutocomplete`.
- Autocompletes apuntaban a endpoints inexistentes; `recipesStore` armaba mal los arrays de filtros.
- `MissingGreenlet` al sincronizar tags de una receta nueva; `{else}` inválido en Svelte.
- 404 de `/register` y de las rutas del menú (`/mis-recetas`, `/mis-favoritos`).

### Docs
- `docs/decisions/ADR-000-source-of-truth.md` (la documentación como fuente de verdad).
- Requisitos (RF/RB), visión, dominio, UI (páginas, componentes, design system),
  casos de uso (`search`, `ingredients`, `admin`, `notifications`), testing y este CHANGELOG.

### Tests
- Suite de endpoints con Postgres real (`recetario_test`) y `ASGITransport`: **146 tests** verdes,
  incluidos notificaciones (preferencias/email) e integración de Socket.IO.
