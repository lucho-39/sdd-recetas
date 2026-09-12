# Entidades: Detalle de Atributos

## Usuario
| Atributo | Tipo | Constraints | Descripción |
|----------|------|-------------|-------------|
| id | UUID | PK, default gen_random_uuid() | Identificador único |
| email | varchar(320) | NOT NULL, UNIQUE | Email de contacto/login (reservado en baja) |
| password_hash | varchar(255) | NULLABLE | Hash bcrypt/argon2; null si OAuth |
| provider | varchar(20) | NOT NULL, CHECK IN ('email','google','github') | Proveedor de auth |
| provider_id | varchar(255) | NULLABLE, UNIQUE (partial WHERE provider!='email') | ID del proveedor OAuth |
| display_name | varchar(100) | NOT NULL | Nombre visible |
| avatar_url | varchar(500) | NULLABLE | URL de avatar |
| is_active | boolean | NOT NULL, default true | Baja lógica: false = desactivado |
| last_login_at | timestamptz | NULLABLE | Último login exitoso |
| deactivated_at | timestamptz | NULLABLE | Timestamp de baja lógica |
| deletion_requested_at | timestamptz | NULLABLE | Solicitud de eliminación definitiva (GDPR) |
| created_at | timestamptz | NOT NULL, default now() | |
| updated_at | timestamptz | NOT NULL, default now() | Actualizado por trigger |

**Reglas de password (provider=email)**:
- Mínimo 8 caracteres
- Al menos 1 mayúscula, 1 minúscula, 1 número, 1 carácter especial
- Validación en registro y cambio de password
- Hash: argon2id (cost ≥ 12) o bcrypt (cost ≥ 12)

**Estados de usuario**:
| Estado | is_active | deactivated_at | deletion_requested_at | Descripción |
|--------|-----------|----------------|----------------------|-------------|
| Activo | true | NULL | NULL | Usuario normal |
| Desactivado (baja lógica) | false | timestamp | NULL | No puede loguear; datos recuperables |
| Eliminación solicitada (GDPR) | false | timestamp | timestamp | Pendiente anonimización definitiva |
| Anonimizado (post-GDPR) | false | timestamp | timestamp | PII borrado; email → `deleted_<uuid>@deleted.local` |

## Receta
| Atributo | Tipo | Constraints | Descripción |
|----------|------|-------------|-------------|
| id | UUID | PK, default gen_random_uuid() | |
| author_id | UUID | NOT NULL, FK → usuario.id | Autor/creador |
| title | varchar(200) | NOT NULL | Título de la receta |
| slug | varchar(220) | NOT NULL, UNIQUE | SEO-friendly: título normalizado, con sufijo numérico si colisiona (ej: "tortilla-de-patatas", "tortilla-de-patatas-2") |
| description | text | NULLABLE | Descripción breve |
| category_id | UUID | NOT NULL, FK → categoria.id | Categoría (cerrada) |
| image_url | varchar(500) | NULLABLE | MVP: siempre NULL |
| prep_time_minutes | int | NULLABLE, CHECK >= 0 | Tiempo de preparación |
| cook_time_minutes | int | NULLABLE, CHECK >= 0 | Tiempo de cocción |
| servings | int | NULLABLE, CHECK > 0 | Porciones |
| difficulty | varchar(10) | NULLABLE, CHECK IN ('facil','medio','dificil') | Dificultad |
| instructions | text | NOT NULL | Pasos (markdown o numerados) |
| ingredients | jsonb | NOT NULL | Array: `[{ingredient_id, amount, unit, notes?}]` — **ingredient_id FK → ingrediente.id** |
| is_public | boolean | NOT NULL, default true | Visible en búsqueda pública |
| visit_count | int | NOT NULL, default 0 | Contador visitas únicas (denormalizado) |
| save_count | int | NOT NULL, default 0 | Contador guardados (denormalizado) |
| avg_rating | decimal(3,2) | NOT NULL, default 0.00 | Promedio 1-5 (denormalizado) |
| rating_count | int | NOT NULL, default 0 | Cantidad de ratings (denormalizado) |
| created_at | timestamptz | NOT NULL, default now() | |
| updated_at | timestamptz | NOT NULL, default now() | |
| deleted_at | timestamptz | NULLABLE | Soft delete |

