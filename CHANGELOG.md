# Changelog

Todos los cambios relevantes del proyecto Recetario IA.

El formato sigue, de manera simplificada, [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).
El proyecto está en fase **MVP (0.x)**.

## [Unreleased]

### Added — Autenticación y cuenta
- Registro/login/logout/refresh con **JWT HS256** (access 15 min) + refresh JWT con `jti` en cookie HttpOnly.
- Páginas `/login`, `/register`, `/forgot-password`, `/verify-email`.
- **Verificación de email**: token de 24 h (`POST /auth/verify-email`), `POST /auth/request-verification`
  (público, por email) y reenvío desde el login. En el MVP el registro auto-verifica
  (`require_email_verification=false`); el envío real de email depende de SMTP.
- **Recuperación de contraseña** real: token de 1 h, email vía SMTP/outbox y página `/reset-password`.
- **Rotación de refresh con detección de reuso**: presentar un token ya rotado revoca su familia.
- **OAuth Google/GitHub** (config-gated): `GET /auth/oauth/{provider}` + callback, vinculación
  de cuentas y emisión de tokens; 503 si faltan credenciales.
- **Baja y eliminación de cuenta** propias: `POST /auth/deactivate` (opcional borrar recetas) y
  `POST /auth/delete-account` (anonimización GDPR), con botones en `/perfil`.
- Perfil privado (`/perfil`) y **perfil público** (`/usuario/:id`) sin datos sensibles.

### Added — Recetas
- CRUD completo: crear/editar/borrar (soft delete) y **restaurar**; detalle por slug con
  contador de visitas; generación de slug con desambiguación.
- **Ingredientes**: catálogo con **seed de 317 ingredientes** (`ingredients_seed.py`), autocomplete
  sobre datos reales y **alta desde el selector vía modal** (RF-12.5): nombre, categoría, unidad
  por defecto y aliases, con validación de `VALID_CATEGORIES`/`VALID_UNITS` en el backend y alta
  pendiente de revisión de admin. Cada fila de la receta expone la unidad como **`<select>` sobre
  las 9 unidades de RF-12.3** en lugar de texto libre. Nombres resueltos en el detalle,
  cantidad/unidad/notas.
- **Tags**: asociación por slug al crear/editar, con `usage_count` sincronizado.
- **Favoritos y colecciones**: guardar/quitar, mover, renombrar y borrar colecciones.
- **Calificaciones y reseñas**: 1–5 estrellas, reseña textual, promedio y **distribución**,
  "mi calificación" y eliminación de la propia.
- **Subida de imágenes** a disco local (`POST /api/v1/uploads`, servidas en `/uploads`), o URL externa.
- **Generación de recetas por IA** (config-gated): `POST /api/v1/ai/generate` (OpenAI-compatible) y
  revisión/guardado en `/recetas/generar`.
- **`/buscar`**: filtros de texto, categoría, tags, ingredientes, dificultad y tiempo; orden,
  deep links por URL e infinite scroll.
- **`/mis-recetas`**: tabs Publicadas/Privadas/Borradas, toggle de visibilidad, editar y restaurar.
- **Modo Cocinando** (`/cooking/:slug`): wake lock, swipe, teclado, voz, timer por paso y fullscreen.

### Added — Notificaciones en tiempo real
- **Socket.IO** (`python-socketio` + `socket.io-client`): al guardar o calificar una receta, el autor
  recibe la notificación al instante.
- **Campanita** en el navbar con badge de no leídas, dropdown, marcar leída + navegar a la receta,
  borrar una o todas.
- **Preferencias por usuario**: eventos (favoritos/calificaciones) y canales
  (in-app, email, push), incluida la opción de no recibir nada.
- **Email** vía SMTP configurable (`SMTP_HOST`, …) con `email_outbox` persistente como fallback.
- **Push**: **Web Push con VAPID** (Service Worker, funciona con la app cerrada)
  con fallback a notificación del navegador vía Socket.IO cuando no hay suscripción.
- Mensaje de calificación: `Tu receta '{título}' recibió una calificación de {n} estrellas de parte
  de '{usuario}'`.

### Added — Panel de administración
- API `/api/admin` con guard de rol `admin` y UI SvelteKit (shell colapsable, header con usuario/logout).
- **Dashboard** con KPIs y charts de recetas por mes/semana.
- **Métricas** (`/metricas`): crecimiento de usuarios, recetas por categoría, distribución de
  calificaciones y recetas más visitadas.
