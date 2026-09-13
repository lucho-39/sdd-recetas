# Definición de Pantallas (Pages)

> Especificación detallada de cada pantalla: layout, componentes, estados, responsive, a11y.

---

## 1. Home — `/` (Página Principal)

### Layout General

```
┌─────────────────────────────────────────────────────────────┐
│  NAVBAR (fixed top, z-50)                                   │
│  ┌─────────────┐                          ┌──────────────┐  │
│  │ Logo        │                          │ Acciones     │  │
│  │ "Recetas    │                          │ (según auth) │  │
│  │  App"       │                          │              │  │
│  └─────────────┘                          └──────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  HERO (section, py-16 md:py-24)                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  "Donde cada ingrediente cuenta una historia"           ││
│  │  Subtítulo opcional                                     ││
│  └─────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────┤
│  BUSCADOR (sticky top-16, z-40, bg-background/80 backdrop) │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ [Buscar por nombre, ingrediente...]  [Filtros ▼]  [✕]  ││
│  │ Chips activos: Categoría: Postre ✕  Tag: Vegano ✕       ││
│  └─────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────┤
│  GRID RECETAS (section, py-8, container max-w-7xl)          │
│  ┌─────────┬─────────┬─────────┬─────────┐  (grid responsive)│
│  │ Card 1  │ Card 2  │ Card 3  │ Card 4  │                  │
│  ├─────────┼─────────┼─────────┼─────────┤                  │
│  │ Card 5  │ Card 6  │ ...                    │                  │
│  └─────────┴─────────┴─────────┴─────────┘                  │
│  [Cargar más / Infinite Scroll]                              │
└─────────────────────────────────────────────────────────────┘
```

---

### Navbar (`components/layout/Navbar.svelte`)

**Props**: `user?: User | null`

**Estados**:
- **No autenticado**: Logo + `Login` (ghost) + `Registrarse` (primary)
- **Autenticado**: Logo + `Mis Recetas` + `Mis Favoritos` + `Avatar` (dropdown: Perfil, Configuración, Cerrar sesión)
- **Admin** (si `user.role === 'admin'`): + `Admin` link (abre admin.en subdominio/nueva pestaña)

**Responsive**:
- `< md`: Hamburger menu (Sheet/Drawer) con mismos links
- Logo siempre visible, actions colapsan en móvil

**Accesibilidad**:
- `role="navigation"`, `aria-label="Navegación principal"`
- Focus visible en todos los links
- Skip link: `<a href="#main-content" class="sr-only focus:not-sr-only">Saltar al contenido</a>`

---

### Hero (`components/home/Hero.svelte`)

**Contenido**:
```html
<section class="py-16 md:py-24 px-4 text-center" aria-labelledby="hero-title">
  <div class="max-w-3xl mx-auto">
    <h1 id="hero-title" class="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight text-foreground">
      Donde cada ingrediente cuenta una historia
    </h1>
    <p class="mt-4 text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto">
      Descubre, guarda y cocina las mejores recetas. 
      Tu cocina, tus reglas.
    </p>
  </div>
</section>
```

**Responsive**: Padding reduce en móvil, tipografía escala fluidamente (`clamp()`).
**Dark mode**: Colores `foreground`/`muted-foreground` automáticos.

---

### Buscador (`components/home/SearchBar.svelte`)

**Props**: `initialFilters?: SearchFilters`, `onSearch: (filters) => void`, `onClear: () => void`

**Layout**:
```
┌─────────────────────────────────────────────────────────────┐
│  [Buscar por nombre, ingrediente...          ] [Filtros ▼]  │
│  ─────────────────────────────────────────────────────────  │
│  Chips activos: [Postre ✕] [Vegano ✕] [Pollo ✕] [Limpiar]  │
└─────────────────────────────────────────────────────────────┘
```

**Componentes internos**:
- `SearchInput`: Debounce 300ms, placeholder dinámico, icon lupa, clear button
- `FilterTrigger`: Button `variant="outline"` + ChevronDown, abre `FilterSidebar` (Sheet en móvil, Popover en desktop)
- `ActiveFiltersChips`: Solo visible si hay filtros; cada chip con `✕` para quitar individual; botón "Limpiar todo"

