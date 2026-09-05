# Use Cases

Define las interacciones entre los actores y el sistema para lograr un
objetivo concreto.

---
## Índice de Casos de Uso

| Archivo | Caso de Uso | Estado | Épica |
|---------|-------------|--------|-------|
| `search.md` | Búsqueda Unificada de Recetas | ✅ Completado | Epic 3: Búsqueda |
| `recipes.md` | CRUD Recetas (Crear, Editar, Borrar, Listar propias) | 🔲 Pendiente | Epic 2: Recetas |
| `favorites.md` | Favoritos y Colecciones (Guardar, Quitar, Colecciones) | 🔲 Pendiente | Epic 4: Favoritos |
| `social.md` | Perfil Público + Compartir (Sin seguimiento/feed) | 🔲 Pendiente | Epic 5: Social |
| `ratings.md` | Calificaciones y Reseñas | 🔲 Pendiente | Epic 6: Ratings |
| `auth.md` | Autenticación y Cuenta (Registro, Login, OAuth, Perfil, Baja/Reactivación) | 🔲 Pendiente | Epic 1: Auth |
| `ai-generation.md` | Generación de Recetas por IA | 🔲 Pendiente | Epic 7: IA |
| `cooking-mode.md` | Modo Cocinando | 🔲 Pendiente | Epic 8: Cocinando |
| `visit-tracking.md` | Tracking de Visitas (Anti-F5, Anónimos) | 🔲 Pendiente | Transversal |
| `admin-categories.md` | Admin: Gestión de Categorías | 🔲 Pendiente | Epic 9: Admin |
| `ingredients.md` | Catálogo Ingredientes (300 seed, autocomplete, búsqueda) | 🔲 Pendiente | Epic 2: Recetas |

## Documentos esperados

Un archivo por caso de uso o grupo de casos relacionados, con el actor, la
precondición, el flujo principal y los flujos alternativos:

| Archivo | Qué contiene |
| ------- | ------------ |
| `<caso-de-uso>.md` | Un caso de uso o grupo relacionado (ej: `users.md`, `recipes.md`). |
| `README.md` | Este índice: lista los casos de uso y su estado. |

## Consejos

- Un caso de uso debe ser accionable: el lector entiende qué hace el sistema.
- Los casos de uso alimentan los casos de prueba de `docs/testing/`.

