# Reglas de Negocio

> Fuente de verdad para validaciones, tests y decisiones de diseño. Cada regla tiene un ID trazable.
>
> **Estado de implementación**: ver `docs/decisions/ADR-000-source-of-truth.md`.
> Las reglas marcadas **[v2]** están documentadas pero **no implementadas** en el MVP.

## RB-01: Categoría única por receta
**Descripción**: Una receta pertenece a exactamente una categoría de la lista cerrada.
**Validación**: `category_id` NOT NULL FK → `categories.id`; `categories.is_active = true`.
**Error**: "La receta debe tener una categoría válida y activa".
**Estado**: Implementado.

## RB-02: Etiquetas múltiples por receta
**Descripción**: Una receta puede tener 0..N tags. Los tags son abiertos (user-generated) con autocompletado.
**Validación**: Tabla `recipe_tags` N:M; `tag.slug` normalizado (lowercase, sin acentos, guiones).
**Comportamiento**: Al crear tag nuevo, `usage_count = 1`; al asociar existente, `usage_count++`.
**Estado**: Parcial. La tabla N:M y el modelo existen; los endpoints de alta/edición de recetas aún no asocian tags.

## RB-03: Búsqueda unificada (AND entre dimensiones, OR dentro de cada una)
**Descripción**: La búsqueda combina filtros de forma lógica:
- **Categoría**: exact match (una sola) → AND
- **Tags**: todos los seleccionados deben estar presentes (AND entre tags)
- **Texto libre**: título O descripción vía `ILIKE` → OR
- **Ingredientes**: coincidencia exacta por `ingredient_id` dentro del JSONB → OR
**Ejemplo**: `category=postre AND tag=vegano AND tag=sin-tacc AND (title ILIKE '%brownie%' OR description ILIKE '%brownie%') AND ingredients @> [{"ingredient_id": "..."}]`
**Estado**: Implementado con `ILIKE` + JSONB `contains`. La similitud trigram y la coincidencia parcial por nombre quedan **[v2]**.

## RB-04: Visita única anti-F5 (anónimos + logueados)
**Descripción**: Contar una visita por receta por visitante por día calendario.
**Identificación de visitante**:
- Usuario logueado: `user_id`
- Usuario anónimo: `visitor_fingerprint` = SHA256(IP + User-Agent)
**Unicidad**: Constraint único `(recipe_id, visitor_fingerprint, visited_at)` a nivel aplicación, verificando el mismo día.
**Comportamiento**:
- Si ya existe visita del mismo visitante ese día → no cuenta
- Si es nueva → se inserta y se incrementa `recipes.visit_count` en la capa de aplicación
- F5/refresh mismo día → no incrementa
- Día siguiente → nueva visita permitida
**Estado**: Implementado con fingerprint SHA256(IP+UA). Cookie persistente y salt diario quedan **[v2]**.

## RB-05: Contador de guardados (favoritos/colecciones)
**Descripción**: `recipes.save_count` debe reflejar cuántas veces la receta está guardada en cualquier colección de cualquier usuario.
**Reglas**:
- INSERT en `favorites` → `save_count++`
- DELETE de `favorites` → `save_count--`
- Una misma receta puede estar en múltiples colecciones del mismo usuario → cada par (user, recipe, collection) cuenta como 1
**Estado**: **Implementado** (capa de aplicación, sin triggers): alta de favorito `save_count++`, baja `save_count--`.

## RB-06: Calificación 1-5 + reseña opcional
**Descripción**: Usuario logueado califica 1-5 estrellas + texto opcional. Una calificación por usuario por receta.
**Validación**: `score` CHECK 1-5; UNIQUE `(recipe_id, user_id)`.
**Agregación**: Al crear/actualizar una calificación, la capa de aplicación recalcula:
- `recipes.avg_rating` = AVG(score) redondeado a 2 decimales
- `recipes.rating_count` = COUNT(*)
**Edición**: Usuario puede actualizar su calificación (UPSERT) → recalcula.
**Visualización (UI)**: Promedio mostrado como **estrellas fraccionales** (ej: 4.15 → 4 estrellas llenas + 15% de la 5ta estrella rellena). No redondear a entero. Componente `RatingStars` recibe `avg_rating` (decimal) y `rating_count` (int).
**Estado**: Implementado en la capa de aplicación (sin triggers de BD).

