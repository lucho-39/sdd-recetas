# User Stories

> Formato: **Como** [rol], **quiero** [acción] **para** [beneficio].  
> Cada story tiene criterios de aceptación (AC) verificables y referencia a RF/RB.

---

## Epic 1: Autenticación y Cuenta

### US-01: Registro con email
**Como** usuario nuevo, **quiero** registrarme con email y contraseña **para** tener mi cuenta personal.
- **AC1**: Formulario valida email único, password strength (RB-AUTH-03)
- **AC2**: Email de verificación enviado; cuenta inactiva hasta verificación
- **AC3**: Tras verificación → login automático + JWT pair
- **Ref**: RF-01.1, RB-AUTH-01,03,04,07

### US-02: Login con email
**Como** usuario registrado, **quiero** iniciar sesión con email y contraseña **para** acceder a mi cuenta.
- **AC1**: Credenciales válidas → access token (15min) + refresh cookie (30d)
- **AC2**: Credenciales inválidas → error genérico (no enumerar usuarios)
- **AC3**: 5 fallos → rate limit 15 min (RB-AUTH-04)
- **Ref**: RF-01.2, RB-AUTH-04

### US-03: Login con OAuth (Google/GitHub)
**Como** usuario, **quiero** entrar con mi cuenta Google/GitHub **para** no gestionar otra contraseña.
- **AC1**: Redirección a proveedor → callback → upsert por email → JWT pair
- **AC2**: Si email ya existe en BD → vincular provider_id (account linking)
- **AC3**: Nuevo usuario → email verificado automáticamente (proveedor de confianza)
- **Ref**: RF-01.3, RF-01.4, RB-AUTH-02

### US-04: Recuperar contraseña
**Como** usuario que olvidó su password, **quiero** restablecerla por email **para** volver a entrar.
- **AC1**: Email enviado con token 1h; formulario valida nuevo password strength
- **AC2**: Token de un solo uso; invalida refresh tokens existentes
- **Ref**: RF-01.6, RB-AUTH-04

### US-05: Gestión de perfil
**Como** usuario logueado, **quiero** ver y editar mi nombre y avatar **para** personalizar mi cuenta.
- **AC1**: `GET /auth/me` devuelve perfil; `PATCH` actualiza name/avatar_url
- **Ref**: RF-01 (implícito)

### US-06: Desactivar cuenta (baja lógica)
**Como** usuario, **quiero** desactivar mi cuenta temporalmente **para** irme pero poder volver.
- **AC1**: Requiere password actual para confirmar identidad
- **AC2**: Opción "Eliminar mis recetas también" (checkbox, default false)
  - Si false: recetas mantienen autoría original, se muestran como "Usuario eliminado" en UI
  - Si true: recetas → soft delete + author_id → system user
- **AC3**: Favoritos, visitas, calificaciones SE MANTIENEN (user_id intacto para reactivación)
- **AC4**: PII anonimizada en UI: display_name → "Usuario eliminado", avatar → NULL
- **AC5**: Email reservado en BD (no se puede registrar nuevo con mismo email)
- **AC6**: No puede loguear mientras desactivado; middleware bloquea con mensaje claro
- **AC7**: Refresh tokens revocados; sesión terminada
- **Ref**: RB-AUTH-08

### US-07: Reactivar cuenta
**Como** usuario que se desactivó, **quiero** reactivar mi cuenta **para** recuperar mis recetas y datos.
- **AC1**: Verificación de identidad (password actual O magic link por email)
- **AC2**: Requiere nuevo display_name (el anterior se perdió en anonimización)
- **AC3**: `is_active=true`, `deactivated_at=NULL`, display_name restaurado
- **AC4**: Recetas, favoritos, visitas, ratings se "reconectan" automáticamente (FKs intactos)
- **AC5**: Si había elegido "eliminar recetas" en baja → esas recetas ya no se recuperan (están en system user)
- **Ref**: RB-AUTH-09

### US-08: Eliminar cuenta definitivamente (GDPR)
**Como** usuario, **quiero** borrar mi cuenta irrevocablemente **para** ejercer mi derecho al olvido.
- **AC1**: Requiere password actual + confirmación expresa ("ELIMINAR MI CUENTA")
- **AC2**: Anonimización irreversible: email → `deleted_<uuid>@deleted.local`, PII borrada
- **AC3**: Recetas → author_id → system user ("Usuario eliminado")
- **AC4**: Favoritos/Visitas/Calificaciones → user_id → NULL (pierden trazabilidad)
- **AC5**: Tags creados → created_by → NULL
- **AC6**: No hay vuelta atrás; no se puede reactivar
- **Ref**: RB-AUTH-10

