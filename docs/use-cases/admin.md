# Casos de Uso: Administración (Proyecto Independiente)

**Proyecto**: `recetario-admin` (SvelteKit separado)  
**Auth**: Independiente del frontend usuario — JWT propio (HS256 en MVP; RS256 queda v2) (`role: "admin"`), cookies HttpOnly, refresh rotation propia. **Endpoints `/api/admin/*` pendientes de implementar.**
**Actores**: Administrador (usuario con `role: "admin"`)  
**API**: Consume misma API backend (`/api/admin/*` endpoints con scope `admin`)

---

## Epic A1: Gestión de Categorías

### UC-ADMIN-001: Listar categorías
**Como** admin, **quiero** ver todas las categorías **para** gestionar la taxonomía.
- **AC1**: Tabla paginada (20/pág): slug, name, icon, sort_order, is_active, recetas_count
- **AC2**: Filtros: activa/inactiva, búsqueda por nombre/slug
- **AC3**: Ordenamiento: sort_order (default), name, recetas_count
- **AC4**: Botón "Nueva categoría" + acciones por fila (editar, toggle activo, eliminar)

### UC-ADMIN-002: Crear categoría
**Como** admin, **quiero** crear una categoría **para** ampliar la taxonomía.
- **AC1**: Modal: name (requerido, único), slug (auto-generado desde name, editable), icon (emoji picker), sort_order (número)
- **AC2**: Validación: slug único, name único, icon opcional
- **AC3**: Al crear → `is_active=true`, sort_order auto (max+1)
- **AC4**: Toast éxito + tabla actualizada

### UC-ADMIN-003: Editar categoría
**Como** admin, **quiero** editar una categoría **para** corregir o reorganizar.
- **AC1**: Click fila → modal con campos prellenados
- **AC2**: Campos editables: name, slug, icon, sort_order, is_active
- **AC3**: Validación slug único (excluyendo actual)
- **AC4**: Si `is_active=false` → categoría no aparece en frontend (pero recetas existentes la mantienen)

### UC-ADMIN-004: Eliminar / Desactivar categoría
**Como** admin, **quiero** eliminar una categoría **para** limpiar taxonomía.
- **AC1**: Si categoría tiene recetas asociadas (`recetas_count > 0`) → **NO permite eliminar**, solo desactivar (`is_active=false`)
- **AC2**: Si `recetas_count = 0` → permite eliminar (DELETE) con confirmación modal
- **AC3**: Toast confirmación + tabla actualizada

---

## Epic A2: Gestión de Usuarios

### UC-ADMIN-005: Listar usuarios
**Como** admin, **quiero** ver todos los usuarios **para** supervisar la comunidad.
- **AC1**: Tabla paginada (20/pág): email, display_name, provider, is_active, role (user/admin), created_at, last_login_at, recetas_count, favoritos_count, ratings_count
- **AC2**: Filtros: estado (activo/inactivo/eliminado), proveedor (email/google/github), rol, rango fechas registro
- **AC3**: Búsqueda: email, display_name (live search con debounce 300ms)
- **AC4**: Ordenamiento: created_at (default), last_login_at, email, recetas_count
- **AC5**: Acciones por fila: ver detalle, activar/desactivar, forzar reactivación, forzar baja GDPR, cambiar rol (user↔admin)

### UC-ADMIN-006: Ver detalle de usuario
**Como** admin, **quiero** ver el detalle completo de un usuario **para** auditar su actividad.
- **AC1**: Panel: info básica (email, display_name, avatar, provider, is_active, role, created_at, last_login_at, deactivated_at)
- **AC2**: Pestañas: Recetas (propias, paginadas), Favoritos, Calificaciones dadas, Visitas recientes
- **AC3**: Métricas: total recetas, recetas públicas/privadas/borradas, total favoritos, promedio rating dado
- **AC4**: Estado de cuenta visible: Activo / Inactivo / Eliminado (GDPR) con badge de color