- **Usuarios**, **Recetas**, **Ingredientes** (validar/rechazar/normalizar), **Categorías** y **Tags**.
- **Configuración** (`/config`): flags `registration_open`, `require_email_verification`,
  `max_upload_size_mb`, `maintenance_mode`, `rate_limit_per_minute` y **plantillas de email**.
- **Audit log** (`/audit-log`): registro de acciones administrativas.
- **Errores** (`/errores`): respuestas 5xx capturadas por un middleware.
- **Estadísticas por receta** (`GET /recipes/{id}/stats`) con vista expandible en `/recetas`.
- **Reactivar** y **borrado GDPR** de usuarios (`/usuarios`); **fusión** de ingredientes duplicados (`/ingredientes`).
- **Desvalidar** y **recuperar** ingredientes (`POST /api/admin/ingredients/{id}/desvalidate` y `/recover`),
  cerrando UC-ADMIN-017 AC3 y UC-ADMIN-018 AC3: mueven un ingrediente entre catálogo oficial y cola de
  pendientes sin romper las recetas que ya lo usan. Ambos auditados, y devuelven 400 si el estado de
  origen no corresponde (desvalidar algo ya pendiente, recuperar algo no rechazado). El listado admin
  de ingredientes ahora expone `created_by`, `validated_by`, `validated_at`, `rejected_by` y `rejected_at`.
- **Modo mantenimiento** (503 en tráfico público, panel admin accesible) y **rate limiting** por minuto
  (configurable, exento para `/api/admin`).

### Added — PWA
- Manifest, ícono, service worker (con fallback offline), botón de instalación y `orientation.lock`
  en el Modo Cocinando.

### Added — API (endpoints destacados)
- `GET/PUT /api/v1/users/me/notification-preferences`.
- `GET /api/v1/notifications`, `/unread-count`, `POST /{id}/read`, `/read-all`, `DELETE /{id}`, `DELETE`.
- `POST /api/v1/recipes/{slug}/restore`; filtros `difficulty` y `max_time` en el listado.
- `GET /api/v1/ratings/{id}/mine`; `DELETE /api/v1/ratings/{id}`.
- `POST /api/v1/uploads`; lectura pública de `tags`, `ingredients` y `categories`.

### Added — Datos y seed
- Seed idempotente de 10 categorías y recetas demo; bootstrap del usuario admin.

### Added — Design system
- **`Dialog`** (`components/ui/Dialog.svelte`) y **`AlertDialog`** (`components/ui/AlertDialog.svelte`),
  que `docs/ui/00-ui-overview.md` ya marcaba como existentes: `role="dialog"`, `aria-modal`,
  `aria-labelledby`/`aria-describedby`, ESC, focus trap con Tab y foco restaurado al cerrar,
  overlay configurable (`closeOnOverlay`) y slot `footer`. `AlertDialog` aporta el variant
  `destructive` para borrados, baja de cuenta y GDPR.
- **`confirmDialog()`** (`stores/confirm.ts`) con API tipo `confirm()` nativo, servida por un único
  `ConfirmHost` montado en `+layout.svelte`. Reemplaza los **7 `confirm()` nativos** de
  `/mis-favoritos`, `/mis-recetas` y `/perfil`, que se leían linealmente y ahora siguen igual
  (`if (!(await confirmDialog(...))) return;`) sin anidar callbacks.

### Infraestructura
- `podman-compose` con **postgres + backend + frontend + admin**, healthchecks y bind mounts persistentes
  (`./.data/postgres`, `./.data/uploads`).
- Backend servido como `app.main:socket_app` (HTTP + Socket.IO en el mismo puerto).
- Frontends en modo **build + preview** (sin HMR en contenedor).
- **`pnpm run check` (svelte-check) habilitado** en el frontend: el typecheck era inexistente
  en la práctica y fue lo que destapó los bugs de la Fase 0 y de la Fase 2.
- **`pnpm run lint` por fin ejecutable**: faltaban `.prettierrc` y `eslint.*` (los plugins ya
  estaban en `devDependencies`), así que el script fallaba antes de analizar nada. Se agregó
  `eslint.config.js` (flat config, con el parser de TypeScript enganchado a los `.svelte`),
  `.prettierrc.json`, `.prettierignore` y se limpiaron los 17 errores que reportó —entre ellos
  los menús con `role="menu"` sin foco ni teclado (AvatarDropdown, NotificationBell) y varias
  piezas de código muerto. El barrido de formato propio de prettier va en un commit aparte.
