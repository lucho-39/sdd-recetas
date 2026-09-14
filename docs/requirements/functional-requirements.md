# Requisitos Funcionales

> Cada requisito tiene fortaleza (MUST/SHALL/SHOULD) y referencia a reglas de negocio (RB-XX).

## RF-01: Autenticación y registro
| ID | Requisito | Fortaleza | RB |
|----|-----------|-----------|-----|
| RF-01.1 | Registrarse con email + contraseña | MUST | — |
| RF-01.2 | Iniciar sesión con email + contraseña | MUST | — |
| RF-01.3 | Registrarse/iniciar sesión con OAuth Google (config-gated) | SHOULD | — |
| RF-01.4 | Registrarse/iniciar sesión con OAuth GitHub (config-gated) | SHOULD | — |
| RF-01.5 | Cerrar sesión | MUST | — |
| RF-01.6 | Recuperar contraseña (email reset) | SHOULD | — |
| RF-01.7 | Sesión persistente (refresh token, 30 días) | SHOULD | — |

## RF-02: Gestión de recetas (CRUD autor)
| ID | Requisito | Fortaleza | RB |
|----|-----------|-----------|-----|
| RF-02.1 | Crear receta propia (todos los campos) | MUST | RB-01,02,08,09,11-14 |
| RF-02.2 | Editar receta propia | MUST | RB-01,02,08,09,11-14 |
| RF-02.3 | Eliminar receta propia (soft delete) | MUST | RB-10 |
| RF-02.4 | Listar mis recetas (incluye borradas/privadas) | MUST | RB-09,10 |
| RF-02.5 | Ver detalle de receta propia | MUST | — |
| RF-02.6 | Toggle público/privado en receta propia | SHOULD | RB-09 |

> Implementado en `/recetas/nueva` y `/recetas/:slug/editar` con `RecipeForm`.
> Crear/editar asocian etiquetas por slug (`tags` en `RecipeCreate`/`RecipeUpdate`),
> creando las faltantes y manteniendo `usage_count`. Borrar/restaurar soft delete.
> **Imágenes**: subida a disco local (`POST /api/v1/uploads`, volumen
> `./.data/uploads`) o URL externa; las imágenes se sirven en `/uploads`. La
> galería/crop y el storage en la nube (S3) quedan fuera de alcance.

## RF-03: Búsqueda y descubrimiento público
| ID | Requisito | Fortaleza | RB |
|----|-----------|-----------|-----|
| RF-03.1 | Buscar recetas públicas por texto libre (título/descripción) | MUST | RB-03 |
| RF-03.2 | Filtrar por categoría (selector single) | MUST | RB-01,03 |
| RF-03.3 | Filtrar por tags (multi-select con autocomplete) | MUST | RB-02,03,07 |
| RF-03.4 | Filtrar por ingredientes (multi-select, coincidencia exacta por `ingredient_id`) | MUST | RB-03,11,16 |
| RF-03.5 | Combinar todos los filtros simultáneamente (AND lógico) | MUST | RB-03 |
| RF-03.6 | Ordenar resultados: más recientes, más visitadas, más guardadas, mejor calificadas | SHOULD | — |
| RF-03.7 | Paginación (cursor o offset) | MUST | — |
| RF-03.8 | Ver detalle de receta pública (URL `/receta/<slug>`) | MUST | RB-04,15 |
| RF-03.9 | Compartir receta (Web Share API + copiar link) | MUST | RB-17 |

## RF-04: Favoritos y colecciones
| ID | Requisito | Fortaleza | RB |
|----|-----------|-----------|-----|
| RF-04.1 | Guardar receta en "Favoritos" (colección default) | MUST | RB-05 |
| RF-04.2 | Guardar receta en colección personalizada (crear/nombrar) | SHOULD | RB-05 |
| RF-04.3 | Quitar receta de favoritos/colección | MUST | RB-05 |
| RF-04.4 | Listar mis favoritos/colecciones | MUST | RB-05 |
| RF-04.5 | Mover receta entre colecciones | SHOULD | RB-05 |
| RF-04.6 | Ver contador de guardados en detalle receta | MUST | RB-05 |