## RB-06b: Moderación de contenido (Post-MVP)
**Descripción**: MVP sin moderación activa. Confianza en comunidad + reportes básicos.
**MVP**: Sin colas de revisión, sin ML. Existe un panel admin separado, pero sin funciones de moderación.
**v2+**: Reportar receta/comentario → cola moderación → acciones (ocultar, advertir, ban).
**Regla**: `is_public` solo lo controla el autor; admin puede forzar `is_public=false` en v2+.

## RB-07: Autocompletado de tags por prefijo + ranking
**Descripción**: Al escribir en input de tag, sugerir tags existentes, ordenados por `usage_count` DESC.
**Implementación**: `GET /api/v1/tags?query=<texto>` → `WHERE (slug ILIKE '%q%' OR name ILIKE '%q%') AND usage_count > 0 ORDER BY usage_count DESC`.
**Estado**: Implementado con coincidencia `ILIKE` (no prefix estricto). Trigram queda **[v2]**.

## RB-08: Imagen representativa única (nullable MVP)
**Descripción**: Campo `recipes.image_url` VARCHAR(500) NULLABLE. En MVP siempre NULL. Preparado para upload futuro (S3, Cloudinary, local).
**Validación futura**: URL válida, content-type image/*, tamaño máx 5MB, dimensiones recomendadas 16:9.
**Estado**: Campo implementado; sin upload.

## RB-09: Recetas públicas por defecto
**Descripción**: `is_public = true` por defecto. Solo recetas públicas aparecen en búsqueda y listados generales.
**Privado**: Autor puede marcar `is_public = false` → solo visible para él (mis recetas).
**Estado**: Implementado.

## RB-10: Soft delete de recetas
**Descripción**: `deleted_at` TIMESTAMPTZ NULLABLE. Borrado lógico: `UPDATE recipes SET deleted_at = now() WHERE id = ?`.
**Consultas**: Todas las consultas públicas incluyen `WHERE deleted_at IS NULL`.
**Cascada**: `favorites`, `visits`, `ratings`, `recipe_tags` tienen FK ON DELETE CASCADE a nivel de modelo.
**Estado**: Implementado (soft delete). Nota: al ser soft delete no se dispara el `ON DELETE CASCADE` físico.

## RB-11: Ingredientes como JSONB estructurado
**Descripción**: `recipes.ingredients` JSONB NOT NULL con schema:
```json
[
  {"ingredient_id": "uuid-del-ingrediente", "amount": 200, "unit": "g", "notes": "todo uso"},
  {"ingredient_id": "uuid-del-ingrediente", "amount": 2, "unit": "unidad", "notes": null}
]
```
**Validación aplicación**: Array (puede estar vacío en el MVP); cada item tiene `ingredient_id` (UUID, req), `amount` (number, req), `unit` (string, req), `notes` (string, opcional).
**Estado**: El modelo/schema usa `ingredient_id`. El seed de ejemplo de `data-model.md` con `name` es **obsoleto** (ver ADR-000).

## RB-12: Dificultad en tres niveles
**Descripción**: `difficulty` en `('easy', 'medium', 'hard')`. Usado para filtrado y badge UI.
**Nota**: La implementación usa valores en inglés; la UI los traduce.
**Estado**: Implementado.

## RB-13: Tiempos en minutos enteros
**Descripción**: `prep_time_minutes`, `cook_time_minutes` INT >= 0. UI muestra "X min" o "X h Y min".
**Estado**: Implementado.

## RB-14: Porciones entero positivo
**Descripción**: `servings` INT > 0. Usado para escalar ingredientes en futuro.
**Estado**: Implementado.

## RB-15: Slug único por receta (SEO)
**Descripción**: Cada receta tiene un `slug` VARCHAR(220) UNIQUE generado automáticamente a partir del título: `slugify(title)` con **desambiguación numérica** si ya existe (`pizza-de-mozzarella` → `pizza-de-mozzarella-2`).
**Uso**: URLs amigables `/receta/<slug>`; lookup por slug en lugar de ID para SEO.
**Inmutabilidad**: El slug se regenera sólo si cambia el título.
**Estado**: Implementado con desambiguación numérica. `nanoid`/hash aleatorio quedan descartados (decisión de producto).

## RB-16: Búsqueda por ingrediente
**Descripción**: Filtro por ingrediente con coincidencia exacta por `ingredient_id` dentro del JSONB `ingredients`.
**Lógica**:
- Selección múltiple → OR entre ingredientes seleccionados.
- Combina con categoría, tags y texto (AND global).
**Estado**: Implementado como equals por `ingredient_id`. La coincidencia parcial por nombre (`ILIKE`/trigram) queda **[v2]**.

## RB-17: Alcance Social — Compartir SÍ, Seguimiento NO
**Descripción**:
- **Compartir**: Web Share API nativo + botón "Copiar link" → genera URL `/receta/<slug>` con `utm_source=share`.
- **Seguimiento (followers/following)**: **NO en MVP**. Sin grafo social, sin feed de actividad.
- **Perfil público**: Accesible en `/usuario/<user_id>` o `/u/<display_name_slug>` → muestra **solo recetas públicas del autor** (grid + paginación). No muestra favoritos, colecciones, ratings dados, ni métricas privadas.
**Estado**: **Implementado** — perfil público (`/usuario/:id`) sin datos sensibles y compartir (Web Share API + copiar link). Sin seguimiento/feed (RB-17).

---

## RB-AUTH-01: Unicidad de email global
**Descripción**: Un email solo puede pertenecer a un usuario.
**Validación**: `email` UNIQUE en `users`.
**Error**: "Email already registered".
**Estado**: Implementado.

## RB-AUTH-02: Vinculación de cuentas (Account Linking)
**Descripción**: Si un usuario existente hace login con OAuth y el email coincide, se vincula el provider_id al mismo usuario.
**Estado**: **Implementado** — OAuth Google/GitHub crea o vincula (`oauth_accounts`) por email de proveedor verificado.

## RB-AUTH-03: Política de contraseña
**Descripción**: Mínimo 8 caracteres (implementado). Requisitos de complejidad (mayúscula, minúscula, número, especial) quedan **[v2]**.
**Hash**: bcrypt (implementado con la librería `bcrypt` directa; `passlib` fue descartado por incompatibilidad con bcrypt 5.x).
**Aplicable**: Registro, cambio de password.

## RB-AUTH-04: Rate limiting
**Descripción**: Protección contra brute force y enumeración.
**Estado**: **Parcial** — hay un **rate limit global por IP/minuto** configurable (`rate_limit_per_minute`, exento `/api/admin`). Los límites específicos por endpoint (login/register/forgot) quedan **[v2]**.

## RB-AUTH-05: Tokens JWT + Refresh Rotation
**Descripción**: Access token **JWT HS256** (15 min) + Refresh token **JWT HS256** con `jti` (30 días, HttpOnly cookie).
**Rotación**: Cada uso de refresh → nuevo access + nuevo refresh.
**Detección de reuso / familias**: **Implementado** — cada refresh se persiste en `refresh_tokens`; presentar un token ya rotado revoca toda su familia (`family_id`) con 401.
**Logout**: Revoca la fila del refresh presentado y borra la cookie.
**Nota**: La spec original decía RS256 + refresh opaque. Se adopta HS256 + refresh JWT (ver ADR-000). RS256/opaque quedan **[v2]**.
**Estado**: Implementado.

## RB-AUTH-06: Verificación de email
**Descripción**: El login rechaza cuentas con `is_verified=false` (403).
**MVP**: el registro crea cuentas **verificadas** (`REQUIRE_EMAIL_VERIFICATION=false`)
para que sean usables de inmediato; con `true` quedan pendientes y se verifica por
enlace. El envío usa SMTP si está configurado (si no, `email_outbox`).
**Estado**: **Implementado** (token 24 h, `POST /auth/verify-email` y `request-verification`).

## RB-AUTH-07: Recuperación de contraseña
**Descripción**: Flujo "olvidé mi contraseña" por email con token de 1 hora.
**Estado**: **Implementado** — `POST /auth/forgot-password` (email vía SMTP/outbox, sin filtrar existencia) y `POST /auth/reset-password` (valida token y cambia la contraseña).

## RB-AUTH-08: Baja lógica de usuario (Soft Delete)
**Descripción**: Usuario se desactiva (`is_active=false`), no se borra físicamente.
**Estado**: **Implementado** — `POST /auth/deactivate` (propia cuenta, opcional borrar recetas) y desactivación por admin.

## RB-AUTH-09: Reactivación de usuario
**Estado**: **Implementado por admin** (`POST /api/admin/users/{id}/reactivate`). La auto-reactivación por magic link queda **[v2]**.

## RB-AUTH-10: Eliminación definitiva (GDPR)
**Estado**: **Implementado** — `POST /auth/delete-account` (anonimiza PII y da de baja las recetas) y `POST /api/admin/users/{id}/gdpr-erase`.

## RB-AUTH-11: Último login tracking
**Descripción**: `last_login_at` se actualiza en cada login exitoso.
**Estado**: Implementado.

---

## RB-ING-01: Catálogo de Ingredientes Normalizado
**Descripción**: Tabla `ingredients` con `slug`, `name`, `category`, `default_unit`, `aliases`.
**Categorías**: proteina, verdura, fruta, lacteo, grano, condimento, grasa, otro.
**Unidades por defecto**: g, kg, ml, l, unidad, cucharada, cucharadita, taza, pizca.
**Aliases**: Array de sinónimos para búsqueda (ej: pollo → {pechuga, suprema}).
**Objetivo de seed**: 300 ingredientes. **Estado**: **Implementado** — seed idempotente con **317** ingredientes (`backend/app/core/ingredients_seed.py`), sin slugs duplicados, marcados `validated_by_admin=true`. No hay columna `usage_count` en ingredientes: el autocomplete ordena por nombre (ranking por uso queda **[v2]**).

## RB-ING-02: Ingredientes en Recetas — Referencia a Catálogo
**Descripción**: `recipes.ingredients` JSONB array de objetos `{ingredient_id, amount, unit, notes?}`.
- `ingredient_id`: UUID obligatorio (validado en app).
- `amount`: number > 0.
- `unit`: string compatible con `default_unit` o en whitelist.
- `notes`: string opcional.
**Estado**: Implementado (validación básica en creación de receta).

## RB-ING-03: Autocompletado de Ingredientes
**Descripción**: Input de ingredientes sugiere del catálogo por coincidencia en `slug`/`name`.
**Implementación**: `GET /api/v1/ingredients?query=<texto>` → `WHERE is_active = true AND (name ILIKE '%q%' OR slug ILIKE '%q%' OR aliases::text ILIKE '%q%') ORDER BY name`.
**Nota**: no existe columna `usage_count` en `ingredients` (la spec la mencionaba por error).
**Estado**: Implementado.

## RB-ING-04: Búsqueda por Ingrediente **[v2 parcial]**
**Descripción**: Filtro por ingrediente con coincidencia exacta por `ingredient_id`.
**Estado**: Implementado el equals por catálogo. La búsqueda parcial por nombre queda **[v2]**.

---

## Trazabilidad de tests

Los casos de prueba y su trazabilidad con estas reglas viven en
`docs/testing/01-test-cases.md`. La estrategia está en
`docs/testing/00-strategy.md`.