### UC-ADMIN-007: Activar / Desactivar usuario
**Como** admin, **quiero** activar o desactivar un usuario **para** controlar el acceso a la plataforma.
- **AC1**: Solo usuarios con `is_active=true` pueden desactivarse; `is_active=false` pueden activarse
- **AC2**: Desactivar: modal confirmación → `is_active=false`, `deactivated_at=now()`, revoca refresh tokens, usuario no puede loguear
- **AC3**: Activar: `is_active=true`, `deactivated_at=NULL`, usuario recupera acceso inmediato
- **AC4**: Toast confirmación + actualización tabla en tiempo real
- **AC5**: Log auditoría: admin_id, user_id, action="activate"/"deactivate", timestamp

### UC-ADMIN-008: Ver perfil de usuario (Resumen ejecutivo)
**Como** admin, **quiero** ver un resumen ejecutivo del usuario **para** toma de decisiones rápida.
- **AC1**: Card superior: email, display_name, avatar, proveedor, estado (badge color), rol
- **AC2**: Métricas clave: Fecha creación, Último login, Total recetas, Total favoritos, Promedio rating
- **AC3**: Estado cuenta: Activo / Inactivo / Eliminado (GDPR) con badge semántico
- **AC4**: Acciones rápidas: Activar/Desactivar, Ver detalle completo, Forzar reactivación, GDPR

### UC-ADMIN-009: Forzar reactivación de usuario
**Como** admin, **quiero** reactivar un usuario desactivado **para** restaurar su acceso (soporte).
- **AC1**: Solo usuarios con `is_active=false` y `deactivated_at` not null
- **AC2**: Modal confirmación: "Reactivar a usuario X? Se le enviará email para definir nuevo display_name"
- **AC3**: Al confirmar → `is_active=true`, `deactivated_at=NULL`, `must_change_password=false`, genera magic link reactivación → email
- **AC4**: Log de auditoría: admin_id, user_id, action="force_reactivate", timestamp

### UC-ADMIN-010: Forzar eliminación GDPR (Right to Erasure)
**Como** admin, **quiero** ejecutar eliminación GDPR inmediata **para** cumplimiento legal.
- **AC1**: Solo usuarios con `is_active=false` (ya desactivados)
- **AC2**: Modal doble confirmación: "ELIMINAR DEFINITIVAMENTE a usuario X? Esta acción es IRREVERSIBLE: PII anonimizada, recetas → system user, FKs → NULL"
- **AC3**: Ejecuta `usuario_eliminar_definitivo(user_id)` (ver `data-model.md`)
- **AC4**: Log auditoría: admin_id, user_id, action="force_gdpr_erasure", timestamp

### UC-ADMIN-011: Cambiar rol (user ↔ admin)
**Como** admin, **quiero** promover/degradar usuarios **para** gestión de permisos.
- **AC1**: Usuario destino debe tener `is_active=true`
- **AC2**: No puede degradarse a sí mismo (protección)
- **AC3**: user → admin: crea usuario en proyecto admin (si no existe), sincroniza email/display_name, `role: "admin"`
- **AC4**: admin → user: desactiva acceso admin (revoca refresh tokens admin), mantiene usuario frontend
- **AC5**: Log auditoría

---

## Epic A3: Gestión de Ingredientes (Validación Catálogo)

### UC-ADMIN-012: Listar ingredientes pendientes de validación
**Como** admin, **quiero** ver ingredientes creados por usuarios **para** validar/mergear al catálogo oficial.
- **AC1**: Tabla: ingredientes con `validated_by_admin=false` (paginada, orden: usage_count DESC)
- **AC2**: Columnas: name, slug, category, default_unit, usage_count, created_by (link a usuario), created_at, aliases
- **AC3**: Filtros: categoría, búsqueda nombre/slug
- **AC4**: Acciones: Validar, Editar + Validar, Mergear, Rechazar

### UC-ADMIN-013: Validar ingrediente
**Como** admin, **quiero** aprobar un ingrediente usuario **para** que pase al catálogo oficial.
- **AC1**: Click "Validar" → modal confirma: name, slug, category, default_unit, aliases
- **AC2**: Opción editar antes de validar
- **AC3**: Al validar → `validated_by_admin=true`, `validated_at=now()`, `validated_by=admin_id`
- **AC4**: Ingrediente pasa a catálogo oficial (aparece en autocomplete frontend)