## RF-05: Calificaciones y reseñas
| ID | Requisito | Fortaleza | RB |
|----|-----------|-----------|-----|
| RF-05.1 | Calificar receta 1-5 estrellas (usuario logueado) | MUST | RB-06 |
| RF-05.2 | Escribir reseña textual opcional | SHOULD | RB-06 |
| RF-05.3 | Editar propia calificación/reseña | SHOULD | RB-06 |
| RF-05.4 | Eliminar propia calificación | SHOULD | RB-06 |
| RF-05.5 | Ver promedio y distribución de estrellas en detalle (estrellas fraccionales) | MUST | RB-06 |
| RF-05.6 | Listar reseñas con paginación | SHOULD | — |

> Implementado: calificar 1–5 (`POST /api/v1/ratings/:id`), reseña textual
> opcional, promedio y **distribución de estrellas** (`GET /api/v1/ratings/:id`
> → `distribution`), **mi calificación** (`GET /api/v1/ratings/:id/mine` y
> `my_rating` en el detalle), **eliminar la propia calificación**
> (`DELETE /api/v1/ratings/:id`) y **lista paginada de reseñas** en el detalle
> (`ReviewList`). El upsert por usuario cubre editar la propia calificación
> (RF-05.3).

## RF-06: Generación de recetas por IA **[implementado, config-gated]**
| ID | Requisito | Fortaleza | RB |
|----|-----------|-----------|-----|
| RF-06.1 | Generar receta a partir de lista de ingredientes disponibles | SHOULD | — |
| RF-06.2 | Generar receta con preferencias dietéticas (tags: vegano, keto, etc.) | SHOULD | RB-02 |
| RF-06.3 | Editar receta generada antes de guardar | SHOULD | RF-02.1 |
| RF-06.4 | Guardar receta generada como propia | SHOULD | RF-02.1 |

> `POST /api/v1/ai/generate` (proveedor OpenAI-compatible vía `AI_API_KEY`;
> devuelve 503 si no está configurado). El borrador se revisa/edita en
> `/recetas/generar` y se guarda con el CRUD normal.

## RF-07: Modo "Cocinando" **[implementado]**
| ID | Requisito | Fortaleza | RB |
|----|-----------|-----------|-----|
| RF-07.1 | Activar modo cocinando en detalle de receta | SHOULD | — |
| RF-07.2 | Pantalla siempre activa (wake lock) | SHOULD | — |
| RF-07.3 | Pasos grandes, navegación swipe/voz | SHOULD | — |
| RF-07.4 | Timer integrado por paso | SHOULD | — |

> `frontend/src/routes/cooking/[slug]` + `CookingStepper.svelte`. Wake Lock,
> swipe, teclado, voz (cuando el navegador soporta `SpeechRecognition`), timer
> por paso persistido en `localStorage` y fullscreen. La orientación forzada y
> el prompt de instalación PWA quedan fuera de alcance.

## RF-08: Contadores y métricas
| ID | Requisito | Fortaleza | RB |
|----|-----------|-----------|-----|
| RF-08.1 | Contador de visitas único por día (anti-F5) | MUST | RB-04 |
| RF-08.2 | Contador de guardados (favoritos) | MUST | RB-05 |
| RF-08.3 | Mostrar contadores en listado y detalle | MUST | RB-04,05 |

## RF-09: Tags - Autocompletado y gestión
| ID | Requisito | Fortaleza | RB |
|----|-----------|-----------|-----|
| RF-09.1 | Autocompletado de tags al escribir (prefix + ranking) | MUST | RB-07 |
| RF-09.2 | Crear tag nuevo si no existe (al confirmar) | MUST | RB-02 |
| RF-09.3 | Mostrar tags populares en selector | SHOULD | RB-07 |

## RF-10: Categorías (solo admin)
| ID | Requisito | Fortaleza | RB |
|----|-----------|-----------|-----|
| RF-10.1 | CRUD categorías (solo admins) | SHOULD | RB-01 |
| RF-10.2 | Seed data inicial con 10 categorías | MUST | RB-01 |