- **Configuración de Ruff y uv al día**: `select`/`ignore`/`per-file-ignores` migraron a
  `tool.ruff.lint.*` y `tool.uv.dev-dependencies` a `[dependency-groups] dev`, así cada
  `ruff check` y `uv sync` dejan de emitir avisos de deprecación. El recuento de findings no cambió
  (1086, deuda de Fase 4), sólo desapareció el ruido de configuración.

### CI
- `.github/workflows/ci.yml`: job de backend (Postgres + `uv sync` + `pytest`, incluida la suite) y
  job de frontend.
- **El job de frontend ahora corre `pnpm run check` y `pnpm run lint` antes de `pnpm run build`**
  (job renombrado a `frontend-checks`). Vite no falla por identificadores sin import —los trata
  como globales—, así que `build` en verde **no** prueba typecheck ni lint: sin estos pasos los
  gates recién habilitados se habrían vuelto a apagar en silencio.
- **Test de integración de Socket.IO** (`tests/test_realtime_socket.py`): levanta un servidor ASGI real
  y valida autenticación, unión al room y entrega del evento.

### Added
- **RF-12.8 — whitelist de unidades por ingrediente.** Cada ingrediente del catálogo puede
  declarar unidades alternativas compatibles (`ingredients.allowed_units`, JSONB). La
  validación de una receta acepta sólo `default_unit` + las listadas y responde **422**
  nombrando los ingredientes que fallan. Una lista vacía sigue siendo permisiva, así que
  las 320 filas del seed no cambian de comportamiento.
  - El alta (`POST /api/v1/ingredients`) valida cada valor contra `VALID_UNITS` → **400**.
  - El formulario de receta limita el `<select>` de unidades de cada fila a
    `default_unit` + las alternativas; con la whitelist de `harina` cargada
    (`g` + `kg`, `taza`) el selector baja de 9 opciones a 3.
  - La whitelist es editable después de crear el ingrediente:
    `POST /api/admin/ingredients/{id}/normalize` acepta `allowed_units` (con
    `mark_validated: false` para no validar de paso) y chequea cada valor
    contra `VALID_UNITS` → 400.
  - `VALID_UNITS`/`VALID_CATEGORIES` vivían duplicadas en `api/v1/endpoints/ingredients.py`
    y `schemas/recipe.py`; pasaron a `app/core/units.py` para que las rutas de admin y las
    públicas validen contra el mismo set.
  - `GET /api/v1/recipes/{slug}` anexa `default_unit` y `allowed_units` a cada fila de
    `ingredients`, así que **editar una receta existente también limita el `<select>`**.
    Lo absorbe `resolve_ingredient_catalog()` (antes `resolve_ingredient_names`), que ya
    hacía el lookup del catálogo para el `name`: un mismo `IN`, cero round trips extra.
    El JSONB sigue guardando sólo los cinco campos de siempre.
- **Stack de migraciones (Alembic) arrancado.** La 0001 (`8fcd65d6eddf`) recrea el schema
  completo de 18 tablas y se aplicó con `alembic stamp` sobre la base existente; la 0002
  (`1ac179e903af`) agrega `allowed_units`. `alembic.ini` y `env.py` ahora leen
  `DATABASE_URL` del entorno, así que la app y las migraciones comparten una sola fuente
  de verdad.
  - Antes, la app dependía sólo de `Base.metadata.create_all`, que **crea tablas pero
    nunca altera las existentes**: no había forma de agregar una columna a una base viva.
  - Verificado que la base real coincide exactamente con los modelos (autogenerate con
    cero diffs) — no había derroga acumulada.
  - **Gotcha**: Alembic omite el `server_default` al generar un `ADD COLUMN NOT NULL`, y
    PostgreSQL lo rechaza sobre una tabla con filas (`contains null values`). La 0002 lo
    fija a mano en `'[]'::jsonb`; migró las 320 filas existentes sin errores.