### UC-ADMIN-014: Editar + Validar ingrediente
**Como** admin, **quiero** corregir un ingrediente antes de validar **para** calidad del catálogo.
- **AC1**: Modal prellenado con datos usuario: name, slug, category, default_unit, aliases (editable)
- **AC2**: Validación: slug único (si cambia), categoría válida, unidad válida
- **AC3**: Al guardar → `validated_by_admin=true` + campos actualizados

### UC-ADMIN-015: Mergear ingrediente (deduplicación)
**Como** admin, **quiero** fusionar ingrediente duplicado con catálogo oficial **para** evitar fragmentación.
- **AC1**: Select "Mergear con..." → busca en catálogo oficial (`validated_by_admin=true`)
- **AC2**: Al mergear:
  - Recetas con `ingredient_id` del duplicado → actualizan al oficial
  - `usage_count` oficial += usage_count duplicado
  - Aliases: union de ambos
  - Duplicado → soft delete (`is_active=false`, `merged_into=oficial_id`)
- **AC3**: Log auditoría

### UC-ADMIN-016: Rechazar ingrediente
**Como** admin, **quiero** rechazar ingrediente inapropiado **para** mantener catálogo limpio.
- **AC1**: Modal razón: "Inapropiado", "Duplicado", "Spam", "Otro" + texto libre
- **AC2**: Al rechazar → `is_active=false`, `rejected_by=admin_id`, `rejected_at=now()`, `rejection_reason=...`
- **AC3**: Usuario creador recibe notificación (email/in-app) con razón

### UC-ADMIN-017: Listar ingredientes validados (Catálogo oficial)
**Como** admin, **quiero** ver todos los ingredientes validados **para** gestionar el catálogo oficial.
- **AC1**: Tabla paginada: name, slug, category, default_unit, usage_count, validated_by, validated_at, aliases
- **AC2**: Filtros: categoría, búsqueda nombre/slug, validado por
- **AC3**: Acciones: Editar, Desvalidar (mover a pendientes), Ver uso en recetas

### UC-ADMIN-018: Listar ingredientes rechazados
**Como** admin, **quiero** ver ingredientes rechazados **para** auditoría y posibles recuperaciones.
- **AC1**: Tabla: name, slug, category, rejection_reason, rejected_by, rejected_at, created_by
- **AC2**: Filtros: razón rechazo, fecha rango, rechazado por
- **AC3**: Acción: Recuperar (mover a pendientes con razón)

### UC-ADMIN-019: Normalizar ingrediente (Unidad / Nombre)
**Como** admin, **quiero** normalizar nombre y unidad de ingrediente **para** consistencia del catálogo.
- **AC1**: Modal: name (editable, slug auto), category, default_unit (selector unidades válidas), aliases (textarea)
- **AC2**: Validación: slug único, categoría válida, unidad en whitelist (g, kg, ml, l, unidad, cucharada, cucharadita, taza, pizca)
- **AC3**: Al guardar → actualiza ingrediente + propaga cambios a recetas que lo usan (ingredient_id inmutable)

---

## Epic A4: Gestión de Recetas (Admin)

### UC-ADMIN-020: Listar recetas
**Como** admin, **quiero** ver todas las recetas **para** gestionar el contenido de la plataforma.
- **AC1**: Tabla paginada (20/pág): título, slug, autor (link), categoría, tags, estado (pública/privada/borrada), visitas, favoritos, rating, created_at, updated_at
- **AC2**: Filtros: estado (pública/privada/borrada), categoría, autor (autocomplete), tags, rango fechas creación, rango rating
- **AC3**: Búsqueda: título, slug, autor, ingredientes (live search debounce 300ms)
- **AC4**: Ordenamiento: created_at (default), updated_at, visitas, favoritos, rating, título
- **AC5**: Acciones por fila: ver detalle, editar, eliminar, ocultar/publicar, ver autor