**Índices recomendados**:
- `idx_receta_author_id` (author_id)
- `idx_receta_category_id` (category_id)
- `idx_receta_is_public_created` (is_public, created_at DESC) — listados públicos
- `idx_receta_title_trgm` (title) — GIN trigram para búsqueda por nombre
- `idx_receta_ingredients_gin` (ingredients) — GIN jsonb para búsqueda por ingrediente_id
- `idx_receta_slug` (slug) — UNIQUE, lookup por URL

**Generación de slug**: `slugify(title)` con **desambiguación numérica** si el slug ya existe → único, legible, SEO-friendly. Ej: "Tortilla de Patatas" → "tortilla-de-patatas"; si ya existe → "tortilla-de-patatas-2".
> **Nota**: los nombres físicos de tablas/columnas en la base y en los modelos
> son en **inglés** (`users`, `recipes`, `categories`, `ingredients`, `tags`,
> `recipe_tags`, `favorites`, `visits`, `ratings`). Este documento usa nombres
> en español a modo conceptual. Ver `docs/decisions/ADR-000-source-of-truth.md`.

**Estructura ingredients (JSONB normalizado)**:
```json
[
  {"ingredient_id": "uuid-del-ingrediente", "amount": 200, "unit": "g", "notes": "todo uso"},
  {"ingredient_id": "uuid-del-ingrediente", "amount": 2, "unit": "unidad", "notes": null}
]
```
- `ingredient_id`: UUID obligatorio, FK a `ingrediente.id` (validado en app)
- `amount`: number > 0
- `unit`: string, debe coincidir con `ingrediente.default_unit` o estar en whitelist (g, kg, ml, l, unidad, cucharada, cucharadita, taza, pizca)
- `notes`: string opcional (ej: "picado fino", "a temperatura ambiente")

## Categoría
| Atributo | Tipo | Constraints | Descripción |
|----------|------|-------------|-------------|
| id | UUID | PK, default gen_random_uuid() | |
| slug | varchar(50) | NOT NULL, UNIQUE | Key técnica: 'postre', 'entrada', 'snack', 'plato-principal', 'acompañamiento', 'bebida', 'desayuno', 'sopa-crema', 'ensalada', 'horneados' |
| name | varchar(50) | NOT NULL | Display: 'Postre', 'Entrada', 'Snack', 'Plato principal', 'Acompañamiento', 'Bebida', 'Desayuno', 'Sopa / Crema', 'Ensalada', 'Horneados' |
| description | text | NULLABLE | |
| icon | varchar(10) | NULLABLE | Emoji: 🍰 🥗 🍿 🍽️ 🥔 🥤 ☕ 🍲 🥗 🍞 |
| color | varchar(7) | NOT NULL, DEFAULT '#FB923C' | **Hex color** para badge UI (Tailwind 400: orange, green, yellow, blue, purple, cyan, rose, lime, emerald, red) |
| sort_order | int | NOT NULL, default 0 | Orden en UI |
| is_active | boolean | NOT NULL, default true | Para desactivar sin borrar |

## Ingrediente (Catálogo Normalizado — 300 items seed)
| Atributo | Tipo | Constraints | Descripción |
|----------|------|-------------|-------------|
| id | UUID | PK, default gen_random_uuid() | |
| slug | varchar(80) | NOT NULL, UNIQUE | Normalizado: 'pollo', 'tomate', 'aceite-oliva' |
| name | varchar(100) | NOT NULL | Display: 'Pollo', 'Tomate', 'Aceite de oliva' |
| category | varchar(30) | NOT NULL | Grupo: 'proteina', 'verdura', 'fruta', 'lacteo', 'grano', 'condimento', 'grasa', 'otro' |
| default_unit | varchar(20) | NOT NULL | Unidad por defecto: 'g', 'ml', 'unidad', 'cucharada' |
| aliases | text[] | DEFAULT '{}' | Sinónimos para búsqueda: '{pechuga, suprema}' |
| is_active | boolean | NOT NULL, default true | Para desactivar sin borrar |
| created_at | timestamptz | NOT NULL, default now() | |

