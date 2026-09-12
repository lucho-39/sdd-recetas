# Alcance y Límites (Scope)

> Delimitación explícita de qué está DENTRO y qué está FUERA del MVP. Evita scope creep.
>
> **Estado**: `[x]` significa "definido dentro del alcance", **no** necesariamente
> implementado. Los ítems no implementados están marcados **[v2]** abajo.
> Ver `docs/decisions/ADR-000-source-of-truth.md`.

---

## ✅ DENTRO del MVP (In Scope)

### Autenticación y Cuenta
- [x] Registro email + password (el gate de verificación existe; el envío de email es **[v2]**)
- [x] Login email + password + JWT (access 15min, refresh 30d)
- [ ] OAuth Google (SHOULD) **[v2]**
- [ ] OAuth GitHub (SHOULD) **[v2]**
- [ ] Recuperar password (email reset) **[v2 — stub]**
- [x] Perfil: nombre, avatar
- [ ] Rate limiting auth endpoints **[v2]**
- [ ] Soft delete cuenta + anonimización PII **[v2]**

### Recetas (CRUD Autor)
- [x] Crear receta completa (todos los campos)
- [x] Editar receta propia
- [x] Soft delete receta propia
- [x] Listar mis recetas (con filtros estado)
- [x] Toggle público/privado
- [x] Validaciones: categoría obligatoria, ingredients JSONB schema, tags normalizados

### Búsqueda y Descubrimiento Público
- [x] Búsqueda texto libre (título + descripción, `ILIKE`)
- [x] Filtro categoría (single select, 10 categorías seed)
- [x] Filtro tags (multi-select, autocomplete prefix + ranking usage_count)
- [x] Filtro ingredientes (multi-select, coincidencia exacta por `ingredient_id`)
- [x] **Búsqueda unificada**: todos los filtros combinados (AND lógico entre dimensiones)
- [x] Ordenamiento: recientes, visitadas, guardadas, calificadas
- [x] Paginación (offset `page`/`limit` + infinite scroll)
- [x] Detalle receta pública (visita registrada anti-F5)
- [ ] URL deep-linkable con todos los filtros **[v2]**

### Favoritos y Colecciones
- [x] Guardar/quitar en "Favoritos" (colección default)
- [x] Crear colecciones personalizadas (nombre único por usuario)
- [x] Mover recetas entre colecciones
- [x] Listar mis colecciones con contadores
- [x] Contador `save_count` denormalizado en receta (increment/decrement triggers)

### Calificaciones y Reseñas
- [x] Calificar 1-5 estrellas (una por usuario/receta)
- [x] Reseña textual opcional (max 2000 chars)
- [x] Editar/borrar propia calificación
- [x] Promedio + distribución en detalle (denormalizado `avg_rating`, `rating_count`)
- [x] Lista paginada de reseñas

### Generación por IA **[v2 — no implementado]**
- [ ] Generar receta desde ingredientes + tags preferencias
- [ ] Vista previa editable antes de guardar
- [ ] Guardar como receta propia

### Modo Cocinando **[v2 — no implementado]**
- [ ] Vista fullscreen + wake lock
- [ ] Pasos grandes, navegación swipe
- [ ] Timer por paso (opcional)

### Tags y Categorías
- [x] 10 categorías seed (postre, entrada, snack, plato-principal, acompañamiento, bebida, desayuno, sopa-crema, ensalada, horneados)
- [x] Tags abiertos user-generated con autocomplete
- [x] Admin: CRUD categorías (solo admins)

### Contadores y Métricas
- [x] Visitas únicas anti-F5 (fingerprint SHA256(IP+UA))
- [ ] Guardados (`save_count`) **[v2 — pendiente de actualización]**
- [x] Visibilidad contadores en listado y detalle

### Técnico / Plataforma
- [ ] PWA instalable (manifest, service worker, offline para guardados) **[v2]**
- [x] Responsive 320px–1920px+ (parcial: frontend en reparación)
- [x] Accesibilidad WCAG 2.1 AA (objetivo; verificación parcial)
- [x] Skeleton loaders
- [x] Logging estructurado (básico de uvicorn)
- [ ] Métricas RED (Prometheus/Grafana) **[v2]**
- [x] Tests de endpoints backend (81 tests; cobertura >80% aún no medida) 
- [ ] CI/CD zero-downtime deploy **[v2]**
- [x] Documentación API OpenAPI (auto-generada por FastAPI)

---

## ❌ FUERA del MVP (Out of Scope) — v2+

### Autenticación Avanzada
- [ ] 2FA / MFA (TOTP, WebAuthn)
- [ ] Login mágico (magic link)
- [ ] Gestión de sesiones activas (ver/dispositivos)
- [ ] Roles granulares (moderador, editor, etc.)

### Recetas Avanzadas
- [ ] Importar receta desde URL (schema.org/Recipe, microdata, JSON-LD)
- [ ] Exportar receta (PDF, schema.org, tarjeta imagen)
- [ ] Versionado de recetas (historial de cambios)
- [ ] Recetas colaborativas (múltiples autores)
- [ ] Fork de receta (copiar y modificar)
- [ ] Escalado automático de ingredientes por porciones
- [ ] Modo "solo ingredientes" para lista de compras
- [ ] Nutrición: macros, calorías, alérgenos (integración USDA/OpenFoodFacts)

