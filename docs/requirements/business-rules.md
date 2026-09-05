# Reglas de Negocio

> Fuente de verdad para validaciones, tests y decisiones de diseño. Cada regla tiene un ID trazable.

## RB-01: Categoría única por receta
**Descripción**: Una receta pertenece a exactamente una categoría de la lista cerrada.
**Validación**: `category_id` NOT NULL FK → `categoria.id`; `categoria.is_active = true`.
**Error**: "La receta debe tener una categoría válida y activa".

## RB-02: Etiquetas múltiples por receta
**Descripción**: Una receta puede tener 0..N tags. Los tags son abiertos (user-generated) con autocompletado.
**Validación**: Tabla `receta_tag` N:M; tag.slug normalizado (lowercase, sin acentos, guiones).
**Comportamiento**: Al crear tag nuevo, `usage_count = 1`; al asociar existente, `usage_count++`.

## RB-03: Búsqueda unificada (AND entre dimensiones, OR dentro de cada una)
**Descripción**: La búsqueda combina filtros de forma lógica:
- **Categoría**: exact match (una sola) → AND
- **Tags**: todos los seleccionados deben estar presentes (AND entre tags) → cada tag es OR interno si el usuario selecciona múltiples
- **Texto libre**: título O descripción (trigram similarity) → OR
- **Ingredientes**: cualquiera de los términos en ingredients JSONB → OR
**Ejemplo**: `categoria=postre AND (tag=vegano AND tag=sin-tacc) AND (titulo~"brownie" OR descripcion~"brownie") AND (ingrediente~"harina" OR ingrediente~"almendra")`

## RB-04: Visita única anti-F5 (anónimos + logueados)
**Descripción**: Contar una visita por receta por visitante por día calendario.
**Identificación de visitante**:
- Usuario logueado: `user_id` (PK en visita)
- Usuario anónimo: `visitor_fingerprint` = SHA256(IP + User-Agent + salt_diario) **o** cookie UUID persistente (1 año, HttpOnly, SameSite=Lax)
**Unicidad**: Constraint único `(recipe_id, visitor_fingerprint, date_trunc('day', visited_at))`
**Comportamiento**: 
- INSERT en `visita` → si constraint violated → no cuenta (ya visitó hoy)
- Si INSERT exitoso → trigger incrementa `receta.visit_count`
- F5/refresh mismo día → no incrementa
- Día siguiente → nueva visita permitida

## RB-05: Contador de guardados (favoritos/colecciones)
**Descripción**: `receta.save_count` refleja cuántas veces la receta está guardada en cualquier colección de cualquier usuario.
**Reglas**:
- INSERT en `favorito` → `save_count++` (trigger AFTER INSERT)
- DELETE de `favorito` → `save_count--` (trigger AFTER DELETE)
- Una misma receta puede estar en múltiples colecciones del mismo usuario → cada par (user, recipe, collection) cuenta como 1
- Mover entre colecciones (DELETE + INSERT misma receta/user) → net 0

## RB-06: Calificación 1-5 + reseña opcional
**Descripción**: Usuario logueado califica 1-5 estrellas + texto opcional. Una calificación por usuario por receta.
**Validación**: `score` CHECK 1-5; UNIQUE `(recipe_id, user_id)`.
**Agregación**: Trigger AFTER INSERT/UPDATE/DELETE en `calificacion` recalcula:
- `receta.avg_rating` = AVG(score)::DECIMAL(3,2)
- `receta.rating_count` = COUNT(*)
**Edición**: Usuario puede actualizar su calificación (UPDATE) → recalcula.
**Visualización (UI)**: Promedio mostrado como **estrellas fraccionales** (ej: 4.15 → 4 estrellas llenas + 15% de la 5ta estrella rellena). No redondear a entero. Componente `RatingStars` recibe `avg_rating` (decimal) y `rating_count` (int).

## RB-06b: Moderación de contenido (Post-MVP)
**Descripción**: MVP sin moderación activa. Confianza en comunidad + reportes básicos.
**MVP**: Sin panel admin, sin colas de revisión, sin ML.
**v2+**: Reportar receta/comentario → cola moderación → acciones (ocultar, advertir, ban).
**Regla**: `is_public` solo lo controla el autor; admin puede forzar `is_public=false` en v2+.