## RF-11: Perfil público y social (MVP)
| ID | Requisito | Fortaleza | RB |
|----|-----------|-----------|-----|
| RF-11.1 | Perfil público accesible (`/usuario/<id>` o `/u/<slug>`) | MUST | RB-17 |
| RF-11.2 | Perfil muestra solo recetas públicas del autor (grid + paginación) | MUST | RB-17 |
| RF-11.3 | Perfil NO muestra favoritos, colecciones, ratings dados, métricas privadas | MUST | RB-17 |
| RF-11.4 | Compartir receta (Web Share API nativo + copiar link) | MUST | RB-17 |
| RF-11.5 | NO seguimiento (followers/following), NO feed actividad | MUST | RB-17 |

## RF-12: Catálogo de Ingredientes (300 items seed + gestión)
| ID | Requisito | Fortaleza | RB |
|----|-----------|-----------|-----|
| RF-12.1 | Seed data: 300 ingredientes normalizados (slug, name, category, default_unit, aliases) | MUST | RB-ING-01 |
| RF-12.2 | Categorías: proteina, verdura, fruta, lacteo, grano, condimento, grasa, otro | MUST | RB-ING-01 |
| RF-12.3 | Unidades por defecto: g, kg, ml, l, unidad, cucharada, cucharadita, taza, pizca | MUST | RB-ING-01 |
| RF-12.4 | Autocompletado en selector ingredientes (prefix en slug/name + ranking uso) | MUST | RB-ING-03 |
| RF-12.5 | Crear ingrediente nuevo desde selector si no existe (modal categoría + unidad) | SHOULD | RB-ING-03 |
| RF-12.6 | Validación: ingredient_id debe existir en catálogo y estar activo | MUST | RB-ING-02 |
| RF-12.7 | Búsqueda por ingrediente: catálogo (exacto) + nombre parcial (ILIKE) | MUST | RB-ING-04 |
| RF-12.8 | Whitelist unidades compatibles por ingrediente (default_unit + alternativas) | SHOULD | RB-ING-02 |

## RF-13: Notificaciones en tiempo real (in-app) **[implementado]**
| ID | Requisito | Fortaleza | RB |
|----|-----------|-----------|-----|
| RF-13.1 | Al guardar (favorito) una receta, notificar al autor en tiempo real | SHOULD | RB-05 |
| RF-13.2 | Al calificar una receta, notificar al autor en tiempo real (con puntaje) | SHOULD | RB-06 |
| RF-13.3 | Campanita con badge de no leídas en el navbar | SHOULD | — |
| RF-13.4 | Dropdown con últimas notificaciones; click marca leída y navega a la receta | SHOULD | — |
| RF-13.5 | Eliminar notificaciones individualmente o todas | SHOULD | — |
| RF-13.6 | Canales configurables por el usuario: in-app, email, push (navegador) | SHOULD | — |
| RF-13.7 | Tipo de evento configurable: favoritos y/o calificaciones | SHOULD | — |
| RF-13.8 | Poder desactivar todas las notificaciones | SHOULD | — |

> Transporte: **Socket.IO** (`python-socketio` en FastAPI + `socket.io-client`
> en SvelteKit). Los eventos no deseados no generan notificación; el canal
> in-app deduplica y nunca hay auto-notificación. Email vía SMTP (o `email_outbox`
> cuando no hay SMTP); "push" = notificación del navegador vía Service Worker
> (`showNotification`).

---

## Matriz de cobertura (RF → Casos de uso en docs/use-cases/)

> Los casos de uso marcados **pendientes** aún no existen como documento.
> Ver `docs/use-cases/README.md`.

| RF | Caso de uso |
|----|-------------|
| RF-01 | `auth.md` ✅ |
| RF-02 | `recipes.md` ✅ |
| RF-03 | `search.md` ✅ |
| RF-04 | `favorites.md` ✅ |
| RF-05 | `ratings.md` ✅ |
| RF-06 | `ai-generation.md` ✅ |
| RF-07 | `cooking-mode.md` ✅ |
| RF-08 | `visit-tracking.md` ✅ |
| RF-09 | `search.md` / `ingredients.md` (cubierto) |
| RF-10 | `admin.md` ✅ |
| RF-12 | `ingredients.md` ✅ |
| RF-13 | `notifications.md` ✅ |