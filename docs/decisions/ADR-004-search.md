# ADR-004: Búsqueda de recetas

## Estado

Aceptado — 2026-10-12. Registra la decisión tomada el 2026-09-05 (Q5) y reconciliada en ADR-000 §7.

## Contexto

Búsqueda combinada (texto + categoría + tags + ingredientes) sobre un catálogo chico, con deep links y ordenamientos, sin operar otro servicio.

## Decisión

- **PostgreSQL con ILIKE** en título/descripción/nombres + `contains` de JSONB por `ingredient_id`; filtros combinados en AND; ordenamientos fijos; paginación por offset (`page`/`limit`).
- `pg_trgm` / índices GIN quedan **v2**: figuran en `data-model.md` pero no están provisionados y nada los usa.

## Alternativas

- **Trigram GIN desde el día 1**: descartado; ILIKE alcanza a esta escala y evita extensiones sin provisionar.
- **Motor dedicado (Elasticsearch/Typesense/Meilisearch)**: descartado; otro servicio para operar sin volumen que lo pida.

## Consecuencias

**Positivas**
- Cero infraestructura extra; la búsqueda vive en la misma query del listado.

**Negativas / deuda aceptada**
- ILIKE con `%término%` no escala indefinidamente ni rankea por relevancia; paginación por cursor queda v2.
