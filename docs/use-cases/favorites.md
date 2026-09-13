# Caso de Uso: Favoritos y Colecciones

**ID**: UC-FAV-001
**Actor principal**: Usuario autenticado
**Precondición**: Sesión iniciada; la receta existe
**Objetivo**: Guardar recetas y organizarlas en colecciones

---

## Flujo Principal

1. En el detalle (`/receta/:slug`) el usuario pulsa **Guardar**.
2. El cliente llama `POST /api/v1/favorites/{recipe_id}` (con `collection` opcional).
3. El backend crea el favorito y genera una **notificación** para el autor
   (RF-13) si este lo tiene habilitado.
4. En `/mis-favoritos` el usuario ve el grid y el sidebar de colecciones.

## Acciones

- **Quitar**: `DELETE /api/v1/favorites/{recipe_id}`.
- **Mover a colección**: `PATCH /api/v1/favorites/{recipe_id}` con `{collection_name}`.
- **Renombrar colección**: `PATCH /api/v1/favorites/collections/{name}` `{new_name}`.
- **Borrar colección**: `DELETE /api/v1/favorites/collections/{name}` (las recetas
  vuelven a la lista general, `collection_name = null`).
- **Listar**: `GET /api/v1/favorites` (con receta anidada); **colecciones**:
  `GET /api/v1/favorites/collections` (con conteos).

## Reglas de Negocio

| Regla | Aplicación |
|-------|------------|
| RB-05 | Contador de guardados (`save_count`) |
| — | Un favorito pertenece a **una** colección (o ninguna) |
| — | No se puede guardar dos veces la misma receta (400) |

## Criterios de Aceptación

| ID | Criterio |
|----|----------|
| AC-01 | Guardar devuelve 201 y aparece en `/mis-favoritos` |
| AC-02 | Guardar duplicado devuelve 400 |
| AC-03 | Mover/renombrar/borrar colección refleja los conteos |
| AC-04 | Quitar un favorito lo elimina del listado |

## Estado de Implementación

- ✅ Favoritos + colecciones (mover/renombrar/borrar) + página `/mis-favoritos`.
- 🔲 Colecciones vacías como entidad propia (hoy derivan de los favoritos).