### Fixed
- **`docs/ui/02-components.md` ya no contradice al filesystem.** El catálogo declaraba 38
  componentes y sólo 18 existían; además 9 componentes reales ni siquiera estaban
  catalogados. Verificado en ambas direcciones: 27 entradas en el filesystem, 27 en la
  doc.
  - **20 entradas marcadas `[no implementado]`** en vez de borradas: la especificación de
    `AdminTable`, `AdminLayout`, `FilterSidebar` y compañía es lo que hay que construir en
    Fase 3, y borrarla destruiría trabajo de diseño hecho. La convención queda documentada
    en el encabezado.
  - **9 entradas agregadas** (`Button`, `Input`, `AvatarDropdown`, `AlertDialog`,
    `ConfirmHost`, `RecipeForm`, `RecipeCardSkeleton`, `ReviewList`, `PublicProfile`), con
    las props que realmente exporta cada uno.
  - **3 marcadas `[sin uso]`**: `Alert`, `Toast` e `Input` existen pero ningún archivo del
    proyecto los importa.
  - La tabla de verificación decía que `Modal/Sheet` estaba completo; `Sheet` no existe.
    Quedó como `Dialog / AlertDialog`, que sí. También estaba duplicada la fila de
    `RecipeCard` y repetida la numeración de secciones (dos "10").
- **Brecha de seguridad: cuenta destruible con una sesión robada**. `POST /auth/deactivate` y
  `POST /auth/delete-account` no pedían nada más que un access token válido, así que cualquiera
  con una sesión secuestrada podía borrar una cuenta de forma irreversible. Ambos exigen ahora la
  contraseña actual (`password`, obligatorio) y responden **403 "Contraseña incorrecta"** si no
  coincide; sin el campo, **422**.
  - 403 y no 401: el caller **sí** está autenticado, lo que falla es la revalidación. Responder
    401 mandaría el mensaje equivocado y podría hacer que un cliente dispare un re-login.
  - `/perfil`: el diálogo de baja y el de eliminación piden la contraseña antes de confirmar.
    `confirmDialog()` sigue devolviendo un boolean para no tocar sus 7 call sites; se agregó
    `confirmPasswordDialog()` a la par, porque cambiar la firma a objeto haría que
    `if (!confirmed)` pasara siempre (un objeto es truthy) — fallo silencioso en siete lugares.
  - La frase exacta `"ELIMINAR MI CUENTA"` que pedía la doc original quedó **descartada**: la
    contraseña prueba identidad de forma inequívoca, y una frase la puede saber cualquiera que
    lea la pantalla.
  - Tests: los tres existentes mandan `password`; se suman `test_deactivate_requires_password`
    (422, la cuenta queda activa), `test_deactivate_rejects_wrong_password` (403) y
    `test_delete_account_rejects_wrong_password` (403, el email no se anonimiza).
- **Fase 2 (calidad de UI: typecheck y lint reales, datos normalizados)**
  - **`flor-de-bondiola` no se podía volver a guardar**: el seed dejaba la unidad como
    `kilos`/`gramos`, fuera de la whitelist `VALID_UNITS`, así que el `PATCH` devolvía **422**.
    Se normalizaron a `kg`/`g`.
  - **El mismo seed guardaba `ingredient_id` como slug** (`bondiola-de-cerdo`) en vez de UUID, y el
    `PATCH` fallaba con **422 `uuid_parsing`**. Se dieron de alta los tres ingredientes que el
    catálogo no tenía (`bondiola-de-cerdo`, `ajos`, `roon`) y se resolvieron los ids. Ya no queda
    ningún `ingredient_id` no-UUID en la base.
  - **El CTA "Limpiar filtros" del estado vacío de `/buscar` no limpiaba**: apuntaba a
    `href="/buscar"`, pero la página sólo lee la URL en `onMount`, que no se re-ejecuta al
    navegar al mismo path. `EmptyState` ahora acepta una acción como callback y `/buscar` le pasa
    `clearAll`.
  - `frontend/tsconfig.json` ahora extiende `./.svelte-kit/tsconfig.json` (antes lo redefinía
    completo con `paths` mal escritos sin `/*`), así que `pnpm run check` **por fin funciona**.
    Pasó de 135 errores —la mayoría falsos positivos por resolución de módulos rota— a **0**.
  - `Button` aceptaba `variant="primary"` en la plantilla pero no en la unión de tipos, y
    `class:btn` apuntaba a una variable inexistente: el componente no renderizaba clases base.
  - `RecipeGrid` usaba `bind:this` sobre una **action** (`setSentinel`), que es `use:setSentinel`.
  - `Alert.svelte` tenía un `<div>` raíz sin cerrar y un import nombrado de un default export;
    `Toast.svelte` aplicaba con `@apply` clases que no son utilidades de Tailwind
    (`animate-in` es custom de `app.css`, `slide-in-from-top-2` viene de `tailwindcss-animate`,
    que no está instalado), así que su animación nunca corrió. Ambos componentes están
    **sin importar en ninguna parte** — el build nunca los compiló, que es por qué no rompían.
  - `apiFetch` se usaba sin import en 6 archivos (ver arriba, commit separado).
  - `replace: true` → `replaceState` en `/buscar`; tipos de `CategoryFilter` y de
    `RecipeForm.initial` (`Partial<Recipe>`); `toRecipe()` de `/recetas/generar` casteaba
    números sin validar y no completaba `Tag.usage_count`.