**Estados**:
- **Vacío**: Solo input + trigger filtros
- **Con filtros**: Chips visibles debajo, sticky mantiene altura
- **Cargando**: Spinner en input, disable interactions

**Responsive**:
- `< md`: Input full width, trigger abre Sheet (filtros fullscreen)
- `≥ md`: Input flex-1, trigger Popover (ancho 320px), chips en fila wrap

**Accesibilidad**:
- `label` asociado al input (visualmente oculto si placeholder)
- `aria-expanded` en trigger filtros
- Chips: `role="button"`, `aria-label="Quitar filtro Categoría: Postre"`

---

### Grid Recetas (`components/home/RecipeGrid.svelte`)

**Props**: `recipes: Recipe[]`, `loading?: boolean`, `onLoadMore?: () => void`, `hasMore?: boolean`

**Grid Responsive**:
```css
grid-template-columns: 
  1fr;                    /* base (< 640px) */
  repeat(2, 1fr);         /* sm: 640px */
  repeat(3, 1fr);         /* md: 768px */
  repeat(4, 1fr);         /* lg: 1024px */
gap: 1.5rem;              /* gap-6 */
```

**Estados**:
- **Loading**: 8 `RecipeCardSkeleton` (shimmer animation)
- **Vacío**: `EmptyState` ilustrado + sugerencias (ver `EmptyState.svelte`)
- **Error**: `ErrorState` + botón "Reintentar"
- **Cargando más**: Skeleton solo en nuevos items (append)

**Infinite Scroll**: `IntersectionObserver` en sentinel (última card) → `onLoadMore()`

---

### RecipeCard (`components/recipe/RecipeCard.svelte`)

**Props**: `recipe: Recipe`, `onClick?: () => void`

**Estructura**:
```
┌─────────────────────────────────────┐
│  Imagen (aspect-[4/3], object-cover)│  ← placehold.co/400x400
│  ┌───────────────────────────────┐  │
│  │ [Badge Categoría] [Tag ✕]      │  │  ← Badge usa category.color
│  └───────────────────────────────┘  │
├─────────────────────────────────────┤
│  Título (2 líneas max, truncate)    │
│  ⭐ 4.7 (128)    📖 1.2k   👤 Autor │  ← Rating fraccional + contadores
└─────────────────────────────────────┘
```

**Detalles visuales**:
- **Imagen**: `placehold.co/400x400/{color}/{color}?text={slug}` — color dinámico basado en categoría (o gris neutro)
- **Badge Categoría**: `CategoryBadge` — `variant="outline"`, `style="background: {color}; border: {color}; color: white"`
- **Tags**: Máx 2 visibles + `+N` si más (tooltip con lista completa)
- **Rating**: `RatingStars` — fill % = `(avg_rating % 1) * 100` para estrella fraccional
- **Contadores**: `save_count` (icono bookmark), `visit_count` (icono eye) — formato compacto (1.2k, 5.3M)
- **Autor**: Avatar (fallback iniciales) + nombre truncado

**Estados**:
- **Hover**: `shadow-lg`, `scale-[1.02]`, `transition-shadow transition-transform`
- **Focus-visible**: Ring `primary` (accesibilidad teclado)
- **Loading**: `RecipeCardSkeleton` (shimmer en imagen, líneas en texto)

**Click**: Navega a `/receta/{recipe.slug}` (router.push)

**Accesibilidad**:
- `article` wrapper, `tabindex=0`, `role="button"` si `onClick`
- `aria-label="Ver receta: {title}"`
- Imagen: `alt="Receta: {title}"` (no "imagen de")

---

### EmptyState (`components/common/EmptyState.svelte`)

**Variants**: `search`, `favorites`, `recipes`, `generic`