### UC-ADMIN-021: Buscar recetas (Admin)
**Como** admin, **quiero** buscar recetas con filtros avanzados **para** encontrar contenido específico.
- **AC1**: Buscador unificado: título, slug, autor, ingredientes (live search debounce 300ms)
- **AC2**: Filtros combinados (AND): categoría (single), tags (multi), autor, estado, rango fechas, rango rating
- **AC3**: Chips activos removibles + "Limpiar todo"
- **AC4**: Resultados en tabla con paginación + columnas configurables

### UC-ADMIN-022: Ver detalle de receta (Admin)
**Como** admin, **quiero** ver el detalle completo de una receta **para** moderación y auditoría.
- **AC1**: Vista completa: título, slug, imagen, autor (link), categoría, tags, tiempos, porciones, dificultad
- **AC2**: Ingredientes: lista con cantidad, unidad, notas + ingrediente_id (link a catálogo)
- **AC3**: Instrucciones completas + markdown renderizado
- **AC4**: Meta: estado (pública/privada/borrada), visitas, favoritos, rating avg/count, created_at, updated_at, deleted_at
- **AC5**: Acciones: Editar, Eliminar, Ocultar/Publicar, Ver autor, Copiar slug

### UC-ADMIN-023: Editar receta (Admin)
**Como** admin, **quiero** editar cualquier receta **para** corregir errores o moderar contenido.
- **AC1**: Formulario prellenado con todos los campos (título, descripción, categoría, tags, ingredientes, instrucciones, tiempos, porciones, dificultad)
- **AC2**: Validación: categoría activa, tags normalizados, ingredientes válidos (ingredient_id existe y activo)
- **AC3**: Toggle estado: pública ↔ privada (sin borrar)
- **AC4**: Al guardar → `updated_at=now()`, log auditoría (admin_id, receta_id, action="update", diff JSON)

### UC-ADMIN-024: Eliminar receta (Admin)
**Como** admin, **quiero** eliminar una receta definitivamente **para** remover contenido inapropiado.
- **AC1**: Solo si `deleted_at IS NULL` (no borradas previamente)
- **AC2**: Modal doble confirmación: "ELIMINAR DEFINITIVAMENTE receta X? Esta acción es IRREVERSIBLE: receta → soft delete, author_id → system user, contadores preservados"
- **AC3**: Al confirmar → `deleted_at=now()`, `author_id=system_user`, log auditoría
- **AC4**: Toast confirmación + tabla actualizada

### UC-ADMIN-025: Ocultar / Publicar receta
**Como** admin, **quiero** ocultar o publicar una receta **para** moderar visibilidad sin borrar.
- **AC1**: Toggle `is_public` (true ↔ false) con confirmación simple
- **AC2**: Ocultar: receta no aparece en búsquedas públicas, solo autor y admins la ven
- **AC3**: Publicar: receta visible en búsquedas y listados públicos
- **AC4**: Toast + actualización inmediata + log auditoría

### UC-ADMIN-026: Ver estadísticas de receta
**Como** admin, **quiero** ver métricas de una receta **para** evaluar su rendimiento.
- **AC1**: Cards: Visitas totales, Visitas 30d, Favoritos, Rating avg, Rating count, Compartidos
- **AC2**: Gráfico visitas 30d (línea) + distribución ratings (barras 5★→1★)
- **AC3**: Top ingredientes/tags de la receta
- **AC4**: Comparativa: vs promedio categoría, vs promedio global

---

## Epic A5: Métricas y Dashboard

### UC-ADMIN-027: Dashboard global
**Como** admin, **quiero** ver KPIs globales **para** monitorear salud del producto.
- **AC1**: Cards: Usuarios activos (7d/30d), Recetas publicadas, Recetas/mes, Búsquedas/día, Visitas/día, Ratings/día, Avg rating global
- **AC2**: Gráficos: Usuarios nuevos/semana (30d), Recetas publicadas/semana, Engagement (guardados/visitas ratio)
- **AC3**: Top 10: Categorías, Tags, Ingredientes, Autores (por recetas/visitas/ratings)
- **AC4**: Alertas: Usuarios pendientes reactivación, Ingredientes pendientes validación, Errores 5xx última hora

