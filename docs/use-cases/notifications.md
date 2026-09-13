# Caso de Uso: Notificaciones en Tiempo Real

**ID**: UC-NOTIF-001
**Actor principal**: Autor de una receta (usuario logueado)
**Precondición**: El autor tiene al menos una receta pública y otro usuario interactúa con ella
**Objetivo**: Enterarse en el momento en que alguien guarda o califica su receta

---

## Flujo Principal

```mermaid
flowchart TD
    A[Usuario B guarda/califica una receta de A] --> B[Backend crea/refresca Notification de A]
    B --> C[Emite 'notification' al room user:A vía Socket.IO]
    C --> D[Socket de A recibe el evento]
    D --> E[Campanita incrementa el badge]
    E --> F[A abre el dropdown y ve la notificación]
    F --> G[Click -> marca leída + navega a /receta/slug]
```

---

## Pasos Detallados

1. **Reconexión / auth**: al iniciar sesión, el cliente abre un socket con
   `auth.token` (JWT de acceso). El servidor valida el token, guarda la sesión
   y une el socket al room `user:<id>`. Un socket sin token válido se rechaza.
2. **Disparo**: al `POST /favorites/{recipe_id}` o `POST /ratings/{recipe_id}`,
   el backend crea o refresca una `Notification` para el autor y, tras el
   commit, emite `notification` al room del autor. Nunca se auto-notifica.
3. **Badge**: el cliente incrementa el contador de no leídas y lo muestra en la
   campanita (`IconBellFilled`).
4. **Dropdown**: muestra las últimas 20 con actor, tipo, receta y tiempo relativo.
5. **Lectura**: click en una notificación → `POST /notifications/{id}/read` +
   navegación a `/receta/<slug>`.
6. **Borrado**: `DELETE /notifications/{id}` (individual) o
   `DELETE /notifications` (todas). "Marcar leídas" usa `POST /notifications/read-all`.

---

## Reglas de Negocio Aplicadas

| Regla | Aplicación |
|-------|------------|
| — | **Sin auto-notificación**: el actor nunca es el destinatario |
| — | **Dedupe**: (destinatario, actor, receta, tipo) es único; repetir refresca |
| RB-05 | Favorito (`type="favorite"`) |
| RB-06 | Calificación (`type="rating"`, con `detail.score`) |

---

## Mensajes

Plantillas (mismo texto en la campanita y en el email):

| Evento | Mensaje |
|--------|---------|
| Favorito | `'{actor}' guardó tu receta '{título}'` |
| Calificación | `Tu receta '{título}' recibió una calificación de {score} estrella(s) de parte de '{actor}'` |

- `{score}` en singular/plural (`1 estrella` / `4 estrellas`).
- Si no hay puntaje: `Tu receta '{título}' recibió una calificación de parte de '{actor}'`.
- `{actor}` usa `display_name`; `{título}` el título de la receta.
- En la campanita, el título de la receta también aparece como línea secundaria.

## Contrato técnico

### Modelo `Notification`
`id`, `user_id` (destinatario = autor), `actor_id`, `type` (`favorite`|`rating`),
`recipe_id`, `detail` (JSONB), `is_read`, `created_at`.
Unique: `(user_id, actor_id, recipe_id, type)`.

### REST (`/api/v1/notifications`, auth)
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/notifications` | Lista paginada + `unread_count` |
| GET | `/notifications/unread-count` | Solo el contador |
| POST | `/notifications/{id}/read` | Marcar una como leída |
| POST | `/notifications/read-all` | Marcar todas como leídas |
| DELETE | `/notifications/{id}` | Borrar una |
| DELETE | `/notifications` | Borrar todas |

### Preferencias (`/api/v1/users/me/notification-preferences`, auth)
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/users/me/notification-preferences` | Preferencias actuales (defaults si no hay fila) |
| PUT | `/users/me/notification-preferences` | Actualización parcial |

Campos: `in_app_enabled`, `email_enabled`, `push_enabled` (canales) y
`favorites_enabled`, `ratings_enabled` (eventos). Defaults: in-app ON, email/push
OFF, ambos eventos ON. Un evento desactivado no genera ninguna notificación.

- **In-app**: crea `Notification` (dedupe) y emite por Socket.IO.
- **Email**: `SMTP_HOST` configurado → envío SMTP; sin SMTP → fila `queued` en
  `email_outbox` (transporte de desarrollo persistente).
- **Push**: **Web Push con VAPID** (funciona con la app cerrada). El navegador
  se suscribe desde el Service Worker (`pushManager.subscribe` con la clave
  pública VAPID) y el backend envía el mensaje. Si no hay suscripción activa, el
  cliente cae a una notificación del navegador vía Socket.IO mientras la pestaña
  está abierta.

### Configuración (env)
`SMTP_HOST`, `SMTP_PORT` (587), `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`,
`SMTP_USE_TLS` (true). Sin `SMTP_HOST`, los emails se encolan en `email_outbox`.

### Web Push (VAPID)
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/v1/push/public-key` | Clave pública VAPID (para `applicationServerKey`) |
| POST | `/api/v1/push/subscribe` | Registrar la suscripción del navegador |
| DELETE | `/api/v1/push/subscribe` | Quitar la suscripción (por `endpoint`) |
| POST | `/api/v1/push/test` | Enviar un push de prueba al usuario |

Las claves VAPID se toman de `VAPID_PUBLIC_KEY`/`VAPID_PRIVATE_KEY` (env); si
están vacías se **generan y persisten en `app_settings`** (la privada nunca se
expone). El backend firma con `pywebpush`; las suscripciones caducas (404/410) se
eliminan. El Service Worker maneja `push` y `notificationclick`.

### Tiempo real
- Servidor: `app/realtime/server.py` (`socketio.AsyncServer`), events
  `connect` (auth + join room) y `disconnect`; helper `emit_notification`.
- `app/services/notifications.py::notify_recipe_author` centraliza el alta.
- ASGI app: `app.main:socket_app` (`socketio.ASGIApp(sio, other_asgi_app=app)`).
- Frontend: `$lib/stores/notifications.ts` gestiona el estado y el socket;
  `$lib/components/ui/NotificationBell.svelte` es la UI del navbar.
- Proxy: vite reenvía `/socket.io` (con `ws: true`) al backend.

---

## Estado de Implementación

- ✅ Eventos de favorito y calificación → notificación en tiempo real.
- ✅ Campanita con badge, dropdown, marcar leída + navegar, borrar una/todas.
- ✅ Rechazo de sockets sin token; isolation por room `user:<id>`.
- ✅ Preferencias por usuario (eventos + canales) desde `/perfil`.
- ✅ Canal email (SMTP configurable, `email_outbox` como fallback persistente).
- ✅ Canal push = **Web Push (VAPID)** con Service Worker; fallback a notificación
  del navegador vía Socket.IO si no hay suscripción.
- ✅ CI (`.github/workflows/ci.yml`) corre la suite completa, incluyendo
  `tests/test_realtime_socket.py` (servidor ASGI real, sin DB).
- 🔲 Notificaciones por respuestas/comentarios (no aplica: sin comentarios en el MVP).