**Ejemplo Search**:
```html
<div class="py-16 text-center">
  <Illustration class="mx-auto mb-4 text-muted-foreground" />
  <h2 class="text-xl font-semibold">No hay recetas con esos filtros</h2>
  <p class="mt-2 text-muted-foreground">Prueba quitar algún filtro o busca "pollo"</p>
  <div class="mt-6 flex gap-2 justify-center flex-wrap">
    <Button variant="outline" on:click={() => clearFilter('category')}>Quitar categoría</Button>
    <Button variant="outline" on:click={() => clearFilter('tags')}>Quitar tags</Button>
    <Button variant="outline" on:click={() => clearFilter('ingredients')}>Quitar ingredientes</Button>
    <Button on:click={clearAll}>Ver todas las recetas</Button>
  </div>
</div>
```

---

## 2. Detalle Receta — `/receta/:slug`

### Layout

```
┌─────────────────────────────────────────────────────────────┐
│  NAVBAR                                                      │
├─────────────────────────────────────────────────────────────┤
│  BREADCRUMB: Inicio / Categoría / Título receta              │
├─────────────────────────────────────────────────────────────┤
│  DETALLE (container max-w-4xl, py-8)                         │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Imagen hero (aspect-[16/9], w-full, object-cover)       ││
│  │ Badge Categoría (esquina sup-izq)                        ││
│  └─────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Título + Acciones (Compartir, Guardar, Cocinar)         ││
│  │ Meta: Autor · Categoría · Tags · Tiempo · Porciones     ││
│  │ Rating: ⭐ 4.7 ★★★★☆ (128)  📖 1.2k  👁 5.4k            ││
│  └─────────────────────────────────────────────────────────┘│
│  ┌─────────────────────┬───────────────────────────────────┐│
│  │ INGREDIENTES        │ INSTRUCCIONES                       ││
│  │ ┌─────────────────┐ │ 1. Primer paso...                  ││
│  │ │ 🥕 500g Zanahoria│ │ 2. Segundo paso...                 ││
│  │ │ 🧅 1 Cebolla     │ │ 3. ...                             ││
│  │ │ 🥩 300g Carne    │ │                                    ││
│  │ └─────────────────┘ │ [Modo Cocinando ▶]                 ││
│  └─────────────────────┴───────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────┐│
│  │ CALIFICACIONES Y RESEÑAS                                ││
│  │ ⭐ 4.7 ★★★★☆ (128)  [Distribución barras 5★→1★]         ││
│  │ [Escribir reseña]                                       ││
│  │ Lista paginada reseñas...                               ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

**Componentes clave**: `RecipeHero`, `RecipeMeta`, `IngredientList`, `InstructionSteps`, `RatingSection`, `RatingStars` (fraccional), `CookingModeTrigger`.

**Autor**: el nombre del autor es un **enlace** a su perfil público `/usuario/:id`.

**Modo Cocinando**: Botón "Cocinar" → abre `/cooking/:slug` (pantalla completa, wake lock).

---

## 3. Búsqueda — `/buscar`

### Layout (Sidebar + Grid)

```
┌─────────────────────────────────────────────────────────────┐
│  NAVBAR                                                      │
├─────────────────────────────────────────────────────────────┤
│  <aside class="w-72 md:w-80 lg:w-96 border-r">             │
│    FILTROS (sticky top-16, h-[calc(100vh-4rem)], overflow) │
│    ┌─────────────────────────────────────────────────────┐  │
│    │ 🔍 Buscar: [______________]                         │  │
│    ├─────────────────────────────────────────────────────┤  │
│    │ Categoría: (radio group)                            │  │
│    │ ☐ Postre    ☐ Entrada    ☐ Snack    ...             │  │
│    ├─────────────────────────────────────────────────────┤  │
│    │ Tags: [TagAutocomplete]  Chips: [Vegano ✕] [Sin TACC]│  │
│    ├─────────────────────────────────────────────────────┤  │
│    │ Ingredientes: [IngredientAutocomplete] Chips...     │  │
│    ├─────────────────────────────────────────────────────┤  │
│    │ [Limpiar todo]                                      │  │
│    └─────────────────────────────────────────────────────┘  │
│  </aside>                                                   │
│  <main class="flex-1">                                      │
│    Toolbar: Ordenar [Recientes ▼]  Vista [Grid ▼]  1,234   │
│    GRID RECETAS (mismo RecipeGrid)                          │
│  </main>                                                    │
└─────────────────────────────────────────────────────────────┘
```

**Responsive**: `< lg`: Sidebar en Sheet (Drawer) activado por botón "Filtros" en toolbar.

---

## 4. Autenticación

### `/login` — Login
- Email + Password + "Recordarme" (extend refresh a 60d)
- OAuth: Google, GitHub (buttons con iconos)
- "¿Olvidaste tu contraseña?" → `/forgot-password`
- "¿No tienes cuenta?" → `/register`
- **Redirect**: `returnTo` query param → post-login navega allí

### `/register` — Registro
- Email, Display Name, Password (validación visual strength meter), Confirm Password
- Checkbox "Acepto términos" (link modal)
- Submit → envía email verificación → "Revisa tu bandeja"

### `/forgot-password` / `/reset-password`
- Email → envía token 1h
- Token válido → form nuevo password (strength meter) + confirm
- Success → login automático + JWT pair

### `/verify-email`
- Token en query → verifica → login automático

---

## 5. Perfil Usuario

### `/perfil` (Autenticado, privado)
- **Header**: foto de perfil (editable por el usuario), `display_name` (editable),
  email y **"Miembro desde"** = `created_at` de la cuenta.
- **Acciones**: el usuario puede cambiar su `display_name` y su avatar.
- **Mis recetas**: lista de **todas las recetas creadas por el usuario**,
  obtenidas de la base de datos (`GET /api/v1/users/me/recipes`).
- **Al final**: cambiar contraseña, darse de baja (soft delete) y eliminar cuenta.
- **NO** mostrar la fecha del último login ni la sección de "últimas sesiones"
  (información no relevante para el usuario).

### `/usuario/:id` (Público)
- **Header**: foto de perfil, `display_name` y **"Miembro desde"** (`created_at`).
- **Grid**: recetas **públicas** del autor (paginado) — `GET /api/v1/users/:id/recipes`.
- **NO** mostrar email, favoritos, ratings dados ni métricas privadas
  (RB-17, RF-11.3).
- Botón "Compartir perfil" (Web Share API).

> El **nombre del autor** en el detalle de una receta es un **enlace** a
> `/usuario/:id`.

---

## 6. Mis Recetas — `/mis-recetas`

### Tabs: Publicadas | Privadas | Borradas
- Tabla/Grid con filtros: búsqueda título, categoría, estado
- Acciones por fila: Editar, Toggle público/privado, Borrar/Restaurar
- Empty state por tab

---

## 6. Favoritos — `/mis-favoritos`

### Sidebar: Lista colecciones (Favoritos + custom)
- Click colección → grid recetas (mismo RecipeGrid)
- Header colección: nombre + contador + acciones (renombrar, borrar)
- Vacío: CTA "Empieza a guardar recetas"

---

## 7. Modo Cocinando — `/cooking/:slug`

### Fullscreen (PWA install prompt si no instalada)
```
┌─────────────────────────────────────────────────────────────┐
│  [✕ Salir]                    [⚙ Ajustes] [🔊 Voz]          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    PASO 3 DE 7                              │
│                                                             │
│         "Dora la carne en aceite caliente..."              │
│                                                             │
│    ◀ Anterior                    Siguiente ▶               │
│                                                             │
│    ⏱ Timer: 5:00  [Iniciar] [Pausar] [Reset]              │
└─────────────────────────────────────────────────────────────┘
```

**Features**: Wake Lock API, swipe izq/der, comandos voz ("siguiente", "anterior", "repite"), timer por paso, pantalla siempre activa.

---

## 8. Admin (Proyecto Separado — `recetario-admin`)

Ver `docs/use-cases/admin.md` para casos de uso y estado de la API.

**Estilo**: más **sobrio y simple** que el frontend, pero **consistente** en todo
el panel (misma paleta/tipografía base, radios y sombras mínimos). Tablas y
formularios directos, sin ornamentos.

**Layout**:
- **Aside izquierdo** fijo con la navegación; **colapsable** a solo iconos
  (preferencia persistida en `localStorage`).
- **Header superior** con el `display_name` del usuario logueado y botón
  **Cerrar sesión**.
- **Dashboard** (`/`): cards con estadísticas reales (usuarios, recetas,
  ingredientes, categorías, tags, calificaciones, visitas) desde
  `GET /api/admin/metrics/dashboard`.

**Secciones** (listar, buscar, filtrar, ver detalle, editar, eliminar según corresponda):
- `/usuarios` → tabla, filtros por estado, activar/desactivar, cambiar rol.
- `/recetas` → tabla, filtros por estado, ocultar/publicar, soft delete.
- `/ingredientes` → tabs Pendientes / Validados / Rechazados; validar,
  rechazar (con razón) y normalizar.
- `/categorias` → CRUD (elimina si no tiene recetas; si no, desactiva).
- `/tags` → CRUD.

**Pendiente (v2)**: `/admin/metricas`, `/admin/config` (flags, rate limits,
email templates, mantenimiento) y `/admin/audit-log`.

---

## Estados Comunes (Todas las páginas)

| Estado | Componente | Descripción |
|--------|------------|-------------|
| **Loading** | `Skeleton` | Shimmer animation, misma estructura que contenido |
| **Error** | `ErrorState` | Icono, mensaje, botón "Reintentar" / "Volver" |
| **Error de Red** | `Alert` (shadcn) | **Destructive variant** — Banner toast superior: "Error de conexión. Reintentando..." + botón "Reintentar ahora" |
| **Error 404** | `ErrorState` + `Alert` | Página 404 temática + toast destructive "Página no encontrada" |
| **Error 5xx** | `Alert` (shadcn) | **Destructive variant** — Toast persistente: "Error del servidor. Nuestro equipo ya fue notificado." |
| **Vacío** | `EmptyState` | Ilustración SVG, mensaje accionable, CTAs |
| **Offline** | `OfflineBanner` | Fixed bottom, "Modo offline: solo recetas guardadas" |
| **Unauthorized** | `AuthGate` | Redirige a `/login?returnTo=...` con toast |

---

## Estados Vacíos por Página (Detalle)

| Página / Contexto | Componente | Ilustración | Mensaje | CTA(s) |
|-------------------|------------|-------------|---------|--------|
| **Detalle receta no encontrada** (`/receta/:slug` 404) | `EmptyState` + `Alert` | 🍪 Galleta rota | "Esta receta se perdió en el horno. La página que buscas no existe o se quemó." | "Volver al inicio" (primary), "Buscar recetas" (outline) |
| **Detalle receta eliminada** (`deleted_at` not null) | `EmptyState` + `Alert` | 🗑️ Papelera | "Esta receta fue eliminada. El autor la removió de la plataforma." | "Volver al inicio" (primary), "Explorar recetas" (outline) |
| **Detalle receta privada** (`is_public=false` + no autor) | `EmptyState` + `Alert` | 🔒 Candado | "Esta receta es privada. Solo el autor puede verla." | "Volver al inicio" (primary), "Iniciar sesión" (outline) |
| **Perfil usuario no encontrado** (`/usuario/:id` 404) | `EmptyState` + `Alert` | 👤 Usuario fantasma | "Este chef no existe. El perfil que buscas no existe o fue eliminado." | "Volver al inicio" (primary), "Explorar chefs" (outline) |
| **Mis recetas - Sin recetas** (tab vacía) | `EmptyState` | 🍳 Chef | "Tu cocina está vacía. Aún no has creado recetas." | "Crear primera receta" (primary) |
| **Mis favoritos - Vacío** | `EmptyState` | 🤍 Corazón vacío | "Tu despensa está vacía. Aún no has guardado recetas." | "Explorar recetas" (primary) |
| **Búsqueda sin resultados** | `EmptyState` + `Alert` | 🔍 Lupa + ? | "No hay recetas con esos filtros. Prueba ampliar tu búsqueda." | "Quitar filtros" (outline), "Ver todas" (primary) |
| **Admin - Sin resultados** (cualquier tabla) | `EmptyState` | 📋 Clipboard | "No hay elementos para mostrar." | "Crear nuevo" (primary) |
| **Modo offline** (cualquier página) | `OfflineBanner` (fixed bottom) | 📶 WiFi tachado | "Modo offline: solo recetas guardadas disponibles." | — |

---

## Alertas de Red (shadcn `Alert` — Variante `destructive`)

| Situación | Componente | Variante | Posición | Comportamiento |
|-----------|------------|----------|----------|----------------|
| **Error de fetch** (network error, timeout) | `Alert` | `destructive` | Toast superior (`top-right`) | Auto-dismiss 6s + botón "Reintentar ahora" |
| **Error 5xx** (server error) | `Alert` | `destructive` | Toast superior + persistente | No auto-dismiss, botón "Reintentar", enlace "Reportar" |
| **Error 401/403** (auth expired) | `Alert` | `destructive` | Toast superior | Auto-redirect a `/login?returnTo=...` tras 3s |
| **Error 404** (página no existe) | `Alert` | `destructive` | Toast superior + página 404 | Auto-dismiss 6s |
| **Error validación** (422) | `Alert` | `destructive` | Inline (debajo del form) | No auto-dismiss, desaparece al corregir |
| **Offline detectado** | `Alert` | `warning` | Toast inferior | "Modo offline: funcionalidad limitada" |

### Implementación shadcn `Alert` (Destructive)

```svelte
<!-- components/ui/Alert.svelte -->
<script lang="ts">
  import { IconX as X } from '@tabler/icons-svelte';
  export let variant: 'default' | 'destructive' | 'warning' = 'default';
  export let title: string;
  export let description: string;
  export let action?: { label: string; onClick: () => void };
  export let dismissible = true;
  export let onDismiss?: () => void;