---

## Epic 2: Recetas (CRUD Autor)

### US-09: Crear receta
**Como** usuario logueado, **quiero** crear una receta completa **para** compartirla.
- **AC1**: Formulario: título, descripción, categoría (selector obligatorio), tags (autocomplete multi), ingredientes (selector catálogo + cantidad/unidad/notas), instrucciones, tiempos, porciones, dificultad, imagen (opcional MVP null)
- **AC2**: Validación server-side: categoría activa, tags normalizados, ingredientes validados contra catálogo (ingredient_id existe y is_active)
- **AC3**: Receta creada → `is_public=true` por defecto; autor = usuario actual
- **Ref**: RF-02.1, RB-01,02,08,09,11-14, RB-ING-02

### US-10: Editar receta propia
**Como** autor, **quiero** modificar mi receta **para** corregirla o mejorarla.
- **AC1**: Solo autor puede editar (ownership check)
- **AC2**: Mismos campos + validaciones que crear
- **AC3**: `updated_at` actualizado; tags: recalcular usage_count (decrementar eliminados, incrementar nuevos); ingredientes: recalcular usage_count por ingredient_id
- **Ref**: RF-02.2

### US-11: Eliminar receta propia
**Como** autor, **quiero** borrar mi receta **para** que no aparezca más.
- **AC1**: Soft delete (`deleted_at`); no aparece en búsquedas públicas
- **AC2**: En "Mis recetas" se muestra con badge "Eliminada"; opción "Restaurar"
- **AC3**: Contadores (visitas, guardados, ratings) preservados para historial
- **Ref**: RF-02.3, RB-10

### US-12: Listar mis recetas
**Como** autor, **quiero** ver todas mis recetas (públicas, privadas, borradas) **para** gestionarlas.
- **AC1**: Tabla con filtros: estado (publicada/privada/borrada), búsqueda por título
- **AC2**: Acciones rápidas: editar, toggle público, borrar/restaurar
- **Ref**: RF-02.4, RB-09,10

### US-13: Toggle público/privado
**Como** autor, **quiero** hacer una receta privada **para** que solo yo la vea.
- **AC1**: Switch en detalle/edición; `is_public` toggle
- **AC2**: Privada → no en búsqueda pública, no en listados, solo en "Mis recetas"
- **Ref**: RF-02.6, RB-09

---

## Epic 2b: Catálogo de Ingredientes

### US-14: Seed catálogo 300 ingredientes
**Como** sistema, **quiero** poblar 300 ingredientes normalizados al deploy **para** que usuarios seleccionen consistente.
- **AC1**: Migración inserta 300 rows en `ingrediente` (slug, name, category, default_unit, aliases)
- **AC2**: Categorías: proteina, verdura, fruta, lacteo, grano, condimento, grasa, otro
- **AC3**: Unidades: g, kg, ml, l, unidad, cucharada, cucharadita, taza, pizca
- **AC4**: Aliases para búsqueda fuzzy (ej: pollo → {pechuga, suprema})
- **Ref**: RF-12.1, RF-12.2, RF-12.3, RB-ING-01

### US-15: Autocompletado ingredientes en formulario receta
**Como** usuario creando receta, **quiero** autocompletado al escribir ingrediente **para** seleccionar rápido y consistente.
- **AC1**: Input ≥2 chars → sugerencias (prefix slug/name + ranking usage_count)
- **AC2**: Sugerencia muestra: nombre, categoría, unidad por defecto
- **AC3**: Click sugerencia → chip con cantidad + unidad (default_unit) + notas
- **AC4**: Debounce 200ms, respuesta < 100ms p95
- **Ref**: RF-12.4, RB-ING-03

### US-16: Crear ingrediente nuevo desde selector
**Como** usuario, **quiero** crear ingrediente si no existe **para** no interrumpir flujo.
- **AC1**: Botón "Crear 'nombre'" al no encontrar match
- **AC2**: Modal: nombre, categoría (select), unidad por defecto (select), aliases (textarea)
- **AC3**: Validación slug único, categoría/unidad válidas → POST → disponible inmediato
- **AC4**: usage_count inicia en 1
- **Ref**: RF-12.5, RB-ING-03