- **Fase 1 (reglas de negocio mal implementadas o mal documentadas)**
  - **Visitas anti-F5 (RB-04)**: `GET /recipes/{slug}` incrementaba `visit_count` en
    **cada** lectura, así que un F5 inflaba el contador. El conteo vive ahora solo en
    `POST /visits/{recipe_id}`, que deduplica por día calendario — por `user_id` si el
    visitante está logueado, por `visitor_fingerprint` si es anónimo. El detalle de la
    receta registra la visita una vez al montar.
  - **Filtro de ingredientes (RB-03/RB-16)**: con varios ingredientes seleccionados el
    filtro era **AND**, así que cualquier combinación realista devolvía 0 resultados.
    Ahora es **OR** entre ingredientes, como exigen las reglas; categoría, tags y texto
    siguen combinándose con AND.
  - **Favoritos (RB-05)**: la PK es `(user_id, recipe_id)`, pero el chequeo de duplicado
    también comparaba `collection_name`. Guardar una receta en una segunda colección
    pasaba el chequeo y reventaba en el INSERT como **500**. Ahora es un **400** que
    indica en qué colección ya está.
  - **Categoría en edición (RB-01)**: `PATCH /recipes/{slug}` aceptaba cualquier
    `category_id` sin verificar que exista y esté activa; ahora valida igual que el create.
  - **Slugs con acentos (RB-02b)**: `slugify()` conservaba acentos (`jalapeño` →
    `jalapeño`), produciendo URLs difíciles de copiar. Ahora normaliza a ASCII
    (`jalapeno`). Los slugs existentes no se migran.
  - **Compartir (RB-17)**: existía solo "Compartir" (Web Share API) sin alternativa de
    copiado y sin `utm_source`. Ahora hay botón **"Copiar link"** con feedback, y ambas
    vías generan `/receta/<slug>?utm_source=share`.
  - **Handle público (RB-17)**: faltaba `/u/<display_name_slug>`. El endpoint de perfil
    público resuelve UUID **o** `slugify(display_name)` ("Lucía Gómez" → `lucia-gomez`),
    y existe la ruta `/u/[slug]` reutilizando el mismo componente que `/usuario/[id]`.
  - Docs re-alineadas: RB-01, RB-02, RB-03, RB-04, RB-05, RB-08 (el upload de imágenes
    ya existía con whitelist de content-type y límite de 5MB), RB-11 (`amount`/`unit`
    son opcionales y `name` es requerido), RB-16, RB-17 e RB-ING-02 (ruta corregida).
- **Fase 0 (bloqueantes de seguridad y consistencia)**
  - `GET /recipes/{slug}` y `/{slug}/similar` ahora aplican la visibilidad de RB-09: una receta
    privada responde 404 a usuarios no autorizados (antes era legible por URL directa).
  - Los ingredientes de una receta se **validan contra el catálogo** (RB-ING-02): ingrediente
    inexistente/inactivo → 400, unidad fuera de `VALID_UNITS` o `amount <= 0` o ingrediente
    repetido → 422. Aplica en creación y edición.
  - Se eliminó el `get_current_user` duplicado de `auth.py`; ahora importa de `core.security`
    y valida `type=access`, por lo que un **refresh token ya no sirve como access token** (401).
  - Se eliminó el endpoint `POST /auth/bootstrap-admin` (el bootstrap idempotente corre en el
    lifespan; recrear el admin no debe ser invocable desde fuera).
  - **Refresh automático del access token**: `frontend/src/lib/api.ts` (`apiFetch`) y el `adminFetch`
    del panel reintentan una vez con el refresh cookie ante un 401, y `auth.init()` reintenta con
    el refresh antes de cerrar la sesión. Fin de las sesiones "fantasma" a los 15 minutos.
  - CTAs y links muertos del home (`/recipes`, `/recipes/new`) y del footer (páginas inexistentes)
    redirigidos a `/buscar` y `/recetas/nueva`.
  - `save_count` se muestra en el detalle de la receta (RF-04.6) y se mantiene sincronizado al
    guardar/quitar favoritos.
