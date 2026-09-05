# Objetivos del Sistema (Medibles)

> Derivados de la visión. Cada objetivo tiene KPI, target MVP y owner.

## Objetivos de Producto

### OBJ-01: Activación temprana
**Descripción**: Usuarios nuevos descubren valor en la primera semana.
| Métrica | Target MVP | Medición |
|---------|------------|----------|
| % usuarios que guardan ≥1 receta en semana 1 | > 40% | Event `recipe_saved` + cohort analysis |
| % usuarios que califican ≥1 receta en semana 1 | > 20% | Event `recipe_rated` |
| % usuarios que usan búsqueda en sesión 1 | > 60% | Event `search_performed` |

### OBJ-02: Retención y hábito
**Descripción**: Usuarios vuelven a cocinar con la app.
| Métrica | Target MVP | Medición |
|---------|------------|----------|
| Retención día 7 | > 35% | Cohort retention (sesión día 0 → sesión día 7) |
| Retención día 30 | > 25% | Cohort retention |
| Sesiones por usuario/semana (activos) | > 2.5 | Avg sessions/week per active user |
| Recetas vistas por usuario/semana | > 5 | `visit_count` agregado por usuario |

### OBJ-03: Calidad de contenido
**Descripción**: Recetas confiables y bien calificadas.
| Métrica | Target MVP | Medición |
|---------|------------|----------|
| % recetas públicas con ≥3 ratings | > 60% | `rating_count >= 3` / total publicadas |
| Promedio global de calificaciones | ≥ 4.2 ★ | AVG(`avg_rating`) WHERE `rating_count` ≥ 3 |
| % recetas con instrucciones completas (pasos ≥ 3) | > 90% | Validación en create/edit |
| % recetas con ≥3 ingredientes | > 95% | JSONB array length |

### OBJ-04: Descubrimiento vía búsqueda
**Descripción**: Búsqueda es el entry point principal.
| Métrica | Target MVP | Medición |
|---------|------------|----------|
| % sesiones con búsqueda | > 50% | Event `search_performed` / sesiones |
| CTR resultado → detalle | > 30% | `visit_count` / impresiones en resultados |
| Búsquedas con filtros combinados (≥2 dimensiones) | > 25% | Query params analysis |
| Tiempo medio búsqueda → primer click | < 8 s | Timestamp diff |

### OBJ-05: Generación IA como diferenciador
**Descripción**: Feature IA genera engagement y contenido.
| Métrica | Target MVP | Medición |
|---------|------------|----------|
| % usuarios que generan ≥1 receta/mes | > 30% | Event `ai_recipe_generated` |
| % recetas generadas que se guardan | > 40% | `saved` / `generated` |
| Tiempo medio generación → guardado | < 3 min | Timestamp diff |

### OBJ-06: Engagement social (guardados + ratings)
**Descripción**: Usuarios contribuyen a la comunidad.
| Métrica | Target MVP | Medición |
|---------|------------|----------|
| Guardados por usuario activo/mes | > 8 | `save_count` agregado / MAU |
| Ratings por usuario activo/mes | > 3 | `rating_count` agregado / MAU |
| Ratio guardados / visitas | > 0.15 | Total saves / total visits |

---

## Objetivos Técnicos

### OBJ-T01: Performance
| Métrica | Target MVP |
|---------|------------|
| API p95 listado búsqueda | < 300 ms |
| API p95 detalle receta | < 200 ms |
| FCP (First Contentful Paint) | < 1.5 s |
| TTI (Time to Interactive) | < 3 s |
| Lighthouse Performance score | > 90 |

### OBJ-T02: Disponibilidad
| Métrica | Target MVP |
|---------|------------|
| Uptime mensual | 99.9% |
| Deploy zero-downtime | 100% deploys |
| Error rate (5xx) | < 0.1% |

### OBJ-T03: Calidad de código
| Métrica | Target MVP |
|---------|------------|
| Test coverage (unit + integration) | > 80% |
| Zero critical/high vulnerabilities (SAST) | 0 |
| Duplicación código | < 3% |

---

## Dashboard de Seguimiento (sugerido)

| Dashboard | Paneles clave |
|-----------|---------------|
| **Product North Star** | WAU, Recetas guardadas/semana, Ratings/semana |
| **Activation Funnel** | Registro → Verificación → Primera búsqueda → Primer guardado → Primera calificación |
| **Search Analytics** | Queries top, Zero-results rate, Filtros usados, CTR |
| **Content Health** | Recetas publicadas/semana, Avg rating, % con ratings, Tiempo medio creación |
| **Technical** | API latency p50/p95/p99, Error rate, DB query time, Cache hit ratio |

---

## Revisión y Ajuste

- **Cadencia**: Revisión mensual en planning meeting
- **Ajuste de targets**: Si métrica supera target 2 meses consecutivos → subir target 10-20%
- **Degradación**: Si métrica cae > 15% vs target → investigar root cause en siguiente sprint