# Requisitos No Funcionales

> Cualidad, restricciones técnicas y operativas. Cada uno medible/verificable.

## RNF-01: Rendimiento
| ID | Requisito | Métrica objetivo | Verificación |
|----|-----------|------------------|--------------|
| RNF-01.1 | Tiempo de respuesta API listado búsquedas (p95) | < 300 ms | Load test k6 / Locust |
| RNF-01.2 | Tiempo de respuesta API detalle receta (p95) | < 200 ms | Load test |
| RNF-01.3 | Tiempo de respuesta autocompletado tags (p95) | < 100 ms | Load test |
| RNF-01.4 | First Contentful Paint (web) | < 1.5 s | Lighthouse CI |
| RNF-01.5 | Time to Interactive (web) | < 3 s | Lighthouse CI |
| RNF-01.6 | Soporte 1000 usuarios concurrentes | Sin degradación > 10% | Stress test |
| RNF-01.7 | Búsqueda full-text + filtros < 500 ms p95 | Con 100k recetas | Load test con dataset realista |

## RNF-02: Escalabilidad
| ID | Requisito | Métrica objetivo | Verificación |
|----|-----------|------------------|--------------|
| RNF-02.1 | Escalado horizontal stateless (API) | Add pods sin downtime | K8s HPA test |
| RNF-02.2 | Base de datos: read replicas para consultas | Lag < 1s | Monitor |
| RNF-02.3 | Cache Redis para listados frecuentes | Hit ratio > 80% | Monitor |
| RNF-02.4 | CDN para assets estáticos + imágenes | 99% requests desde edge | Monitor |

## RNF-03: Disponibilidad
| ID | Requisito | Métrica objetivo | Verificación |
|----|-----------|------------------|--------------|
| RNF-03.1 | Uptime mensual | 99.9% | SLA monitor |
| RNF-03.2 | Deploy zero-downtime | Rolling deploy | CI/CD pipeline |
| RNF-03.3 | Recuperación ante fallo (RTO) | < 5 min | Chaos engineering |
| RNF-03.4 | Pérdida de datos (RPO) | 0 (backups continuos) | Backup test |

## RNF-04: Seguridad
| ID | Requisito | Métrica objetivo | Verificación |
|----|-----------|------------------|--------------|
| RNF-04.1 | Autenticación JWT (access 15min, refresh 30d) | Rotación automática | Pen test |
| RNF-04.2 | Contraseñas: bcrypt/argon2 cost ≥ 12 | — | Code review |
| RNF-04.3 | HTTPS obligatorio (HSTS, TLS 1.3) | 100% tráfico | SSL Labs A+ |
| RNF-04.4 | CORS restrictivo (solo dominio app) | — | Config review |
| RNF-04.5 | Rate limiting auth endpoints | 10 req/min/IP | WAF / middleware |
| RNF-04.6 | Rate limiting API general | 100 req/min/user | Middleware |
| RNF-04.7 | Sanitización XSS en inputs (título, descripción, reseñas) | 0 vulnerabilidades | SAST/DAST |
| RNF-04.8 | Validación JSONB ingredients (schema estricto) | Rechazar inválidos | Unit tests |
| RNF-04.9 | Soft delete + auditoría (created_by, updated_by) | Trazabilidad completa | Audit log |
| RNF-04.10 | Datos personales: GDPR ready (export, delete) | Cumplimiento | Legal review |

## RNF-05: Privacidad
| ID | Requisito | Métrica objetivo | Verificación |
|----|-----------|------------------|--------------|
| RNF-05.1 | Analytics anónimas, opt-in | 0 PII en analytics | Config review |
| RNF-05.2 | Fingerprint visita: hash unidireccional + salt rotativo | No reversible | Crypto review |
| RNF-05.3 | Cookie visita: HttpOnly, Secure, SameSite=Lax, 1 año | — | Browser devtools |
| RNF-05.4 | No tracking cross-site | — | Privacy audit |

