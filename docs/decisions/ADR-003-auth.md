# ADR-003: Autenticación y autorización

## Estado

Aceptado — 2026-10-12. Registra decisiones tomadas entre 2026-09-05 y 2026-10-12 (Q3, Q20, Epic A2).

## Contexto

Dos superficies con sesiones largas estilo red social (access corto + refresh largo), login social opcional y un admin con auth separada del frontend.

## Decisión

- **JWT HS256** con secreto simétrico (`JWT_SECRET`); access 15 min + refresh 30 días en cookie HttpOnly, con **rotación y detección de reuso por familia** (reuso → revoca la familia).
- Verificación de email requerida antes del login (OAuth = verificado automático); reset real con token de un solo uso; OAuth Google/GitHub config-gated.
- **Admin**: app SvelteKit separada, mismo backend. Autorización por **rol en DB** (`require_admin` lo lee en cada request: el cambio de rol es inmediato, sin tokens admin separados). Bootstrap por `ADMIN_INITIAL_USER` / `ADMIN_INITIAL_PASSWORD` + `must_change_password`.
- Baja lógica (`is_active`), reactivación solo-admin, GDPR con anonimización (ver UC-009/010/011).

## Alternativas

- **RS256 + refresh opaque**: descartado para el MVP por costo operativo (par de claves, store de tokens); queda v2 (ADR-000 §2-3).
- **Auth delegada (Clerk/Auth.js/Lucia)**: descartada; dependencia externa y costo para un modelo de sesiones que el backend ya resuelve.

## Consecuencias

**Positivas**
- Sin infraestructura extra (sin Redis: blacklist en memoria, apiarios en JWT).
- El rol en DB elimina toda una clase de bugs de sincronización entre "proyectos".

**Negativas / deuda aceptada**
- Revocar un access token antes de su expiración no es posible salvo desactivando la cuenta.
- Auto-reactivación por magic link queda v2.