### UC-ADMIN-028: Métricas de contenido
**Como** admin, **quiero** analizar contenido **para** decisiones editoriales.
- **AC1**: Recetas: publicadas/privadas/borradas por mes, por categoría, por autor
- **AC2**: Calidad: % recetas con rating ≥3, % con rating ≥4, distribución ratings
- **AC3**: Engagement: Top recetas por visitas, guardados, ratings; Recetas "fantasma" (0 visitas 30d)
- **AC4**: Exportar CSV (últimos 90d)

### UC-ADMIN-029: Métricas de usuarios
**Como** admin, **quiero** analizar comportamiento usuarios **para** retención.
- **AC1**: Cohort retention (semana 1, 2, 4, 8, 12)
- **AC2**: Funnel activación: Registro → Verificación → 1ra búsqueda → 1er guardado → 1er rating
- **AC3**: Churn: Usuarios inactivos 30d/60d/90d, razones baja (si disponible)
- **AC4**: Segmentos: Power users (≥5 recetas/mes), Casual (1-4), Solo lectores (0 recetas)

---

## Epic A6: Configuración del Sistema

### UC-ADMIN-030: Feature Flags
**Como** admin, **quiero** activar/desactivar features **para** releases graduales.
- **AC1**: Lista flags: `ai_generation_enabled`, `cooking_mode_enabled`, `social_sharing_enabled`, `ingredients_creation_enabled`, `ratings_enabled`
- **AC2**: Toggle por flag + % rollout (0-100%) + targeting (all, beta_users, admins)
- **AC3**: Auditoría: quién cambió, cuándo, valor anterior/nuevo

### UC-ADMIN-031: Límites de Rate Limiting
**Como** admin, **quiero** configurar rate limits **para** proteger la API.
- **AC1**: Config por endpoint: login, register, search, create_recipe, rate_recipe, ai_generate
- **AC2**: Parámetros: requests, window (segundos), burst allowance
- **AC3**: Override por IP/usuario (whitelist/blacklist)

### UC-ADMIN-032: Templates de Email
**Como** admin, **quiero** editar templates de email **para** comunicación.
- **AC1**: Templates: verification, password_reset, reactivation_magic_link, gdpr_confirmation, welcome
- **AC2**: Editor: subject, HTML body, text body, variables disponibles ({{user_name}}, {{link}}, {{code}})
- **AC3**: Preview + test send (a email admin)

### UC-ADMIN-033: Modo Mantenimiento
**Como** admin, **quiero** activar modo mantenimiento **para** deploys/emergencias.
- **AC1**: Toggle ON/OFF + mensaje personalizado + ETA opcional
- **AC2**: ON → API devuelve 503 (excepto `/health`, `/admin/*` con bypass), frontend muestra banner
- **AC3**: Log auditoría + notificación admins (email/Slack)

---

## Epic A7: Auditoría y Logs

### UC-ADMIN-034: Log de auditoría
**Como** admin, **quiero** ver historial de acciones admin **para** trazabilidad.
- **AC1**: Tabla: timestamp, admin_id, admin_email, action, target_type, target_id, details (JSON), ip_address
- **AC2**: Filtros: admin, action, target_type, rango fechas
- **AC3**: Acciones logadas: todos los CRUD admin, force_reactivate, force_gdpr_erasure, role_change, flag_change, maintenance_toggle
- **AC4**: Export CSV (últimos 90d)

### UC-ADMIN-035: Logs de errores (5xx)
**Como** admin, **quiero** ver errores del backend **para** debugging.
- **AC1**: Lista: timestamp, endpoint, method, status_code, error_message, stack_trace (truncado), user_id (si autenticado), request_id
- **AC2**: Filtros: status_code, endpoint, rango fechas
- **AC3**: Agrupación: por error único (count, first_seen, last_seen)
- **AC4**: Link a request completo (si logging estructurado)

---

## Matriz de Permisos Admin (RBAC)