### US-17: Agregar ingrediente a receta con cantidad y unidad
**Como** usuario, **quiero** especificar cantidad, unidad y notas por ingrediente **para** receta precisa.
- **AC1**: Chip ingrediente + input cantidad (number > 0) + select unidad (default_unit + alternativas)
- **AC2**: Notas opcional (ej: "picado fino", "temperatura ambiente")
- **AC3**: Validación: amount > 0, ingredient_id existe y is_active=true
- **AC4**: Duplicate ingredient_id → merge amounts + concat notes
- **Ref**: RF-12.6, RF-12.7, RF-12.8, RB-ING-02

### US-18: Búsqueda recetas por ingrediente (catálogo + parcial)
**Como** usuario, **quiero** filtrar recetas por ingredientes **para** usar lo que tengo.
- **AC1**: Selector multi-chip con autocompletado (mismo que US-15)
- **AC2**: Lógica: catálogo exacto (ingredient_id) OR nombre parcial (ILIKE) — OR entre chips
- **AC3**: Combina con categoría, tags, texto (AND global)
- **Ref**: RF-12.7, RF-12.8, RB-ING-04

---

## Epic 3: Búsqueda y Descubrimiento

### US-19: Buscar recetas (texto libre)
**Como** usuario (logueado o no), **quiero** buscar recetas por nombre/descripción **para** encontrar lo que quiero cocinar.
- **AC1**: Input búsqueda → resultados paginados (20/página) ordenados por relevancia (trigram similarity) + fecha
- **AC2**: Debounce 300ms en frontend; loading skeleton
- **AC3**: Empty state con sugerencias (categorías populares, tags top)
- **Ref**: RF-03.1, RB-03

### US-20: Filtrar por categoría
**Como** usuario, **quiero** filtrar por una categoría **para** acotar resultados.
- **AC1**: Select/radio group con 10 categorías (icon + nombre); solo una seleccionable
- **AC2**: Combinable con texto, tags, ingredientes (AND lógico)
- **AC3**: URL refleja filtro (`?category=postre`) → shareable/bookmarkable
- **Ref**: RF-03.2, RB-01,03

### US-21: Filtrar por tags (con autocomplete)
**Como** usuario, **quiero** filtrar por múltiples etiquetas dietéticas **para** encontrar recetas que fit mis necesidades.
- **AC1**: Input con autocomplete: al escribir "veg" → sugiere "vegano", "vegetariano", "vegetariano-facil" ordenados por usage_count
- **AC2**: Multi-select: chips removibles; cada tag = AND (receta debe tener TODOS)
- **AC3**: Tag nuevo: al confirmar (Enter/comma) → crear tag si no existe (usage_count=1)
- **Ref**: RF-03.3, RF-09.1-2, RB-02,03,07

### US-22: Filtrar por ingredientes (coincidencia parcial)
**Como** usuario, **quiero** buscar recetas que contengan ciertos ingredientes **para** usar lo que tengo en la nevera.
- **AC1**: Input multi-select tipo tags; busca en `ingredients.name` con **coincidencia parcial** (ILIKE/trigram) — "pollo" matchea "pechuga de pollo", "pollo al horno"
- **AC2**: Lógica OR entre ingredientes seleccionados (cualquiera coincide)
- **AC3**: Combinable con categoría, tags, texto (AND global)
- **Ref**: RF-03.4, RB-03,11,16

### US-23: Búsqueda combinada (todos los filtros juntos)
**Como** usuario, **quiero** aplicar categoría + tags + texto + ingredientes a la vez **para** precisión máxima.
- **AC1**: Todos los filtros visibles en sidebar/header; chips activos removibles individualmente
- **AC2**: "Limpiar todo" resetea a listado general
- **AC3**: URL sincroniza todos los parámetros → deep linkable
- **Ref**: RF-03.5, RB-03

### US-24: Ordenar y paginar resultados
**Como** usuario, **quiero** ordenar resultados y navegar páginas **para** explorar eficientemente.
- **AC1**: Select: "Más recientes", "Más visitadas", "Más guardadas", "Mejor calificadas"
- **AC2**: Paginación cursor-based (infinite scroll) o offset con page numbers
- **AC3**: Estado de orden+página en URL
- **Ref**: RF-03.6, RF-03.7

