# Caso de Uso: Calificaciones y Reseñas

**ID**: UC-RATE-001
**Actor principal**: Usuario autenticado
**Precondición**: Sesión iniciada; la receta existe
**Objetivo**: Calificar (1–5) y dejar una reseña; ver el promedio y la distribución

---

## Flujo Principal

1. En el detalle (`/receta/:slug`) el usuario elige estrellas y, opcionalmente,
   escribe una reseña.
2. `POST /api/v1/ratings/{recipe_id}?score=N[&review_text=...]`.
3. El backend hace **upsert** por (receta, usuario), recalcula
   `avg_rating`/`rating_count` y notifica al autor (RF-13): `Tu receta '<título>'
   recibió una calificación de N estrellas de parte de '<usuario>'`.
4. El detalle muestra promedio, distribución (5★→1★) y la lista paginada de reseñas.

## Consultas

- `GET /api/v1/ratings/{recipe_id}` → reseñas paginadas + `distribution`.
- `GET /api/v1/ratings/{recipe_id}/mine` → mi calificación (`score`/`review_text`).
- `DELETE /api/v1/ratings/{recipe_id}` → eliminar la propia y recalcular.

## Reglas de Negocio

| Regla | Aplicación |
|-------|------------|
| RB-06 | Rating 1–5, visible en tarjeta y detalle |
| — | Upsert: una calificación por usuario y receta |
| — | El promedio/conteo se recalculan tras cada cambio |

## Criterios de Aceptación

| ID | Criterio |
|----|----------|
| AC-01 | Calificar guarda el puntaje y actualiza el promedio |
| AC-02 | Re-calificar actualiza (no duplica) |
| AC-03 | Score fuera de 1–5 → 400 |
| AC-04 | `mine` devuelve mi puntaje; `DELETE` lo elimina |

## Estado de Implementación

- ✅ Calificar, reseña textual, distribución, "mi calificación" y eliminación.
- ✅ Lista paginada de reseñas (`ReviewList`) y formulario en el detalle.
- 🔲 Eliminar reseñas por moderación admin; reacciones a reseñas.