| Acción | Admin | Superadmin (opcional v2) |
|--------|-------|--------------------------|
| Categorías CRUD | ✓ | ✓ |
| Usuarios: listar, ver, activar/desactivar, reactivar, GDPR | ✓ | ✓ |
| Usuarios: cambiar rol | ✓ | ✓ |
| Recetas: listar, buscar, ver, editar, eliminar, ocultar/publicar, stats | ✓ | ✓ |
| Ingredientes: listar (validados/pendientes/rechazados), validar, editar, mergear, rechazar, normalizar | ✓ | ✓ |
| Métricas: dashboard, export | ✓ | ✓ |
| Feature flags | ✓ | ✓ |
| Rate limits | ✓ | ✓ |
| Email templates | ✓ | ✓ |
| Modo mantenimiento | ✓ | ✓ |
| Auditoría logs | ✓ | ✓ |
| **Gestión admins** (crear/borrar admins) | ✗ | ✓ (v2) |
| **Configuración crítica** (JWT keys, DB config) | ✗ | ✓ (v2) |

---

## Endpoints API Admin (Scope `admin`)| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/admin/categories` | Listar categorías (paginado, filtros) |
| POST | `/api/admin/categories` | Crear categoría |
| PATCH | `/api/admin/categories/{id}` | Editar categoría |
| DELETE | `/api/admin/categories/{id}` | Eliminar (si 0 recetas) / Desactivar |
| GET | `/api/admin/users` | Listar usuarios (paginado, filtros) |
| GET | `/api/admin/users/{id}` | Detalle usuario |
| POST | `/api/admin/users/{id}/activate` | Activar usuario |
| POST | `/api/admin/users/{id}/deactivate` | Desactivar usuario |
| POST | `/api/admin/users/{id}/reactivate` | Forzar reactivación |
| POST | `/api/admin/users/{id}/gdpr-erase` | Forzar GDPR |
| PATCH | `/api/admin/users/{id}/role` | Cambiar rol |
| GET | `/api/admin/recipes` | Listar recetas (paginado, filtros, búsqueda) |
| GET | `/api/admin/recipes/search` | Buscar recetas (filtros avanzados) |
| GET | `/api/admin/recipes/{id}` | Detalle receta |
| PATCH | `/api/admin/recipes/{id}` | Editar receta |
| DELETE | `/api/admin/recipes/{id}` | Eliminar receta (soft delete) |
| PATCH | `/api/admin/recipes/{id}/visibility` | Ocultar/Publicar (toggle is_public) |
| GET | `/api/admin/recipes/{id}/stats` | Estadísticas de receta |
| GET | `/api/admin/ingredients/pending` | Ingredientes pendientes validación |
| GET | `/api/admin/ingredients/validated` | Ingredientes validados (catálogo oficial) |
| GET | `/api/admin/ingredients/rejected` | Ingredientes rechazados |
| POST | `/api/admin/ingredients/{id}/validate` | Validar ingrediente |
| POST | `/api/admin/ingredients/{id}/merge` | Mergear con oficial |
| POST | `/api/admin/ingredients/{id}/reject` | Rechazar ingrediente |
| POST | `/api/admin/ingredients/{id}/normalize` | Normalizar ingrediente (unidad/nombre) |
| GET | `/api/admin/metrics/dashboard` | KPIs dashboard |
| GET | `/api/admin/metrics/content` | Métricas contenido |
| GET | `/api/admin/metrics/users` | Métricas usuarios |
| GET | `/api/admin/flags` | Feature flags |
| PATCH | `/api/admin/flags/{key}` | Actualizar flag |
| GET | `/api/admin/rate-limits` | Config rate limits |
| PATCH | `/api/admin/rate-limits/{endpoint}` | Actualizar rate limit |
| GET | `/api/admin/email-templates` | Templates email |
| PATCH | `/api/admin/email-templates/{key}` | Actualizar template |
| POST | `/api/admin/email-templates/{key}/test` | Test send |
| PATCH | `/api/admin/maintenance` | Toggle mantenimiento |
| GET | `/api/admin/audit-log` | Log auditoría |
| GET | `/api/admin/error-log` | Log errores 5xx |

---

### Estado de implementación (MVP)

