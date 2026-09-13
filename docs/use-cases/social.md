# Caso de Uso: Perfil Público y Compartir

**ID**: UC-SOCIAL-001
**Actor principal**: Visitante (anónimo o autenticado)
**Precondición**: El usuario existe y está activo
**Objetivo**: Ver el perfil público de un autor y compartir recetas

---

## Flujo Principal

1. Desde el detalle de una receta, el **nombre del autor** es un enlace a
   `/usuario/:id`.
2. La página muestra avatar, `display_name`, "Miembro desde" (`created_at`) y el
   grid de **recetas públicas** del autor (paginado).
3. El botón **Compartir** en el detalle usa la **Web Share API**; si no está
   disponible, copia el link `/receta/<slug>` al portapapeles.

## Reglas de Negocio

| Regla | Aplicación |
|-------|------------|
| RB-17 | El perfil público **no** expone email, favoritos, ratings dados ni métricas privadas |
| RB-17 | **Sin seguimiento** (followers/following) ni feed de actividad en el MVP |
| RB-15 | El link compartido usa el slug SEO |

## Criterios de Aceptación

| ID | Criterio |
|----|----------|
| AC-01 | `/usuario/:id` muestra solo recetas públicas del autor |
| AC-02 | El perfil no incluye datos sensibles (email, favoritos, métricas privadas) |
| AC-03 | Compartir usa Web Share API o copia el link |
| AC-04 | El nombre del autor en el detalle enlaza a su perfil |

## Contrato técnico

- `GET /api/v1/users/{id}` → `PublicProfileResponse` (sin campos sensibles).
- `GET /api/v1/users/{id}/recipes` → recetas públicas paginadas.
- `frontend/src/routes/usuario/[id]/`, `AuthorAvatar`.

## Estado de Implementación

- ✅ Perfil público (`/usuario/:id`), enlace desde el detalle y compartir
  (Web Share API + copiar link).
- 🔲 Seguimiento / feed de actividad (fuera de alcance por RB-17).
