# 02-security.md — Modelo de seguridad

## Autenticación

- **JWT HS256** simétrico (`JWT_SECRET`); access 15 min, refresh 30 días en
  cookie HttpOnly `Secure` (en prod) + `SameSite=Lax`, con rotación y
  **detección de reuso por familia**.
- Passwords con **bcrypt** (truncadas a su límite de 72 bytes); política
  enforced: mínimo 8 caracteres (complejidad queda v2, ver RB-AUTH-03).
- Verificación de email antes del login (OAuth = verificado automático);
  reset con token de un solo uso; OAuth Google/GitHub solo si hay credenciales.
- Bootstrap admin por `ADMIN_INITIAL_*` + cambio forzado en primer login.
- ⚠️ **Riesgo conocido y aceptado**: el access token vive en `localStorage`
  (ambos frontends). Un XSS lo expondría; mitiga su vida corta (15 min) y la
  rotación del refresh. Moverlo a memoria queda v2.

## Autorización

- Admin por **rol en DB**, leído en cada request (`require_admin`): cambiar
  el rol es efectivo de inmediato, sin tokens separados.
- Recurso ajeno = 404 (no 403): no se revela existencia.
- Desactivar corta sesiones vivas (revoca refresh); GDPR anonimiza + desactiva.

## Transporte y borde

- TLS terminado en Caddy (Let's Encrypt); sin TLS no hay `Secure` ni
  SameSite que valga: **nunca exponer el compose sin el proxy**.
- CORS restringido a orígenes configurados (con validator que splitea por
  coma) + credenciales; en el diseño actual casi todo es same-origin.
- Rate limit por IP vista tras `X-Forwarded-For` (lo pone Caddy): válido
  **solo** con los puertos internos cerrados (ufw 22/80/443). Exento
  `/api/admin`; configurable y apagable desde `/config`.

## Secretos y operación

- Todo secreto vive en `.env` (jamás en git): `JWT_SECRET`, `POSTGRES_*`,
  `ADMIN_INITIAL_PASSWORD`, SMTP, VAPID. Rotar `JWT_SECRET` invalida todas
  las sesiones: es el botón de pánico.
- Blacklist de tokens **en memoria por proceso**: con un worker alcanza;
  con más réplicas habría que externalizarla (v2, con el resto de la
  observabilidad).
- Mantenimiento: 503 en tráfico público excepto `/health`, `/api/admin` y
  auth; audit log registra quién tocó qué (`user.*`, `config.update`…).

## Queda v2

RS256/refresh opaque · complejidad de password · headers CSP/HSTS ·
observabilidad (Prometheus/OpenTelemetry) · auto-reactivación por magic link.