**Implementado** en `/api/admin` (guard: rol `admin`):
- Métricas: `GET /metrics/dashboard`, `GET /metrics/recipes-series?interval=month|week&periods=N` (recetas creadas por mes/semana).
- Categorías: `GET`, `POST`, `PATCH /{id}`, `DELETE /{id}` (elimina si no tiene recetas; si no, desactiva).
- Tags: `GET`, `POST`, `PATCH /{id}`, `DELETE /{id}`.
- Usuarios: `GET` (listado con filtros), `GET /{id}`, `POST /{id}/activate`, `POST /{id}/deactivate`, `PATCH /{id}/role`.
- Recetas: `GET` (listado/filtros/estado), `GET /{id}`, `PATCH /{id}`, `PATCH /{id}/visibility`, `DELETE /{id}` (soft delete).
- Ingredientes: `GET /pending`, `GET /validated`, `GET /rejected`, `POST /{id}/validate`, `POST /{id}/reject`, `POST /{id}/normalize`.
- Métricas extra: `GET /metrics/users-series?interval=month|week&periods=N`, `GET /metrics/overview` (top recetas, recetas por categoría, distribución de calificaciones, crecimiento de usuarios).
- Config: `GET /config`, `PUT /config` (flags `registration_open`, `require_email_verification`, `max_upload_size_mb`, `maintenance_mode`, `rate_limit_per_minute` y plantillas de email; persisten en `app_settings`).
- Audit log: `GET /audit-log` (filtros por `action` y `target_type`, paginado). Se registran acciones de categorías, tags, usuarios, recetas, ingredientes y config.
- Usuarios: `POST /{id}/reactivate`, `POST /{id}/gdpr-erase` (`{delete_recipes: bool}`, anonimiza PII y desactiva).
- Ingredientes: `POST /{id}/merge` (`{target_id}`, reasigna las recetas y borra el duplicado).
- Recetas: `GET /{id}/stats` (visitas, guardados, favoritos, distribución y visitas por día).
- Error log: `GET /error-log` (filtros por `status_code`/`path`); un middleware captura las respuestas 5xx.
- Infra: modo mantenimiento (503 en tráfico público, admin accesible) y rate limiting por minuto (exento `/api/admin`).

**Pendiente (v2)**: `GET /recipes/{id}/stats` ya está; quedan reactivación por email, firma de documentos y otros extras no listados.

## Flujos de Autenticación Admin (Proyecto Separado)

```
1. Admin accede a admin.recetario.com
2. Si no hay access token válido → redirige a /login
3. Login: email + password (solo usuarios con role="admin" en BD)
4. Backend valida → emite JWT pair (access 15min, refresh 30d HttpOnly cookie)
   Claims: { sub, email, role: "admin", admin_id, jti }
5. SvelteKit store guarda access token (memoria), refresh en cookie
6. Requests a /api/admin/* → Authorization: Bearer <access>
7. Backend valida JWT (HS256 en MVP) + claim role="admin" + acceso a /api/admin/* **[endpoints pendientes]**
6. Refresh: POST /auth/refresh (cookie) → nuevo pair (rotación)
7. Logout: POST /auth/logout → revoca refresh actual + access token blacklist (opcional)
```

---

## Notas de Implementación

- **Proyecto**: `recetario-admin` (SvelteKit 5, TypeScript, Vite)
- **Shared types**: Monorepo `packages/api-types` (generado desde OpenAPI backend)
- **UI**: Mismos design tokens que frontend usuario (consistencia visual)
- **Deploy**: Mismo VPS, contenedor Podman separado (`recetario-admin`), mismo dominio subpath `/admin` o subdominio `admin.recetario.com`
- **Auth isolation**: Cookies separadas con `Path=/admin` o dominio separado (claves JWT propias en v2 con RS256)

---

## Próximos Pasos

1. **Confirmar** épicas y casos de uso (¿falta alguno? ¿sobra alguno?)
2. **Priorizar** para MVP Admin (sugerido: A1, A2, A3, A4 básico)
3. **Crear** `docs/use-cases/admin.md` (este documento) + `docs/use-cases/admin-detailed.md` si hace falta
4. **Definir** OpenAPI spec para `/api/admin/*` en `architecture/01-api-design.md`
5. **Diseñar** UI Admin en `docs/ui/` (pages, components)