## RNF-06: Accesibilidad (WCAG 2.1 AA)
| ID | Requisito | Métrica objetivo | Verificación |
|----|-----------|------------------|--------------|
| RNF-06.1 | Contraste mínimo 4.5:1 (texto), 3:1 (UI) | Pass axe-core | CI axe-core |
| RNF-06.2 | Navegación teclado completa | 100% focusable | Manual test |
| RNF-06.3 | ARIA labels en controles complejos | 0 violations | axe-core |
| RNF-06.4 | Tamaño toque mínimo 44x44px | — | Design review |
| RNF-06.5 | Modo alto contraste soportado | — | CSS test |
| RNF-06.6 | Screen reader: landmarks, headings, alt images | — | NVDA/VoiceOver test |

## RNF-07: Experiencia de Usuario (UX)
| ID | Requisito | Métrica objetivo | Verificación |
|----|-----------|------------------|--------------|
| RNF-07.1 | PWA instalable (manifest, service worker) | Lighthouse PWA > 90 | Lighthouse CI |
| RNF-07.2 | Offline: recetas guardadas disponibles | 100% funcionalidad | Manual test |
| RNF-07.3 | Skeleton loaders en todas las listas | 0 layout shift | CLS < 0.1 |
| RNF-07.4 | Imágenes: lazy loading, WebP/AVIF, responsive | — | Lighthouse |
| RNF-07.5 | Empty states en todas las vistas | 0 vistas sin empty state | Design review |

## RNF-08: Mantenibilidad
| ID | Requisito | Métrica objetivo | Verificación |
|----|-----------|------------------|--------------|
| RNF-08.1 | Cobertura de tests (unit + integration) | > 80% | CI coverage |
| RNF-08.2 | Complexity ciclomática < 10 por función | — | SonarQube |
| RNF-08.3 | Duplicación código < 3% | — | SonarQube |
| RNF-08.4 | Documentación API (OpenAPI/Swagger) | 100% endpoints | CI validation |
| RNF-08.5 | Migraciones DB versionadas, reversibles | — | Code review |

## RNF-09: Observabilidad
| ID | Requisito | Métrica objetivo | Verificación |
|----|-----------|------------------|--------------|
| RNF-09.1 | Logging estructurado (JSON) + correlation ID | 100% requests | Log audit |
| RNF-09.2 | Métricas RED (Rate, Errors, Duration) por endpoint | — | Prometheus/Grafana |
| RNF-09.3 | Traces distribuidos (OpenTelemetry) | 100% requests | Jaeger/Tempo |
| RNF-09.4 | Alertas: error rate > 1%, latency p99 > 2s | < 5 min detection | Alert test |

## RNF-10: Compatibilidad
| ID | Requisito | Métrica objetivo | Verificación |
|----|-----------|------------------|--------------|
| RNF-10.1 | Navegadores: Chrome/FF/Safari/Edge últimas 2 versiones | 0 bugs críticos | BrowserStack |
| RNF-10.2 | Responsive: 320px - 1920px+ | — | Design system |
| RNF-10.3 | PWA: iOS Safari (limitaciones known) | Funcional core | Device test |

---

## Priorización MVP (Must-have vs Nice-to-have)

| Must-have (bloquean release) | Nice-to-have (post-MVP) |
|------------------------------|-------------------------|
| RNF-01.1, 01.2, 01.4, 01.5 | RNF-01.3, 01.6, 01.7 |
| RNF-02.1, 02.4 | RNF-02.2, 02.3 |
| RNF-03.1, 03.2, 03.4 | RNF-03.3 |
| RNF-04.1–04.8 | RNF-04.9, 04.10 |
| RNF-05.1–05.3 | RNF-05.4 |
| RNF-06.1–06.4 | RNF-06.5, 06.6 |
| RNF-07.1, 07.3, 7.5 | RNF-07.2, 07.4 |
| RNF-08.1, 08.4, 08.5 | RNF-08.2, 08.3 |
| RNF-09.1, 09.2 | RNF-09.3, 09.4 |
| RNF-10.1, 10.2 | RNF-10.3 |