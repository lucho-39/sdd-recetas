# Modelo de Dominio: Recetario IA

## Conceptos principales y relaciones

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│   Usuario   │       │   Receta    │       │  Categoría  │
└──────┬──────┘       └──────┬──────┘       └──────┬──────┘
       │                     │                     │
       │ 1:N (autor)         │ N:1                 │
       │                     │                     │
       │              ┌──────┴──────┐              │
       │              │             │              │
       ▼              ▼             ▼              ▼
┌─────────────┐ ┌──────────┐ ┌───────────┐ ┌────────────┐ ┌──────────────┐
│  Favorito   │ │  Visita  │ │   Tag     │ │  Calificación│ │ Ingrediente  │
│ (guardado)  │ │  (view)  │ │ (etiqueta)│ │  (rating)   │ │  (catálogo)  │
└─────────────┘ └──────────┘ └───────────┘ └────────────┘ └──────────────┘
       ▲              ▲             ▲                        ▲
       │ N:M          │ 1:N         │ N:M                    │ 1:N (catálogo)
       │              │             │                        │
       └──────────────┴─────────────┘                        │
                     (RecetaTag)                              │
                                                            ▼
                                                  ┌───────────────────┐
                                                  │ RecetaIngrediente │
                                                  │ (JSONB array con   │
                                                  │  ingredient_id,    │
                                                  │  amount, unit,     │
                                                  │  notes)            │
                                                  └───────────────────┘
