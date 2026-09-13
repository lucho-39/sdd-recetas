# Caso de Uso: Autenticación y Cuenta

**ID**: UC-AUTH-001
**Actor principal**: Usuario (anónimo o autenticado)
**Objetivo**: Registrarse, iniciar/cerrar sesión, refrescar tokens, verificar email y gestionar la cuenta

---

## Flujo Principal — Registro y login

1. `/register`: email + nombre + contraseña → `POST /api/v1/auth/register`.
2. Si `registration_open` está desactivado → 403.
   Si `require_email_verification` está activo, la cuenta nace sin verificar.
3. `/login`: email + password → `POST /api/v1/auth/login` (form-urlencoded).
4. El backend devuelve un **access token** (JWT HS256, 15 min) y setea el
   **refresh token** en cookie HttpOnly (30 días).
5. Login de cuenta no verificada → 403 (se ofrece reenviar verificación).

## Refresh / logout

- `POST /api/v1/auth/refresh` (cookie) → nuevo par access/refresh (rotación; el
  anterior se agrega a la blacklist en memoria).
- `POST /api/v1/auth/logout` → blacklist del refresh + borra la cookie.

## Verificación de email

- `POST /api/v1/auth/request-verification` (público, por email) → genera un token
  de 24 h. Sin proveedor SMTP, en desarrollo se devuelve el enlace.
- `POST /api/v1/auth/verify-email` `{token}` → marca `is_verified`.
- Página `/verify-email`; reenvío desde el login ante "Email not verified".

## Cuenta

- `GET /api/v1/auth/me`, `PATCH /api/v1/auth/me` (perfil), `PATCH /api/v1/users/me`.
- `POST /api/v1/auth/change-password`.
- Preferencias de notificación: `/api/v1/users/me/notification-preferences`.

## Reglas de Negocio

| Regla | Aplicación |
|-------|------------|
| RB-AUTH-06 | El login rechaza cuentas no verificadas |
| — | Access 15 min + refresh 30 días con rotación |
| — | El registro auto-verifica salvo que se configure lo contrario |

## Criterios de Aceptación

| ID | Criterio |
|----|----------|
| AC-01 | Registro + login devuelven un access token usable |
| AC-02 | Refresh renueva el access token |
| AC-03 | Cuenta no verificada no puede loguearse (403) |
| AC-04 | Token de verificación marca `is_verified` y permite el login |

## Estado de Implementación

- ✅ Registro/login/refresh/logout, verificación de email (envío real de email vía
  SMTP configurable) y gestión de cuenta.
- 🔲 OAuth Google/GitHub; reset de contraseña real; reuso de refresh por familia.