## RB-07: Autocompletado de tags por prefijo + ranking
**Descripción**: Al escribir en input de tag, sugerir tags existentes que empiecen por lo escrito (prefix en `slug`), ordenados por `usage_count` DESC.
**Implementación**: `SELECT slug, name FROM tag WHERE slug LIKE 'prefijo%' ORDER BY usage_count DESC LIMIT 10`
**Alternativa trigram**: `WHERE slug % 'prefijo' ORDER BY usage_count DESC` (más tolerante a typos)

## RB-08: Imagen representativa única (nullable MVP)
**Descripción**: Campo `receta.image_url` VARCHAR(500) NULLABLE. En MVP siempre NULL. Preparado para upload futuro (S3, Cloudinary, local).
**Validación futura**: URL válida, content-type image/*, tamaño máx 5MB, dimensiones recomendadas 16:9.

## RB-09: Recetas públicas por defecto
**Descripción**: `is_public = true` por defecto. Solo recetas públicas aparecen en búsqueda y listados generales.
**Privado**: Autor puede marcar `is_public = false` → solo visible para él (mis recetas).

## RB-10: Soft delete de recetas
**Descripción**: `deleted_at` TIMESTAMPTZ NULLABLE. Borrado lógico: `UPDATE receta SET deleted_at = now() WHERE id = ?`.
**Consultas**: Todas las consultas públicas incluyen `WHERE deleted_at IS NULL`.
**Cascada**: `favorito`, `visita`, `calificacion`, `receta_tag` tienen FK ON DELETE CASCADE → se limpian automáticamente.

## RB-11: Ingredientes como JSONB estructurado
**Descripción**: `ingredients` JSONB NOT NULL con schema:
```json
[
  {"name": "harina", "amount": 200, "unit": "g", "notes": "todo uso"},
  {"name": "huevo", "amount": 2, "unit": "unidad", "notes": null}
]
```
**Validación aplicación**: Array no vacío; cada item tiene `name` (string, req), `amount` (number, req), `unit` (string, req), `notes` (string, opcional).

## RB-12: Dificultad en tres niveles
**Descripción**: `difficulty` ENUM ('facil', 'medio', 'dificil'). Usado para filtrado y badge UI.

## RB-13: Tiempos en minutos enteros
**Descripción**: `prep_time_minutes`, `cook_time_minutes` INT >= 0. UI muestra "X min" o "X h Y min".

## RB-14: Porciones entero positivo
**Descripción**: `servings` INT > 0. Usado para escalar ingredientes en futuro.

## RB-15: Slug único por receta (SEO)
**Descripción**: Cada receta tiene un `slug` VARCHAR(220) UNIQUE generado automáticamente: `slugify(title) + '-' + nanoid(4)`.
**Ejemplo**: "Tortilla de Patatas" → "tortilla-de-patatas-a1b2".
**Uso**: URLs amigables `/receta/<slug>`; lookup por slug en lugar de ID para SEO.
**Generación**: Función `generate_recipe_slug()` en BD; reintenta hasta 10 veces si colisión.
**Inmutabilidad**: Slug no cambia tras creación (evita roturas de enlaces compartidos).

## RB-16: Búsqueda por ingrediente — Coincidencia parcial
**Descripción**: Búsqueda en `ingredients.name` usa **ILIKE/trigram** (no exact match). 
**Ejemplo**: "pollo" coincide con "pechuga de pollo", "pollo al horno", "caldo de pollo".
**Implementación**: `jsonb_path_query` con `@@` + `LIKE_RE` o trigram GIN en `ingredients` → `ingredients @@ '$.ingredients[*].name LIKE_RE "pollo"'` o `ingredients % 'pollo'`.
**Combinación**: Se combina con categoría, tags, texto libre (AND global, OR dentro de ingredientes).

## RB-17: Alcance Social — Compartir SÍ, Seguimiento NO
**Descripción**: 
- **Compartir**: Web Share API nativo + botón "Copiar link" → genera URL `/receta/<slug>` con `utm_source=share`.
- **Seguimiento (followers/following)**: **NO en MVP**. Sin grafo social, sin feed de actividad.
- **Perfil público**: Accesible en `/usuario/<user_id>` o `/u/<display_name_slug>` → muestra **solo recetas públicas del autor** (grid + paginación). No muestra favoritos, colecciones, ratings dados, ni métricas privadas.
- **Compartir receta propia**: Botón en detalle → abre share sheet nativo o copia link al portapapeles.

---

## RB-AUTH-01: Unicidad de email global
**Descripción**: Un email solo puede pertenecer a un usuario (independiente del provider).
**Validación**: `email` UNIQUE en `usuario`.
**Error**: "Este email ya está registrado".

## RB-AUTH-02: Vinculación de cuentas (Account Linking)
**Descripción**: Si un usuario existente hace login con OAuth y el email coincide, se vincula el provider_id al mismo usuario.
**Regla**: Email verificado en proveedor OAuth = confianza para vincular.
**Excepción**: Si email no verificado en OAuth → crear usuario nuevo o pedir confirmación.

## RB-AUTH-03: Política de contraseña (provider=email)
**Descripción**: Mínimo 8 caracteres, al menos 1 mayúscula, 1 minúscula, 1 número, 1 carácter especial.
**Validación**: Regex `^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*]).{8,}$`
**Hash**: argon2id (cost ≥ 12) o bcrypt (cost ≥ 12).
**Aplicable**: Registro, cambio de password, reset password.

## RB-AUTH-04: Rate limiting en auth endpoints
**Descripción**: Protección contra brute force y enumeración.
| Endpoint | Límite | Ventana |
|----------|--------|---------|
| POST /auth/login | 5 intentos | 15 min / IP |
| POST /auth/register | 5 intentos | 15 min / IP |
| POST /auth/forgot-password | 3 intentos | 1 hora / email |
| POST /auth/resend-verification | 3 intentos | 1 hora / usuario |

## RB-AUTH-05: Tokens JWT + Refresh Rotation
**Descripción**: Access token JWT RS256 (15 min), Refresh token opaque (30 días, HttpOnly cookie).
**Rotación**: Cada uso de refresh → nuevo access + nuevo refresh (el anterior revocado).
**Detección de reuso**: Si se presenta refresh revocado → revocar toda la familia (posible robo).
**Logout**: Revoca refresh actual; opcional "logout all devices" revoca toda la familia.

## RB-AUTH-06: Verificación de email
**Descripción**: Email debe verificarse antes de permitir login completo.
**Flujo**: Registro → email con token 24h → click → `email_verified=true` → login permitido.
**Excepción**: OAuth Google/GitHub → email verificado automáticamente (proveedor de confianza).

## RB-AUTH-07: Recuperación de contraseña
**Descripción**: Flujo "olvidé mi contraseña" por email con token de 1 hora, un solo uso.
**Pasos**: 
1. POST /auth/forgot-password {email} → email con link (rate limited RB-AUTH-04)
2. GET /auth/reset-password?token=... → formulario nuevo password (valida RB-AUTH-03)
3. POST /auth/reset-password {token, password} → invalida refresh tokens existentes → login automático

## RB-AUTH-08: Baja lógica de usuario (Soft Delete)
**Descripción**: Usuario se desactiva (`is_active=false`), no se borra físicamente.
**Efectos**:
- No puede loguear (middleware verifica `is_active=true`)
- PII anonimizada en UI: `display_name` → "Usuario eliminado", `avatar_url` → NULL
- Email reservado en BD (UNIQUE se mantiene) → previene registro nuevo con mismo email
- **Recetas**: Por defecto mantienen `author_id` original (recuperable al reactivar)
- **Favoritos/Visitas/Calificaciones**: Mantienen `user_id` original (recuperables)
- **Opción al desactivar**: Usuario elige "Eliminar mis recetas también" → recetas → soft delete + author_id → system user

## RB-AUTH-09: Reactivación de usuario
**Descripción**: Usuario desactivado puede reactivar su cuenta.
**Requisitos**: 
- Verificar identidad (email + password o link magic link)
- Proveer nuevo `display_name` (el anterior se perdió en anonimización)
- `is_active=true`, `deactivated_at=NULL`, `display_name` restaurado
- Recetas, favoritos, visitas, ratings se "reconectan" automáticamente (FKs intactos)

## RB-AUTH-10: Eliminación definitiva (GDPR Right to Erasure)
**Descripción**: Tras solicitud expresa o período de gracia (30 días tras baja), anonimización irreversible.
**Efectos**:
- `email` → `deleted_<uuid>@deleted.local` (reserva único)
- `password_hash`, `provider_id` → NULL
- `display_name` → "Usuario eliminado"
- Recetas: `author_id` → system user (`00000000-0000-0000-0000-000000000000`)
- Favoritos/Visitas/Calificaciones: `user_id` → NULL (pierden trazabilidad a usuario)
- Tags creados: `created_by` → NULL
- Refresh tokens: revocados todos

## RB-AUTH-11: Último login tracking
**Descripción**: `last_login_at` se actualiza en cada login exitoso (email/password u OAuth).
**Uso**: Métricas de actividad, detección de cuentas abandonadas.

---

## RB-ING-01: Catálogo de Ingredientes Normalizado (300 items seed)
**Descripción**: Tabla `ingrediente` con 300 ingredientes predefinidos, cada uno con `slug`, `name`, `category`, `default_unit`, `aliases`.
**Categorías**: proteina, verdura, fruta, lacteo, grano, condimento, grasa, otro.
**Unidades por defecto**: g, kg, ml, l, unidad, cucharada, cucharadita, taza, pizca.
**Aliases**: Array de sinónimos para búsqueda fuzzy (ej: pollo → {pechuga, suprema}).
**Regla**: Solo ingredientes `is_active=true` disponibles para selección.

## RB-ING-02: Ingredientes en Recetas — Referencia a Catálogo
**Descripción**: `receta.ingredients` JSONB array de objetos `{ingredient_id, amount, unit, notes?}`.
- `ingredient_id`: UUID obligatorio, FK a `ingrediente.id` (validado en app).
- `amount`: number > 0.
- `unit`: string, debe ser compatible con `ingrediente.default_unit` o estar en whitelist.
- `notes`: string opcional (ej: "picado fino", "a temperatura ambiente").
**Validación**: Al crear/editar receta, verificar que cada `ingredient_id` existe y está activo.

## RB-ING-03: Autocompletado de Ingredientes
**Descripción**: Input ingredientes sugiere del catálogo por prefix en `slug`/`name` + ranking por uso en recetas.
**Implementación**: `SELECT * FROM ingrediente WHERE (slug LIKE 'prefijo%' OR name ILIKE 'prefijo%') AND is_active=true ORDER BY usage_count DESC LIMIT 10`.
**Creación libre**: Si usuario escribe ingrediente no existente → opción "Crear nuevo" → abre modal con categoría + unidad por defecto → guarda en catálogo (uso futuro).

## RB-ING-04: Búsqueda por Ingrediente — Catálogo + Parcial
**Descripción**: Filtro ingredientes busca en catálogo (exacto por `ingredient_id`) Y en nombres (parcial ILIKE/trigram).
**Lógica**: 
- Selección múltiple de chips → OR entre ingredientes seleccionados.
- Combina con categoría, tags, texto (AND global).
**Ejemplo**: "pollo" matchea recetas con `ingredient_id` de "pollo" Y recetas donde `ingredients.name` contiene "pollo" (legacy/compatibilidad).

---

## Matriz de trazabilidad (Regla → Tests esperados)

| Regla | Test unitario | Test integración | Test E2E |
|-------|---------------|------------------|----------|
| RB-01 | ✓ Validación category_id | ✓ Crear receta sin categoría falla | ✓ UI muestra error |
| RB-02 | ✓ Tag normalización slug | ✓ Asociar múltiples tags | ✓ Autocompletado funciona |
| RB-03 | ✓ Query builder lógica | ✓ Búsqueda combinada | ✓ Filtros UI aplican juntos |
| RB-04 | ✓ Constraint único visita | ✓ F5 no incrementa | ✓ Anónimo + logueado |
| RB-05 | ✓ Trigger save_count | ✓ Guardar/quitar actualiza | ✓ Contador UI sincroniza |
| RB-06 | ✓ CHECK 1-5, UNIQUE | ✓ Promedio recalcula | ✓ Editar calificación |
| RB-07 | ✓ Prefix query + ranking | ✓ Sugerencias API | ✓ Input autocomplete |
| RB-08 | ✓ Campo nullable | — | — |
| RB-09 | ✓ Default is_public | ✓ Privada no en búsqueda | ✓ Toggle UI |
| RB-10 | ✓ Soft delete | ✓ Cascada limpia | ✓ "Mis recetas" muestra borradas |
| RB-11 | ✓ JSONB schema validation | ✓ Búsqueda ingredientes | ✓ Form ingredientes |
| RB-12 | ✓ ENUM check | ✓ Filtro dificultad | ✓ Badge UI |
| RB-13 | ✓ INT >= 0 | ✓ Conversión h/min | ✓ Display |
| RB-14 | ✓ INT > 0 | ✓ Escalar ingredientes | — |