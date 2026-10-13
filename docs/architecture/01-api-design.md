# 01-api-design.md — Contrato de la API

## Prefijos y versionado

- Pública: `/api/v1/*`. Admin: `/api/admin/*` (requiere rol `admin` en DB).
- Versionado por prefijo URL (`v1`); el admin no se versiona (viaja con el deploy).
- OpenAPI autogenerado por FastAPI; `/docs` y `/redoc` **apagados en producción**.
- Realtime fuera de REST: Socket.IO en `/socket.io/` (misma app, mismo puerto).

## Autenticación en las llamadas

- `Authorization: Bearer <access>` (15 min) en endpoints protegidos.
- Refresh: `POST /api/v1/auth/refresh` con cookie HttpOnly (path
  `/api/v1/auth/refresh`), rota en cada uso; reuso → 403 y familia revocada.
- Sin token en realtime no hay conexión (el socket se rechaza).

## Paginación y orden

- Listados: `?page=1&limit=20` (límite 100) → `{items, total, page, limit}`.
- Orden con claves fijas y dirección fija (no hay parámetro de dirección;
  un click cambia la clave). Ver UC-005 AC4.
- Búsqueda combina filtros en AND; texto por ILIKE (ver ADR-004).

## Errores

- Cuerpo `{detail: "..."}`; códigos: 400 (validación/estado inválido), 401
  (sin token o inválido), 403 (sin rol, cuenta no verificada/desactivada,
  reuso de refresh), 404 (inexistente **o ajeno**: editar receta ajena da
  404, no 403, para no revelar existencia), 429 (rate limit), 503
  (mantenimiento, salvo `/health`, `/api/admin` y `/api/v1/auth`).
- Los 5xx se registran en el error log con endpoint, path y request id.

## Idempotencia y efectos

- `DELETE` de receta admin es idempotente: si ya estaba borrada, devuelve el
  estado sin cambios (`recipe.delete`).
- `PUT /api/admin/config` acepta claves desconocidas y las ignora; solo
  persiste claves de `DEFAULTS`.
- Uploads: `POST /api/v1/uploads` (límite `max_upload_size_mb`), servidos en
  `/uploads` como archivos estáticos.
