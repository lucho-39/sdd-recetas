# Use Cases

Define las interacciones entre los actores y el sistema para lograr un
objetivo concreto.

---
## Índice de Casos de Uso

> Solo los marcados **✅** existen como documento. Los **🔲** están pendientes
> de escribir (el estado refleja el documento, no la implementación).

| Archivo | Caso de Uso | Estado | Épica |
|---------|-------------|--------|-------|
| `search.md` | Búsqueda Unificada de Recetas | ✅ Completado | Epic 3: Búsqueda |
| `ingredients.md` | Catálogo Ingredientes (seed, autocomplete, búsqueda) | ✅ Completado | Epic 2: Recetas |
| `admin.md` | Panel Admin (categorías, usuarios, ingredientes, métricas) | ✅ Completado | Epic 9: Admin |
| `notifications.md` | Notificaciones en Tiempo Real (favoritos/ratings) | ✅ Completado | Epic 6/4 |
| `recipes.md` | CRUD Recetas (Crear, Editar, Borrar, Listar propias) | ✅ Completado | Epic 2: Recetas |
| `favorites.md` | Favoritos y Colecciones | ✅ Completado | Epic 4: Favoritos |
| `ratings.md` | Calificaciones y Reseñas | ✅ Completado | Epic 6: Ratings |
| `auth.md` | Autenticación y Cuenta | ✅ Completado | Epic 1: Auth |
| `visit-tracking.md` | Tracking de Visitas (Anti-F5) | ✅ Completado | Transversal |
| `cooking-mode.md` | Modo Cocinando | ✅ Completado | Epic 8: Cocinando |
| `social.md` | Perfil Público + Compartir | 🔲 Pendiente **[v2]** | Epic 5: Social |
| `ai-generation.md` | Generación de Recetas por IA | 🔲 Pendiente **[v2]** | Epic 7: IA |

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