**Índices**:
- `idx_ingrediente_slug` (slug) — UNIQUE, lookup exacto
- `idx_ingrediente_name_trgm` (name) — GIN trigram para autocomplete
- `idx_ingrediente_category` (category) — Filtro por grupo

**Reglas de normalización de slug**:
- Lowercase, sin acentos, espacios → guiones, solo alnum + guión
- Ej: "Aceite de oliva" → "aceite-oliva", "Pechuga de pollo" → "pechuga-pollo"

## Tag / Etiqueta
| Atributo | Tipo | Constraints | Descripción |
|----------|------|-------------|-------------|
| id | UUID | PK, default gen_random_uuid() | |
| slug | varchar(80) | NOT NULL, UNIQUE | Normalizado: 'sin-tacc', 'vegano' |
| name | varchar(80) | NOT NULL | Display: 'Sin TACC', 'Vegano' |
| usage_count | int | NOT NULL, default 0 | Para ranking autocomplete |
| created_by | UUID | NULLABLE, FK → usuario.id | Creador (null = sistema) |
| created_at | timestamptz | NOT NULL, default now() | |

**Índices**:
- `idx_tag_slug_trgm` (slug) — GIN trigram para autocompletado por prefijo
- `idx_tag_usage_count` (usage_count DESC) — Top tags

## RecetaTag (N:M)
| Atributo | Tipo | Constraints |
|----------|------|-------------|
| recipe_id | UUID | PK, FK → receta.id ON DELETE CASCADE |
| tag_id | UUID | PK, FK → tag.id ON DELETE CASCADE |
| created_at | timestamptz | NOT NULL, default now() |

## Favorito / Guardado
| Atributo | Tipo | Constraints | Descripción |
|----------|------|-------------|-------------|
| user_id | UUID | PK, FK → usuario.id ON DELETE CASCADE | |
| recipe_id | UUID | PK, FK → receta.id ON DELETE CASCADE | |
| collection_name | varchar(100) | PK, NULLABLE | null = "Favoritos"; ej: "Cenas rápidas" |
| created_at | timestamptz | NOT NULL, default now() | |

**Índice**: `idx_favorito_user_collection` (user_id, collection_name)

## Visita
| Atributo | Tipo | Constraints | Descripción |
|----------|------|-------------|-------------|
| id | UUID | PK, default gen_random_uuid() | |
| recipe_id | UUID | NOT NULL, FK → receta.id ON DELETE CASCADE | |
| user_id | UUID | NULLABLE, FK → usuario.id ON DELETE SET NULL | Null = anónimo |
| visitor_fingerprint | varchar(64) | NOT NULL | Hash SHA256(IP + UA + salt) o cookie ID |
| visited_at | timestamptz | NOT NULL, default now() | |

**Constraint único**: `uq_visita_unique_daily` (recipe_id, visitor_fingerprint, date_trunc('day', visited_at))
**Índices**:
- `idx_visita_recipe_date` (recipe_id, visited_at DESC)
- `idx_visita_fingerprint` (visitor_fingerprint)

## Calificación / Rating
| Atributo | Tipo | Constraints | Descripción |
|----------|------|-------------|-------------|
| id | UUID | PK, default gen_random_uuid() | |
| recipe_id | UUID | NOT NULL, FK → receta.id ON DELETE CASCADE | |
| user_id | UUID | NOT NULL, FK → usuario.id ON DELETE CASCADE | |
| score | smallint | NOT NULL, CHECK BETWEEN 1 AND 5 | 1-5 estrellas |
| review_text | text | NULLABLE | Reseña opcional |
| created_at | timestamptz | NOT NULL, default now() | |
| updated_at | timestamptz | NOT NULL, default now() | |

**Constraint único**: `uq_rating_user_recipe` (recipe_id, user_id)
**Índices**:
- `idx_rating_recipe` (recipe_id)
- `idx_rating_user` (user_id)