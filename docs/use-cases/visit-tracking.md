# Caso de Uso: Tracking de Visitas (Anti-F5)

**ID**: UC-VISIT-001
**Actor principal**: Visitante (anónimo o autenticado)
**Precondición**: La receta existe y no está borrada
**Objetivo**: Contar visitas a una receta evitando inflar el contador al recargar

---

## Flujo Principal

1. El visitante abre el detalle de una receta.
2. El cliente llama `POST /api/v1/visits/{recipe_id}`.
3. El backend calcula un **fingerprint** del visitante
   (`sha256(ip:user-agent)` truncado) y busca una visita del mismo fingerprint
   en la fecha actual.
4. Si no existe: crea la `Visit` e incrementa `recipe.visit_count`.
   Si ya existe: no hace nada (idempotente por día).
5. Responde `201 {"message": "Visit recorded"}` en ambos casos.

## Reglas de Negocio

| Regla | Aplicación |
|-------|------------|
| RB-04 | Visita única por día y por visitante (anti-F5) |
| — | Recetas borradas → 404 |
| — | El contador `visit_count` se muestra en tarjeta y detalle |

## Criterios de Aceptación

| ID | Criterio |
|----|----------|
| AC-01 | Una visita incrementa `visit_count` en 1 |
| AC-02 | Repetir el mismo día no vuelve a contar |
| AC-03 | Receta inexistente → 404 |

## Estado de Implementación

- ✅ Endpoint público con deduplicación diaria por fingerprint.
- ⚠️ El detalle de receta (`GET /recipes/{slug}`) también incrementa
  `visit_count` de forma directa para el conteo inmediato; el endpoint de
  visitas es la vía canónica anti-F5.
- 🔲 Diferenciar visitas autenticadas (`user_id`) de anónimas en métricas.