### US-25: Ver detalle de receta
**Como** usuario, **quiero** ver la receta completa **para** cocinarla.
- **AC1**: Título, imagen (placeholder MVP), autor, categoría, tags, tiempos, porciones, dificultad, ingredientes (lista formateada con cantidad/unidad/notas), instrucciones (pasos numerados), contadores (visitas, guardados, rating avg + count con estrellas fraccionales)
- **AC2**: Si autor → botones editar/borrar/toggle público
- **AC3**: Si logueado → botones guardar, calificar, compartir; si anónimo → login prompt
- **AC4**: Visita registrada (anti-F5 RB-04)
- **AC5**: URL usa slug SEO (`/receta/tortilla-de-patatas`; si ya existe: `/receta/tortilla-de-patatas-2`)
- **AC6**: Botón compartir (Web Share API nativo + fallback copiar link)
- **Ref**: RF-03.8, RF-03.9, RB-04,05,06,15,17

---

## Epic 4: Favoritos y Colecciones

### US-26: Guardar en favoritos
**Como** usuario, **quiero** guardar una receta en favoritos **para** encontrarla fácil después.
- **AC1**: Botón "Guardar" (icono bookmark) en detalle y tarjetas → toggle
- **AC2**: Por defecto en colección "Favoritos" (collection_name = NULL)
- **AC3**: `save_count` incrementa en tiempo real (optimistic UI + server confirm)
- **Ref**: RF-04.1, RB-05

### US-27: Crear colección personalizada
**Como** usuario, **quiero** crear colecciones temáticas **para** organizar mis guardados.
- **AC1**: Modal "Guardar en..." → opción "Nueva colección" → nombre único por usuario
- **AC2**: Colecciones listadas en sidebar/perfil; contador de recetas cada una
- **Ref**: RF-04.2, RB-05

### US-28: Quitar de favoritos/colección
**Como** usuario, **quiero** quitar una receta guardada **para** limpiar mi colección.
- **AC1**: Botón "Quitar" en tarjeta guardada o en detalle → DELETE favorito
- **AC2**: `save_count` decrementa; si colección queda vacía → opcional auto-borrar
- **Ref**: RF-04.3, RB-05

### US-29: Ver mis colecciones
**Como** usuario, **quiero** navegar mis colecciones **para** ver recetas guardadas por tema.
- **AC1**: Vista grid/list igual que búsqueda pero solo mis guardados
- **AC2**: Filtros internos: categoría, tags (de las recetas guardadas)
- **Ref**: RF-04.4

### US-30: Mover entre colecciones
**Como** usuario, **quiero** mover una receta de una colección a otra **para** reorganizar.
- **AC1**: Dropdown en tarjeta guardada → "Mover a..." → lista colecciones
- **AC2**: Net save_count = 0 (DELETE + INSERT mismo user/recipe)
- **Ref**: RF-04.5, RB-05

---

## Epic 5: Perfil Público y Social (MVP)

### US-31: Ver perfil público de autor
**Como** usuario, **quiero** ver el perfil de un autor **para** descubrir sus otras recetas.
- **AC1**: Acceso vía `/usuario/<id>` o `/u/<display_name_slug>` desde tarjeta receta
- **AC2**: Muestra: avatar, display_name, bio (opcional), fecha unión, **grid de recetas públicas del autor** (paginado)
- **AC3**: NO muestra: favoritos, colecciones, ratings dados, métricas privadas, email
- **AC4**: Botón "Compartir perfil" (Web Share API + copiar link)
- **Ref**: RF-11.1, RF-11.2, RF-11.3, RB-17

### US-32: Compartir receta
**Como** usuario, **quiero** compartir una receta **para** que otros la vean.
- **AC1**: Botón "Compartir" en detalle → abre Web Share API nativo (móvil) o modal "Copiar link" (desktop)
- **AC2**: Link generado: `/receta/<slug>?utm_source=share&utm_medium=web&utm_campaign=recipe_share`
- **AC3**: Fallback: "Copiar al portapapeles" con toast confirmación
- **AC4**: Funciona sin login (receta pública) y con login (receta propia privada → link con token temporal opcional v2)
- **Ref**: RF-03.9, RF-11.4, RB-17

### US-33: NO seguimiento / NO feed
**Como** usuario, **quiero** que la app sea simple **para** enfocarme en cocinar, no en redes sociales.
- **AC1**: No existe botón "Seguir" en perfiles ni recetas
- **AC2**: No existe feed de actividad / timeline
- **AC3**: No existe lista de seguidores / seguidos
- **Ref**: RF-11.5, RB-17