</script>

<div 
  class="relative w-full rounded-lg border p-4 
    bg-background text-foreground
    data-[variant=destructive]:border-destructive/50 data-[variant=destructive]:bg-destructive/10 data-[variant=destructive]:text-destructive
    data-[variant=warning]:border-warning/50 data-[variant=warning]:bg-warning/10 data-[variant=warning]:text-warning
    animate-fade-in"
  role="alert"
  aria-live="polite"
>
  <div class="flex items-start gap-3">
    {#if variant === 'destructive'}
      <AlertCircle class="w-5 h-5 shrink-0" />
    {:else if variant === 'warning'}
      <AlertTriangle class="w-5 h-5 shrink-0" />
    {:else}
      <Info class="w-5 h-5 shrink-0" />
    {/if}
    <div class="flex-1 min-w-0">
      <h4 class="font-medium">{title}</h4>
      <p class="text-sm opacity-90 mt-1">{description}</p>
    </div>
    {#if action}
      <Button variant="outline" size="sm" on:click={action.onClick}>
        {action.label}
      </Button>
    {/if}
    {#if dismissible}
      <button 
        class="absolute top-2 right-2 p-1 hover:bg-accent rounded"
        on:click={onDismiss}
        aria-label="Cerrar"
      >
        <X class="w-4 h-4" />
      </button>
    {/if}
  </div>
</div>
```

### CSS Tokens para Alert Destructive (Tailwind)

```js
// tailwind.config.js - extend colors
colors: {
  destructive: {
    DEFAULT: '#B84A3A',      // warm red
    hover: '#A03A2A',
    foreground: '#FAF9F6',   // warm off-white
    light: '#FEF2F2',        // bg for alert
    border: '#FECACA',       // border
  },
}
```

---

## Implementación Toast Network Error (Ejemplo)

```typescript
// stores/toast.ts
import { toast } from 'svelte-sonner';

export function showNetworkError(retryAction?: () => void) {
  toast.error('Error de conexión', {
    description: 'No pudimos conectar con el servidor. Verifica tu conexión.',
    action: retryAction ? {
      label: 'Reintentar ahora',
      onClick: retryAction
    } : undefined,
    duration: 6000,
    className: 'bg-destructive/10 border-destructive/50 text-destructive',
  });
}

export function showServerError(retryAction?: () => void) {
  toast.error('Error del servidor', {
    description: 'Algo salió mal. Nuestro equipo ya fue notificado.',
    action: retryAction ? {
      label: 'Reintentar',
      onClick: retryAction
    } : undefined,
    duration: 0, // persistente
    className: 'bg-destructive/10 border-destructive/50 text-destructive',
  });
}
```