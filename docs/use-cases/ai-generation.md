# Caso de Uso: Generación de Recetas por IA

**ID**: UC-AI-001
**Actor principal**: Usuario autenticado
**Precondición**: El proveedor de IA está configurado (`AI_API_KEY`)
**Objetivo**: Generar un borrador de receta a partir de los ingredientes disponibles

---

## Flujo Principal

1. El usuario entra a `/recetas/generar`.
2. Ingresa ingredientes disponibles, preferencias (opcional) y porciones.
3. `POST /api/v1/ai/generate` con `{ingredients, preferences?, servings?}`.
4. El backend arma un prompt y llama a un endpoint **OpenAI-compatible**
   (`AI_BASE_URL` + `/chat/completions`, modelo `AI_MODEL`) pidiendo un JSON
   estructurado (título, descripción, dificultad, tiempos, porciones, pasos,
   tags e ingredientes).
5. El borrador se muestra en el **formulario de receta** (`RecipeForm`) para
   revisar/editar (RF-06.3).
6. Al guardar, se crea con `POST /api/v1/recipes` como receta propia (RF-06.4).

## Reglas de Negocio

| Regla | Aplicación |
|-------|------------|
| RF-06.1 | Generar a partir de ingredientes |
| RF-06.2 | Preferencias dietéticas (se envían como texto/tags) |
| RF-06.3/06.4 | Editar antes de guardar y guardar como propia |
| — | Si `AI_API_KEY` está vacío → **503** (feature deshabilitada) |
| — | La generación **no** persiste nada por sí sola |

## Criterios de Aceptación

| ID | Criterio |
|----|----------|
| AC-01 | Sin configurar, el endpoint responde 503 |
| AC-02 | Requiere autenticación (401 sin token) |
| AC-03 | Entrada inválida (ingredientes muy cortos) → 422 |
| AC-04 | Con proveedor configurado, devuelve un borrador JSON usable |
| AC-05 | El borrador se puede editar y guardar como receta propia |

## Configuración (env)

`AI_API_KEY`, `AI_BASE_URL` (default `https://api.openai.com/v1`),
`AI_MODEL` (default `gpt-4o-mini`).

## Estado de Implementación

- ✅ Endpoint config-gated, prompt JSON, frontend `/recetas/generar` con revisión
  y guardado vía `RecipeForm`.
- 🔲 Streaming de la respuesta, imágenes generadas y validación del borrador
  contra el catálogo de ingredientes.