---

## Epic 6: Calificaciones y Reseñas

### US-34: Calificar receta
**Como** usuario, **quiero** dar 1-5 estrellas a una receta **para** compartir mi opinión.
- **AC1**: Widget estrellas en detalle (solo logueado); click → envía score
- **AC2**: Una calificación por usuario/receta (upsert); `avg_rating` y `rating_count` actualizan en tiempo real
- **Ref**: RF-05.1, RB-06

### US-35: Escribir reseña
**Como** usuario, **quiero** escribir un comentario junto a mi calificación **para** dar detalles.
- **AC1**: Textarea opcional al calificar; max 2000 chars
- **AC2**: Reseña editable posterior; visible en lista de reseñas
- **Ref**: RF-05.2, RB-06

### US-36: Ver calificaciones y reseñas
**Como** usuario, **quiero** ver el promedio y leer reseñas **para** decidir si cocinarla.
- **AC1**: Header: estrellas grandes + número (ej: 4.7 ★ · 128 reseñas)
- **AC2**: Distribución: barras 5★→1★ con porcentajes
- **AC3**: Lista paginada reseñas (más recientes primero); "Ver todas"
- **Ref**: RF-05.5, RF-05.6

---

## Epic 7: Generación por IA

### US-37: Generar receta por ingredientes
**Como** usuario, **quiero** que la IA me cree una receta con lo que tengo **para** aprovechar ingredientes.
- **AC1**: Input: lista ingredientes (chips) + preferencias (tags: vegano, keto, etc.)
- **AC2**: Output: receta completa (todos los campos) en vista previa editable
- **AC3**: Botón "Guardar como mía" → crea receta propia (RF-02.1)
- **Ref**: RF-06.1, RF-06.2, RF-06.3, RF-06.4

---

## Epic 8: Modo Cocinando

### US-38: Modo cocinando
**Como** usuario cocinando, **quiero** una vista optimizada manos libres **para** seguir pasos sin tocar pantalla.
- **AC1**: Botón "Modo cocinando" en detalle → fullscreen, wake lock, pasos grandes
- **AC2**: Navegación: swipe izq/der, botones grande "Siguiente/Anterior", comando voz "siguiente"
- **AC3**: Timer por paso (opcional): botón "Iniciar timer X min" → notificación
- **Ref**: RF-07.1-4

---

## Epic 9: Tags y Categorías (Admin)

### US-39: Gestionar categorías (Admin)
**Como** admin, **quiero** CRUD categorías **para** mantener la taxonomía.
- **AC1**: Panel admin: listar, crear, editar (nombre, slug, icon, orden), desactivar
- **AC2**: No borrar si hay recetas asociadas (FK RESTRICT); solo desactivar
- **Ref**: RF-10.1, RB-01

---

## Matriz de Trazabilidad (US → RF → RB)

| US | RF | RB |
|----|----|----|
| US-01 a US-08 | RF-01 | RB-AUTH-01 a 11 |
| US-09 a US-13 | RF-02 | RB-01,02,08,09,10,11-14, RB-ING-02 |
| US-14 a US-18 | RF-12 | RB-ING-01 a 04 |
| US-19 a US-25 | RF-03 | RB-03,04, RB-ING-04 |
| US-26 a US-30 | RF-04 | RB-05 |
| US-31 a US-33 | RF-11 | RB-17 |
| US-34 a US-36 | RF-05 | RB-06 |
| US-37 | RF-06 | RB-02 |
| US-38 | RF-07 | — |
| US-39 | RF-10 | RB-01 |

---

## Priorización MVP (Story Points estimados)

| Must (MVP) | Should (MVP si tiempo) | Won't / [v2] |
|------------|------------------------|--------------|
| US-01, 02, 04, 05, 06, 07 | US-30 (mover entre colecciones) | US-03 (OAuth) |
| US-09, 10, 11, 12, 13 | — | US-08 (GDPR delete) |
| US-14, 15, 16, 17, 18 | — | US-37 (IA gen) |
| US-19, 20, 21, 22, 23, 24, 25 | — | US-38 (modo cocina) |
| US-26, 27, 28, 29 | — | — |
| US-31, 32, 33 | — | — |
| US-34, 35, 36 | — | — |
| US-39 (admin) | — | — |

**Total MVP**: 34 stories Must + 1 Should = 35; 4 stories diferidas a v2 (US-03, US-08, US-37, US-38).