# Caso de Uso: Gestión de Recetas Propias

**ID**: UC-RECIPES-001
**Actor principal**: Usuario autenticado (autor)
**Precondición**: Sesión iniciada
**Objetivo**: Crear, editar, publicar/ocultar, listar y eliminar (soft delete) las recetas propias

---

## Flujo Principal — Crear

1. El usuario entra a `/recetas/nueva`.
2. Completa el formulario (`RecipeForm`): título, descripción, categoría, imagen
   (URL o subida), tiempos, porciones, dificultad, ingredientes, etiquetas,
   preparación y visibilidad.
3. Envía → `POST /api/v1/recipes`.
4. El backend valida categoría activa, genera slug único (con desambiguación
   `-2`, `-3`, …) y asocia etiquetas por slug (crea las faltantes y ajusta
   `usage_count`).
5. Redirige a `/receta/<slug>`.

## Flujo — Editar / publicar / borrar / restaurar

- **Editar**: `/recetas/:slug/editar` → `PATCH /api/v1/recipes/:slug` (solo autor).
  Si cambia el título, se regenera el slug.
- **Toggle público/privado**: `PATCH /api/v1/recipes/:slug` con `is_public`.
- **Borrar**: `DELETE /api/v1/recipes/:slug` (soft delete: setea `deleted_at`).
- **Restaurar**: `POST /api/v1/recipes/:slug/restore`.
- **Listar propias**: `/mis-recetas` (`GET /api/v1/users/me/recipes`,
  `include_deleted`, `include_private`) con tabs Publicadas/Privadas/Borradas.

## Reglas de Negocio

| Regla | Aplicación |
|-------|------------|
| RB-01 | Categoría: FK a tabla cerrada y activa |
| RB-02 | Tags por slug con normalización y `usage_count` |
| RB-08/09 | Validación de campos; visibilidad pública/privada |
| RB-10 | Borrado lógico (`deleted_at`), restaurar |
| RB-11/12/13/14 | Ingredientes referencian el catálogo |
| RB-15 | Slug SEO en `/receta/<slug>` |

## Criterios de Aceptación

| ID | Criterio |
|----|----------|
| AC-01 | Crear receta devuelve 201 con slug único |
| AC-02 | Editar receta ajena devuelve 404 |
| AC-03 | Cambiar el título regenera el slug |
| AC-04 | Soft delete la oculta del listado público; restore la devuelve |
| AC-05 | Editar sin enviar tags conserva las existentes |

## Estado de Implementación

- ✅ CRUD + soft delete + restaurar; slug único; tags; subida de imágenes.
- ✅ `/recetas/nueva`, `/recetas/:slug/editar`, `/mis-recetas`.
- 🔲 Edición colaborativa / historial de versiones; generación por IA (RF-06, v2).