- `save_count` ahora se incrementa/decrementa al guardar/quitar favoritos (antes quedaba en 0).
- El buscador del home obtiene las **categorías desde la API** en vez de una lista hardcodeada.
- 10 bugs reales de endpoints detectados al escribir la suite de tests.
- Build del frontend por markup inválido en `CategoryFilter`/`TagAutocomplete`.
- Autocompletes apuntaban a endpoints inexistentes; `recipesStore` armaba mal los arrays de filtros.
- `MissingGreenlet` al sincronizar tags de una receta nueva; `{else}` inválido en Svelte.
- 404 de `/register` y de las rutas del menú (`/mis-recetas`, `/mis-favoritos`).

### Docs
- **Reescritura de la documentación de baja y eliminación de cuenta** para que describa el sistema
  real. La versión anterior pedía `password` en `/auth/deactivate` y `/auth/delete-account`, la
  frase exacta `"ELIMINAR MI CUENTA"`, un usuario **"system"** al que se transfería `author_id` y
  el nullado de favoritos/visitas/calificaciones. El código nunca hizo nada de eso — y la doc se
  contradecía a sí misma (US-06 AC4 anonimizaba `display_name` al desactivar, US-07 AC2 decía que
  el original se había perdido y US-07 AC3 decía que se restauraba).
  - `user-stories.md`: US-06, US-07 y US-08 reescriben sus criterios según el comportamiento
    observable; US-07 queda aclarada como reactivación **sólo por admin** (`/auth/reactivate`
    self-service no existe).
  - `authentication.md`: contratos corregidos — `{"delete_recipes": false}` y `{"confirm": true}`
    como requests, respuestas reales (`{"deactivated"|"deleted", "recipes_deleted"}`) y bad paths
    verificados (400 "Inactive user" vía `get_current_active_user`, 422 por Pydantic).
  - `business-rules.md`: RB-AUTH-08/09/10 con las reglas efectivas y la decisión de **descartar**
    el usuario "system" (anonimizar in place ya produce "Usuario eliminado" en la UI; nullar las
    claves foráneas sería destrucción de datos sin ganancia de privacidad, porque el email de la
    fila ya es aleatorio).
  - La re-autenticación con contraseña antes de destruir la cuenta queda marcada explícitamente
    como **brecha de seguridad** en los tres archivos, en vez de figurar como requisito cumplido.
  Motivo (ADR-000): un doc que se refuta a sí mismo no puede mandar sobre el código.
- `user-stories.md`: **US-03 (OAuth), US-08 (baja/eliminación), US-37 (IA) y US-38 (modo cocina)**
  figuraban como *Won't / [v2]* pero ya estaban implementadas y cubiertas por la suite; se movieron
  a Must para que la priorización describa el producto real (total 38 Must + 1 Should, ninguna
  diferida). `functional-requirements.md` y `business-rules.md` documentan RF-12.5/RF-12.3 como
  implementados y RF-12.8 como pendiente de arrancar el stack de migraciones (0 versiones en
  `backend/alembic/versions/`).
- `docs/decisions/ADR-000-source-of-truth.md` (la documentación como fuente de verdad).
- Requisitos (RF/RB), visión, dominio, UI (páginas, componentes, design system),
  casos de uso (`search`, `ingredients`, `admin`, `notifications`), testing y este CHANGELOG.

### Tests
- Suite de endpoints con Postgres real (`recetario_test`) y `ASGITransport`: **197 tests** verdes,
  incluidos notificaciones (preferencias/email/Web Push), administración v2, OAuth/reset/refresh,
  IA (gating), seed del catálogo e integración de Socket.IO. La Fase 0 suma regresiones de
  visibilidad por slug, validación de ingredientes y rechazo del refresh token como access token;
  la Fase 1 cubre la deduplicación de visitas, el filtro OR de ingredientes, el 400 de
  favoritos duplicados, el handle público `/u/<slug>` y los slugs sin acentos.