### Social y Comunidad
- [ ] Seguir usuarios / feed de actividad
- [ ] Comentarios en recetas (hilos, respuestas, menciones)
- [ ] Notificaciones push/email (nuevas recetas de seguidos, respuestas)
- [ ] Reportar receta/contenido inapropiado
- [ ] Moderación comunitaria (votos útil/no útil en reseñas)
- [ ] Perfil público con stats (recetas, seguidores, guardados)
- [ ] Badges/logros (chef level, especialista vegano, etc.)

### Planificación y Compras
- [ ] Planificador semanal (arrastrar recetas a días)
- [ ] Lista de compras automática (agregar ingredientes de recetas planificadas)
- [ ] Agrupar ingredientes por pasillo/supermercado
- [ ] Marcar comprados, compartir lista
- [ ] Integración supermercados online (API Carrefour, Dia, etc.)

### IA Avanzada
- [ ] Generación desde foto de nevera/despensa (computer vision)
- [ ] Generación desde texto libre ("quiero algo ligero para cena con pollo")
- [ ] Sugerencia de sustituciones ("no tengo X, ¿qué uso?")
- [ ] Análisis nutricional de receta generada
- [ ] Chatbot asistente de cocina (paso a paso, dudas)

### Modo Cocinando Avanzado
- [ ] Navegación por voz completa (comandos: "siguiente", "repite", "cuánto falta")
- [ ] Temporizadores múltiples paralelos
- [ ] Modo "manos sucias" (detección proximidad/gestos cámara)
- [ ] Sincronización entre dispositivos (móvil → tablet en cocina)

### Discovery y Personalización
- [ ] Recomendaciones personalizadas (collaborative filtering)
- [ ] "Recetas para ti" basadas en guardados/ratings
- [ ] Explorar por ingrediente de temporada
- [ ] Colecciones destacadas / editoriales
- [ ] Búsqueda semántica (embeddings + vector DB)

### Monetización / Premium
- [ ] Suscripción premium (sin ads, features extra)
- [ ] Marketplace recetas de chefs verificados
- [ ] Clases de video integradas
- [ ] Nutricionista IA premium

### Técnico / Infra
- [ ] App nativa iOS/Android (React Native / Flutter / Capacitor)
- [ ] Multi-idioma (i18n: EN, PT, FR, IT...)
- [ ] Multi-región / CDN global
- [ ] Event sourcing / CQRS para audit trail completo
- [ ] Vector DB (pgvector, Pinecone, Weaviate) para búsqueda semántica
- [ ] Meilisearch/Typesense/Elasticsearch para búsqueda full-text avanzada
- [ ] Feature flags (LaunchDarkly, Unleash)
- [ ] A/B testing framework

---

## Decisiones de Límite (Boundary Decisions)

| Decisión | Justificación | Revisión |
|----------|---------------|----------|
| **Una imagen por receta (nullable MVP)** | Simplicidad storage; evita gestión galerías, orden, portada vs pasos. Futuro: array de imágenes con `is_cover` flag. | v2 |
| **Categorías cerradas (admin only)** | Taxonomía controlada evita fragmentación; UX consistente. Tags cubren flexibilidad. | v2: permitir sugerir categoría por users |
| **Tags abiertos + autocomplete** | Balance entre control y libertad; usage_count previene duplicados semánticos. | v2: sinónimos, jerarquía tags |
| **Visita única por día (no por sesión)** | Métrica más realista de "interés diario"; evita inflado por F5. Cookie 1 año + salt diario = privacy-friendly. | v2: sesión de 30 min como alternativa |
| **Soft delete obligatorio** | Preserva contadores, ratings, guardados de otros usuarios; GDPR right to erasure = anonimización, no hard delete. | Siempre |
| **Sin comentarios en MVP** | Complejidad moderación, hilos, notificaciones. Ratings + reseña cubren feedback básico. | v2 |
| **Sin lista de compras** | Requiere planificador semanal; feature separada grande. | v2 |
| **Una sola colección "Favoritos" por defecto** | Simplicidad mental; colecciones personalizadas son opt-in. | v2: colecciones inteligentes (recetas veganas guardadas, etc.) |

---

## Criterios de Entrada a v2 (Definition of Ready para siguiente fase)

1. MVP lanzado en producción con ≥ 100 usuarios activos semanales
2. Métricas OBJ-01 a OBJ-06 estables 2+ sprints
3. Feedback cualitativo (encuestas, interviews) ≥ 30 usuarios
4. Deuda técnica < 20% (SonarQube quality gate pass)
5. Documentación API completa y actualizada

---

## Change Log

| Versión | Fecha | Cambio | Autor |
|---------|-------|--------|-------|
| 1.0 | 2026-09-05 | Scope inicial MVP | Orchestrator |