```

## Entidades principales

### Usuario
- `id`: UUID (PK)
- `email`: string, unique, not null
- `password_hash`: string, nullable (OAuth users)
- `provider`: enum('email', 'google', 'github'), not null
- `provider_id`: string, nullable (OAuth)
- `display_name`: string, not null
- `avatar_url`: string, nullable
- `created_at`: timestamp
- `updated_at`: timestamp

### Receta
- `id`: UUID (PK)
- `author_id`: UUID (FK → Usuario), not null
- `title`: string, not null, max 200
- `description`: text, nullable
- `category_id`: UUID (FK → Categoría), not null
- `image_url`: string, nullable (MVP: siempre null, preparado para futuro)
- `prep_time_minutes`: integer, nullable
- `cook_time_minutes`: integer, nullable
- `servings`: integer, nullable
- `difficulty`: enum('facil', 'medio', 'dificil'), nullable
- `instructions`: text, not null (pasos numerados o markdown)
- `ingredients`: jsonb, not null (array de objetos: `{name, amount, unit, notes?}`)
- `is_public`: boolean, default true
- `visit_count`: integer, default 0
- `save_count`: integer, default 0
- `avg_rating`: decimal(3,2), default 0.00 (cache denormalizado)
- `rating_count`: integer, default 0 (cache denormalizado)
- `created_at`: timestamp
- `updated_at`: timestamp
- `deleted_at`: timestamp, nullable (soft delete)

### Categoría (lista cerrada, administrable solo por admins)
- `id`: UUID (PK)
- `slug`: string, unique, not null (ej: 'postre', 'entrada', 'snack')
- `name`: string, not null (ej: 'Postre', 'Entrada', 'Snack')
- `description`: text, nullable
- `icon`: string, nullable (nombre de icono o emoji)
- `sort_order`: integer, default 0
- `is_active`: boolean, default true

**Valores semilla (seed data)**:
| slug | name | icon |
|------|------|------|
| postre | Postre | 🍰 |
| entrada | Entrada | 🥗 |
| snack | Snack | 🍿 |
| plato-principal | Plato principal | 🍽️ |
| acompañamiento | Acompañamiento | 🥔 |
| bebida | Bebida | 🥤 |
| desayuno | Desayuno | ☕ |
| otro | Otro | 📦 |

### Ingrediente (Catálogo Normalizado — 300 items seed)
- `id`: UUID (PK)
- `slug`: string, unique, not null (normalizado: 'pollo', 'tomate', 'aceite-oliva')
- `name`: string, not null (display: "Pollo", "Tomate", "Aceite de oliva")
- `category`: string, not null (grupo: 'proteina', 'verdura', 'fruta', 'lacteo', 'grano', 'condimento', 'grasa', 'otro')
- `default_unit`: string, not null (unidad por defecto: 'g', 'ml', 'unidad', 'cucharada')
- `aliases`: string[] (sinónimos para búsqueda: '{pechuga, suprema}')
- `is_active`: boolean, default true
- `created_at`: timestamp

**Reglas de normalización de slug** (igual que tags):
- Lowercase, sin acentos, espacios→guiones, solo alnum+guión
- Ej: "Aceite de oliva" → "aceite-oliva", "Pechuga de pollo" → "pechuga-pollo"

### Tag / Etiqueta (abierta, creada por usuarios con autocompletado)
- `id`: UUID (PK)
- `slug`: string, unique, not null (normalizado: lowercase, sin espacios, ascii)
- `name`: string, not null (display: "Sin TACC", "Vegano", "Keto")
- `usage_count`: integer, default 0 (para ranking en autocompletado)
- `created_by`: UUID (FK → Usuario), nullable
- `created_at`: timestamp

**Reglas de normalización de slug**:
- Lowercase
- Espacios → guiones
- Acentos removidos (á→a, é→e, etc.)
- Solo alphanum + guión
- Ej: "Sin TACC" → "sin-tacc", "Alto Proteína" → "alto-proteina"

### RecetaTag (tabla intermedia N:M)
- `recipe_id`: UUID (FK → Receta), PK parte 1
- `tag_id`: UUID (FK → Tag), PK parte 2
- `created_at`: timestamp

### Favorito / Guardado (N:M Usuario-Receta con metadata)
- `user_id`: UUID (FK → Usuario), PK parte 1
- `recipe_id`: UUID (FK → Receta), PK parte 2
- `collection_name`: string, nullable (ej: "Cenas rápidas", null = "Favoritos general")
- `created_at`: timestamp
- **Unique constraint**: (user_id, recipe_id, collection_name) — una receta puede estar en múltiples colecciones del mismo usuario

### Visita (tracking único anti-F5)
- `id`: UUID (PK)
- `recipe_id`: UUID (FK → Receta), not null
- `user_id`: UUID (FK → Usuario), nullable (anónimo = null)
- `visitor_fingerprint`: string, not null (hash: IP + user-agent + salt, o cookie anonima)
- `visited_at`: timestamp
- **Unique constraint**: (recipe_id, visitor_fingerprint, date_trunc('day', visited_at)) — una visita por receta por visitante por día

### Calificación / Rating
- `id`: UUID (PK)
- `recipe_id`: UUID (FK → Receta), not null
- `user_id`: UUID (FK → Usuario), not null
- `score`: integer, not null, check 1-5
- `review_text`: text, nullable
- `created_at`: timestamp
- `updated_at`: timestamp
- **Unique constraint**: (recipe_id, user_id) — una calificación por usuario por receta

## Reglas de negocio transversales (resumen)

| Regla | Descripción |
|-------|-------------|
| **RB-01** | Una receta pertenece a exactamente una categoría (cerrada) |
| **RB-02** | Una receta puede tener 0..N tags (abiertos) |
| **RB-03** | Búsqueda unificada: categoría + tags + título + ingredientes (AND lógico entre dimensiones, OR dentro de cada dimensión multi-valor) |
| **RB-04** | Visita única: misma receta + mismo visitante (user_id o fingerprint) + mismo día = 1 visita |
| **RB-05** | Guardado: incrementa `save_count`; quitar guardado: decrementa `save_count` |
| **RB-06** | Calificación: 1-5 estrellas + texto opcional; actualiza `avg_rating` y `rating_count` de la receta |
| **RB-07** | Tags: autocompletado por prefijo en `slug` + ranking por `usage_count` |
| **RB-08** | Imagen: un campo `image_url` nullable; MVP siempre null; preparado para upload futuro |