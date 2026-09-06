# Especificación de Componentes

> Catálogo completo de componentes: props, estados, variants, a11y, testing.

---

## 1. Layout & Navigation

### Navbar (`components/layout/Navbar.svelte`)

**Props**:
```typescript
interface NavbarProps {
  user: User | null;           // null = no autenticado
  returnTo?: string;           // para redirect post-login
}
```

**Slots**: `default` (acciones custom), `logo` (override logo)

**Estados**:
| Estado | Qué muestra |
|--------|-------------|
| `user === null` | Logo + `Login` (ghost) + `Registrarse` (primary) |
| `user.role === 'user'` | Logo + `Mis Recetas` + `Mis Favoritos` + `AvatarDropdown` |
| `user.role === 'admin'` | + `Admin` link (target="_blank" rel="noopener") |

**AvatarDropdown** (DropdownMenu):
- Avatar (fallback iniciales) + display_name
- Items: Perfil (`/perfil`), Configuración, Divider, Cerrar sesión
- `role="menu"`, `aria-label="Menú de usuario"`

**Responsive**:
- `< md`: Hamburger button → Sheet (Drawer right) con misma estructura
- Breakpoint: `md` (768px)

**A11y**:
- `<nav role="navigation" aria-label="Navegación principal">`
- Skip link: `<a href="#main" class="sr-only focus:not-sr-only">Saltar al contenido</a>`
- Focus trap en Sheet móvil
- `aria-expanded` en hamburger button

---

### Footer (`components/layout/Footer.svelte`)

**Contenido**: Links legales, redes sociales, versión, copyright
**Responsive**: Stack vertical en móvil, horizontal en desktop
**Variant**: `minimal` (solo copyright) para páginas auth

---

### Breadcrumb (`components/layout/Breadcrumb.svelte`)

**Props**: `items: { label: string; href?: string }[]`
**Auto-generado**: Desde router (basado en ruta actual)
**A11y**: `nav aria-label="Ruta de navegación"`, `ol` + `li` + `aria-current="page"` en último

---

## 2. Home Components

### Hero (`components/home/Hero.svelte`)

**Props**:
```typescript
interface HeroProps {
  title?: string;           // default: "Donde cada ingrediente cuenta una historia"
  subtitle?: string;        // opcional
  cta?: { label: string; href: string }; // opcional
  illustration?: boolean;   // default false
}
```

**Variants**: `centered` (default), `split` (texto izq, imagen der - ≥ lg)

**A11y**: `<section aria-labelledby="hero-title">`, `h1#hero-title`

---

### SearchBar (`components/home/SearchBar.svelte`)

**Props**:
```typescript
interface SearchBarProps {
  initialFilters?: SearchFilters;
  onSearch: (filters: SearchFilters) => void;
  onClear: () => void;
  loading?: boolean;
}
```

**Sub-componentes**:
- `SearchInput`: `input[type="search"]` + debounce 300ms + clear button + loading spinner
- `FilterTrigger`: Button + ChevronDown → abre `FilterSidebar` (Sheet móvil) / `FilterPopover` (desktop)
- `ActiveFiltersChips`: Solo si `filters.hasAny()` → chips removibles + "Limpiar todo"

**FilterSidebar** (Sheet móvil / Popover desktop):
- Tabs: Categoría, Tags, Ingredientes
- Cada tab: componente dedicado (ver abajo)

**A11y**:
- `label` en input (sr-only si placeholder)
- `aria-expanded` en trigger
- `aria-label` en chips de eliminación
- Focus trap en Sheet

---

### CategoryFilter (`components/search/CategoryFilter.svelte`)

**Props**: `selected?: string`, `onChange: (slug: string) => void`, `categories: Category[]`

**UI**: Radio group (solo una selección) + icon + nombre
**Empty state**: "Todas las categorías" (value="")

---

### TagAutocomplete (`components/search/TagAutocomplete.svelte`)

**Props**:
```typescript
interface TagAutocompleteProps {
  selected: string[];           // slugs seleccionados
  onChange: (slugs: string[]) => void;
  placeholder?: string;
  maxTags?: number;             // default 10
}
```

**Behavior**:
- Debounce 200ms → `GET /api/tags/autocomplete?q=`
- Sugerencias: `name` + `category` (ej: "Vegano · Dieta") + `usage_count` badge
- Selección: click/Enter → agrega chip, limpia input, mantiene foco
- Crear nuevo: si no hay match + Enter → "Crear 'texto'" → POST `/api/tags` → agrega

**Chip seleccionado**: `{name} ✕` → click ✕ → `onChange` sin ese slug

---

### IngredientAutocomplete (`components/search/IngredientAutocomplete.svelte`)

**Similar a TagAutocomplete** pero:
- Busca en catálogo 300 items (`GET /api/ingredients/autocomplete?q=`)
- Sugerencia muestra: nombre, categoría, unidad por defecto
- Selección → chip con cantidad + unidad (ver `IngredientChip`)

---

### ActiveFiltersChips (`components/search/ActiveFiltersChips.svelte`)

**Props**: `filters: SearchFilters`, `onRemove: (key: string, value?: string) => void`, `onClearAll: () => void`

**Render**: Grupo de chips por dimensión (categoría, tags, ingredientes) + botón "Limpiar todo"

---

### RecipeGrid (`components/recipe/RecipeGrid.svelte`)

**Props**:
```typescript
interface RecipeGridProps {
  recipes: Recipe[];
  loading?: boolean;
  onLoadMore?: () => void;
  hasMore?: boolean;
  emptyVariant?: 'search' | 'favorites' | 'recipes';
}
```

**Grid CSS**:
```css
display: grid;
grid-template-columns: 1fr;                    /* base */
grid-template-columns: repeat(2, 1fr);         /* sm */
grid-template-columns: repeat(3, 1fr);         /* md */
grid-template-columns: repeat(4, 1fr);         /* lg */
gap: 1.5rem; /* gap-6 */
```

**Infinite Scroll**: `IntersectionObserver` en sentinel (div después de última card) → `onLoadMore()`

**Estados**:
- `loading` + `recipes.length === 0` → 8 `RecipeCardSkeleton`
- `loading` + `recipes.length > 0` → append skeletons al final
- `!loading` + `recipes.length === 0` → `EmptyState` (variant según contexto)
- `error` → `ErrorState` + botón reintentar

---

## 3. Recipe Components

### RecipeCard (`components/recipe/RecipeCard.svelte`)

**Props**:
```typescript
interface RecipeCardProps {
  recipe: Recipe;
  variant?: 'default' | 'compact';  // compact: sin imagen, para listas densas
  onClick?: () => void;
}
```

**Estructura**:
```
<article class="group relative flex flex-col h-full bg-card rounded-xl overflow-hidden 
                transition-shadow hover:shadow-lg hover:scale-[1.02] 
                focus-visible:ring-2 focus-visible:ring-primary focus-visible:outline-none">
  <!-- Imagen -->
  <div class="aspect-[4/3] w-full overflow-hidden bg-muted">
    <img src={imageUrl} alt={`Receta: ${recipe.title}`} 
         class="w-full h-full object-cover transition-transform group-hover:scale-105"
         loading="lazy" />
    <!-- Badge Categoría (esquina sup-izq) -->
    <CategoryBadge category={recipe.category} class="absolute top-2 left-2 z-10" />
  </div>

  <!-- Contenido -->
  <div class="flex-1 flex flex-col p-4 space-y-3">
    <!-- Tags (máx 2 + +N) -->
    <div class="flex flex-wrap gap-1.5">
      {#each recipe.tags.slice(0, 2) as tag}
        <TagChip tag={tag} />
      {/each}
      {#if recipe.tags.length > 2}
        <TagChip label={`+${recipe.tags.length - 2}`} variant="outline" />
      {/if}
    </div>

    <!-- Título -->
    <h3 class="font-semibold text-lg line-clamp-2 group-hover:text-primary transition-colors">
      {recipe.title}
    </h3>

    <!-- Meta: Rating + Contadores + Autor -->
    <div class="flex items-center gap-3 text-sm text-muted-foreground flex-wrap">
      <RatingStars 
        value={recipe.avg_rating} 
        count={recipe.rating_count} 
        size="sm" 
        showCount 
      />
      <span class="flex items-center gap-1">
        <BookmarkIcon class="w-4 h-4" /> {formatNumber(recipe.save_count)}
      </span>
      <span class="flex items-center gap-1">
        <EyeIcon class="w-4 h-4" /> {formatNumber(recipe.visit_count)}
      </span>
      <AuthorAvatar author={recipe.author} size="sm" />
    </div>
  </div>
</article>
```

**Imagen**: `placehold.co/400x400/{color}/{color}?text={slug}` — color = `category.color` (o gris neutro)

**Variants**:
- `default`: Card completa con imagen (grid home, búsqueda)
- `compact`: Sin imagen, horizontal, para listas (mis recetas, favoritos)

**A11y**:
- `article` + `tabindex=0` + `role="button"` si `onClick`
- `aria-label="Ver receta: {title}"`
- `focus-visible:ring-2 focus-visible:ring-primary`
- Imagen: `alt="Receta: {title}"`

---

### CategoryBadge (`components/recipe/CategoryBadge.svelte`)

**Props**: `category: Category`, `variant?: 'outline' | 'solid'`, `size?: 'sm' | 'md' | 'lg'`

**Estilo**:
```svelte
<Badge 
  variant={variant === 'solid' ? 'default' : 'outline'} 
  class={`
    font-medium gap-1
    ${variant === 'outline' 
      ? `bg-transparent border-[${category.color}] text-white 
         [&>svg]:stroke-[${category.color}]` 
      : `bg-[${category.color}] text-white`}
    ${size === 'sm' ? 'px-2 py-0.5 text-xs' : size === 'lg' ? 'px-3 py-1 text-base' : 'px-2.5 py-0.5 text-sm'}
  `}
>
  {category.icon} {category.name}
</Badge>
```

**Colores**: Usa `category.color` (Hex) directo en `style` o CSS custom property `--badge-color`

---

### TagChip (`components/recipe/TagChip.svelte`)

**Props**: `tag: Tag` | `{ label: string }`, `variant?: 'default' | 'outline'`, `removable?: boolean`, `onRemove?: () => void`

**UI**: Badge con `✕` si `removable` → `onRemove()`

---

### RatingStars (`components/recipe/RatingStars.svelte`)

**Props**:
```typescript
interface RatingStarsProps {
  value: number;           // 0-5 con decimales (ej: 4.15)
  count?: number;          // opcional, muestra "(128)"
  size?: 'xs' | 'sm' | 'md' | 'lg';
  showCount?: boolean;
  interactive?: boolean;   // false = display only
  onChange?: (value: number) => void;
}
```

**Algoritmo estrellas fraccionales**:
```typescript
const fullStars = Math.floor(value);
const fraction = value % 1;
const hasHalf = fraction >= 0.25 && fraction < 0.75;
const hasPartial = fraction >= 0.75;
// Render: fullStars × ★ + (hasHalf ? ½★ : hasPartial ? ¾★ : ☆) + (5 - fullStars - 1) × ☆
```

**SVG**: Estrellas como SVG inline (fill `currentColor` para heredar color)
**Tamaños**: `xs` (12px), `sm` (16px), `md` (20px), `lg` (24px)

**Interactive**: Si `interactive` + `onChange` → click estrella → `onChange(n)` + feedback visual

**A11y**: `role="img" aria-label="Calificación: 4.15 de 5 estrellas, 128 reseñas"`

---

### AuthorAvatar (`components/common/AuthorAvatar.svelte`)

**Props**: `author: User`, `size?: 'xs' | 'sm' | 'md' | 'lg'`, `href?: string` (link a perfil)

**Fallback**: Iniciales (primeras 2 letras display_name) en círculo con color determinista (hash email → palette)

**Sizes**: `xs` (24px), `sm` (32px), `md` (40px), `lg` (56px)

---

## 4. Recipe Detail Components

### RecipeHero (`components/recipe/RecipeHero.svelte`)

**Props**: `recipe: Recipe`, `onShare?: () => void`, `onSave?: () => void`, `onCook?: () => void`

**Estructura**:
- Imagen hero: `aspect-[16/9] w-full object-cover` + `CategoryBadge` esquina sup-izq
- Acciones: Compartir (Web Share API), Guardar (toggle), Cocinar (link `/cooking/:slug`)

---

### RecipeMeta (`components/recipe/RecipeMeta.svelte`)

**Props**: `recipe: Recipe`

**Render**:
```
Autor: <AuthorAvatar /> {display_name} · {categoria.icon} {categoria.name} · {tags chips}
Tiempo: {prep} min prep + {cook} min cocción · {servings} porciones · {difficulty}
```

---

### IngredientList (`components/recipe/IngredientList.svelte`)

**Props**: `ingredients: RecipeIngredient[]` (con `ingredient_id` resuelto a `Ingrediente`)

**Render**: Lista agrupada opcionalmente por categoría de ingrediente
```
┌─────────────────────────────────────────────────────────────┐
│ INGREDIENTES                                                │
├─────────────────────────────────────────────────────────────┤
│  Proteínas                                                  │
│  • 500g Pollo (en cubos)                                   │
│  Verduras                                                   │
│  • 1 Cebolla (picada fina)                                 │
│  • 2 Zanahorias (en rodajas)                               │
└─────────────────────────────────────────────────────────────┘
```

---

### InstructionSteps (`components/recipe/InstructionSteps.svelte`)

**Props**: `steps: string[]` (array de líneas, cada línea = paso), `onCook?: () => void`

**Render**: Lista numerada con stepper visual
```
<ol class="space-y-6">
  {#each steps as step, i}
    <li class="flex gap-4">
      <span class="flex-shrink-0 w-8 h-8 rounded-full bg-primary text-primary-foreground 
                      flex items-center justify-center font-bold">
        {i + 1}
      </span>
      <div class="flex-1 pt-1 prose prose-sm max-w-none">
        {step}
      </div>
    </li>
  {/each}
</ol>
```

**Modo Cocinando**: Botón "Cocinar" → navega a `/cooking/:slug`

---

### RatingSection (`components/recipe/RatingSection.svelte`)

**Props**: `recipe: Recipe`, `userRating?: Rating | null`, `onRate: (score: number) => void`, `onReview: (text: string) => void`

**Secciones**:
1. **Header**: `RatingStars` grande (lg) + count + distribución barras 5★→1★
2. **Formulario** (si autenticado y no rated): `RatingStars` interactive + Textarea reseña (max 2000 chars) + Submit
3. **Editar** (si ya rated): misma UI + "Actualizar"
4. **Lista reseñas**: Paginada, orden: recientes primero, cada una: autor, fecha, estrellas, texto

---

## 5. Search Components

### FilterSidebar (`components/search/FilterSidebar.svelte`)

**Props**: `filters: SearchFilters`, `onChange: (filters) => void`, `categories: Category[]`, `open: boolean`, `onClose: () => void`

**Tabs**: Categoría, Tags, Ingredientes
- **Categoría**: `CategoryFilter` (radio group)
- **Tags**: `TagAutocomplete` (multi-select)
- **Ingredientes**: `IngredientAutocomplete` (multi-select)

**Footer**: "Limpiar todo" button

**Responsive**:
- `< lg`: Sheet (Drawer right, `w-96 max-w-[90vw]`)
- `≥ lg`: Aside fijo (`w-72 md:w-80 lg:w-96`), sticky top-16

---

### SearchToolbar (`components/search/SearchToolbar.svelte`)

**Props**: `sort: SortOption`, `onSortChange: (sort) => void`, `view: 'grid' | 'list'`, `onViewChange: (view) => void`, `totalCount: number`

**UI**: `Select` orden + `ButtonGroup` vista (Grid/List) + contador total

---

## 6. Auth Components

### AuthForm (`components/auth/AuthForm.svelte`)

**Props**: `mode: 'login' | 'register' | 'forgot' | 'reset'`, `returnTo?: string`

**Sub-componentes**:
- `EmailInput` (validación email + autocomplete="email")
- `PasswordInput` (con toggle visibilidad + strength meter en register/reset)
- `DisplayNameInput` (solo register)
- `OAuthButtons`: Google + GitHub (icon + label)
- `SubmitButton` (loading state, disabled si invalid)
- `FooterLinks`: "¿Olvidaste password?", "¿No tienes cuenta?", etc.

**Validación**: Zod schema en cliente + server

---

### PasswordStrengthMeter (`components/auth/PasswordStrengthMeter.svelte`)

**Props**: `password: string`, `requirements?: string[]`

**UI**: Barra progresiva (0-4) + checklist visual:
- ✅ 8+ caracteres
- ✅ 1 mayúscula
- ✅ 1 minúscula
- ✅ 1 número
- ✅ 1 especial (!@#$%^&*)

**Colors**: `destructive` → `warning` → `success` según score

---

## 7. Profile & Settings

### AvatarUpload (`components/profile/AvatarUpload.svelte`)

**Props**: `currentUrl?: string`, `onUpload: (file: File) => Promise<string>`, `size?: 'sm' | 'md' | 'lg'`

**Features**: Drag & drop + click → file picker → preview → upload → callback con nueva URL
**Validación**: Tipo imagen, max 5MB, dimensiones recomendadas 1:1

---

### ProfileTabs (`components/profile/ProfileTabs.svelte`)

**Tabs**: Perfil | Seguridad | Cuenta
- **Perfil**: Nombre, avatar, email (read-only), bio (futuro)
- **Seguridad**: Cambiar password, sesiones activas (listado + "Cerrar todas"), 2FA (v2)
- **Cuenta**: Baja lógica (con checkbox "eliminar recetas"), GDPR (confirmación expresa)

---

## 8. Cooking Mode

### CookingStepper (`components/cooking/CookingStepper.svelte`)

**Props**: `recipe: Recipe`, `steps: string[]`, `onExit: () => void`

**Features**:
- **Wake Lock**: `navigator.wakeLock.request('screen')` + cleanup
- **Navegación**: Swipe izq/der (touch), botones ◀ ▶, teclado (← →), voz ("siguiente", "anterior", "repite")
- **Timer por paso**: Botón "Iniciar X min" → countdown visual + notificación + sonido
- **Voz**: `SpeechRecognition` (comandos: "siguiente", "anterior", "repite", "timer X minutos", "pausa", "continuar")
- **Fullscreen**: `document.documentElement.requestFullscreen()` + `screen.orientation.lock('landscape')` opcional
- **Persistencia**: `localStorage` guarda paso actual + timers si recarga accidental

**UI**:
```
Header: [✕ Salir] [⚙ Ajustes: voz, pantalla, fuente] [🔊 Voz: ON/OFF]
Step Counter: "Paso 3 de 7"
Content: Texto paso grande (text-2xl md:text-3xl), line-height relajado
Navigation: ◀ Anterior | Siguiente ▶ (botones grandes, touch-friendly 60x60px)
Timer: ⏱ 5:00 [Iniciar] [Pausar] [Reset] (persistente por paso)
Footer: [◀ Anterior] [Siguiente ▶] (sticky bottom)
```

**A11y**: `role="region" aria-label="Modo cocinando"`, comandos voz anunciados via `aria-live="polite"`

---

## 9. Common / Feedback

### Toast (`components/ui/Toast.svelte` / Sonner)

**Variants**: `success`, `error`, `warning`, `info`, `loading`
**API**: `toast.success("Guardado")`, `toast.error("Error")`, `toast.loading("Guardando...")`
**Position**: `top-right` (default), `bottom-center` (móvil)
**Duration**: 4s (success/info), 6s (error), persistente (loading)

---

### Modal / Dialog (`components/ui/Dialog.svelte`, `AlertDialog.svelte`)

**Props**: `open: boolean`, `onClose: () => void`, `title`, `description`, `children`
**A11y**: Focus trap, `aria-modal="true"`, `role="dialog"`, `aria-labelledby`, `aria-describedby`, ESC para cerrar, click overlay para cerrar (configurable)

**AlertDialog**: `destructive` action confirmación (borrar, baja, GDPR) — requiere confirmación explícita

---

### Sheet / Drawer (`components/ui/Sheet.svelte`)

**Props**: `open`, `onClose`, `side: 'left' | 'right' | 'bottom'`, `children`
**Sizes**: `sm` (320px), `md` (384px), `lg` (512px), `full` (100vw)
**A11y**: Focus trap, `aria-modal`, swipe to close (bottom), backdrop click close

---

### Tooltip (`components/ui/Tooltip.svelte`)

**Props**: `content`, `side: 'top' | 'bottom' | 'left' | 'right'`, `delay?: number`
**Trigger**: `hover` + `focus` (teclado)
**A11y**: `role="tooltip"`, `aria-describedby` en trigger

---

### EmptyState (`components/common/EmptyState.svelte`)

**Variants**: `search`, `favorites`, `recipes`, `ratings`, `admin`, `generic`
**Props**: `variant`, `title`, `description`, `action?: { label: string; onClick: () => void }`, `secondaryAction?`, `illustration?: string` (nombre SVG)

---

### ErrorState (`components/common/ErrorState.svelte`)

**Props**: `message`, `onRetry?: () => void`, `onGoBack?: () => void`

---

### Alert (`components/ui/Alert.svelte`) — **Network Errors & Destructive Alerts**

**Props**:
```typescript
interface AlertProps {
  variant: 'default' | 'destructive' | 'warning' | 'success';
  title: string;
  description: string;
  action?: { label: string; onClick: () => void };
  dismissible?: boolean;          // default true
  onDismiss?: () => void;
}
```

**Variants & Tokens**:
| Variant | Border | Background | Text | Icon | Uso |
|---------|--------|------------|------|------|-----|
| `destructive` | `border-destructive/50` | `bg-destructive/10` | `text-destructive` | `AlertCircle` | **Errores de red, 5xx, 401, 404, validación** |
| `warning` | `border-warning/50` | `bg-warning/10` | `text-warning` | `AlertTriangle` | Offline, acciones destructivas suaves |
| `success` | `border-success/50` | `bg-success/10` | `text-success` | `CheckCircle` | Operaciones exitosas, confirmaciones |
| `default` | `border-border` | `bg-background` | `text-foreground` | `Info` | Info neutral, onboarding |

**Posicionamiento**:
- **Toast superior** (`top-right`): Errores de red, 5xx, 401, 404 — auto-dismiss 6s + acción "Reintentar"
- **Toast inferior** (`bottom-center`): Offline detectado — persistente hasta reconectar
- **Inline** (debajo de form): Errores de validación 422 — no auto-dismiss, desaparece al corregir
- **Página 404/5xx**: Toast + página dedicada

**Implementación shadcn `Alert` (Destructive)**:
```svelte
<script lang="ts">
  import { X, AlertCircle, AlertTriangle, CheckCircle, Info } from 'lucide-svelte';
  export let variant: 'default' | 'destructive' | 'warning' | 'success' = 'default';
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
    data-[variant=success]:border-success/50 data-[variant=success]:bg-success/10 data-[variant=success]:text-success
    animate-fade-in"
  role="alert"
  aria-live="polite"
>
  <div class="flex items-start gap-3">
    {#if variant === 'destructive'}
      <AlertCircle class="w-5 h-5 shrink-0" />
    {:else if variant === 'warning'}
      <AlertTriangle class="w-5 h-5 shrink-0" />
    {:else if variant === 'success'}
      <CheckCircle class="w-5 h-5 shrink-0" />
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

**Tokens CSS (Tailwind)**:
```js
// tailwind.config.js
colors: {
  destructive: {
    DEFAULT: '#B84A3A',      // warm red
    hover: '#A03A2A',
    foreground: '#FAF9F6',   // warm off-white
    light: '#FEF2F2',        // bg for alert (destructive/10)
    border: '#FECACA',       // border
  },
  warning: {
    DEFAULT: '#C47A2A',
    light: '#FEF9E7',
    border: '#FDE68A',
  },
  success: {
    DEFAULT: '#5A7D4A',
    light: '#F0FDF4',
    border: '#86EFAC',
  },
}
```

**Uso en Network Errors**:
```typescript
// stores/toast.ts
import { toast } from 'svelte-sonner';

export function showNetworkError(retryAction?: () => void) {
  toast.error('Error de conexión', {
    description: 'No pudimos conectar con el servidor. Verifica tu conexión.',
    action: retryAction ? { label: 'Reintentar ahora', onClick: retryAction } : undefined,
    duration: 6000,
    className: 'bg-destructive/10 border-destructive/50 text-destructive',
  });
}

export function showServerError(retryAction?: () => void) {
  toast.error('Error del servidor', {
    description: 'Algo salió mal. Nuestro equipo ya fue notificado.',
    action: retryAction ? { label: 'Reintentar', onClick: retryAction } : undefined,
    duration: 0, // persistente
    className: 'bg-destructive/10 border-destructive/50 text-destructive',
  });
}
```

---

### Skeleton Components

| Componente | Uso |
|------------|-----|
| `RecipeCardSkeleton` | Grid home, búsqueda, favoritos |
| `SearchSkeleton` | Buscador + sidebar |
| `DetailSkeleton` | Página detalle receta |
| `ProfileSkeleton` | Perfil usuario |
| `AdminTableSkeleton` | Tablas admin |

**Animación**: `animate-pulse` + gradient shimmer (`bg-gradient-to-r from-muted via-muted-foreground/20 to-muted`)

---

## 10. Admin Components (Proyecto Admin)

### AdminLayout (`components/admin/AdminLayout.svelte`)

**Sidebar navegación**: Dashboard, Categorías, Usuarios, Ingredientes, Métricas, Config, Auditoría
**Header**: Usuario admin + logout
**Responsive**: Sidebar colapsable en `< lg`

---

### AdminTable (`components/admin/AdminTable.svelte`)

**Props**: `columns: ColumnDef[]`, `data: any[]`, `pagination`, `sorting`, `filtering`, `selection`, `actions: RowAction[]`

**Features**: Server-side pagination/sort/filter, row selection bulk actions, column resize, sticky header

---

### AdminFormModal (`components/admin/AdminFormModal.svelte`)

**Props**: `open`, `onClose`, `title`, `fields: FieldDef[]`, `onSubmit: (data) => Promise<void>`, `initialData?`

**Fields**: `input`, `textarea`, `select`, `checkbox`, `radio`, `switch`, `file`, `color-picker`, `icon-picker`, `slug` (auto-generado)

---

## 11. Design Tokens Reference (para implementación)

### Colors (Tailwind config extend)
```js
colors: {
  primary: { 500: '#6366f1', 600: '#4f46e5', ... },
  category: { // dinámico desde BD
    postre: '#f97316',
    entrada: '#22c55e',
    snack: '#eab308',
    'plato-principal': '#3b82f6',
    acompañamiento: '#a855f7',
    bebida: '#06b6d4',
    desayuno: '#f43f5e',
    otro: '#64748b',
  },
  rating: '#fbbf24', // amber-400 para estrellas
}
```

### Spacing Scale
```js
spacing: {
  '0': '0',
  '1': '0.25rem',  // 4px
  '2': '0.5rem',   // 8px
  '3': '0.75rem',  // 12px
  '4': '1rem',     // 16px
  '5': '1.25rem',  // 20px
  '6': '1.5rem',   // 24px
  '8': '2rem',     // 32px
  '10': '2.5rem',  // 40px
  '12': '3rem',    // 48px
  '16': '4rem',    // 64px
}
```

### Typography
```js
fontFamily: {
  sans: ['Inter', 'system-ui', 'sans-serif'],
  mono: ['JetBrains Mono', 'monospace'],
},
fontSize: {
  xs: ['0.75rem', { lineHeight: '1rem' }],
  sm: ['0.875rem', { lineHeight: '1.25rem' }],
  base: ['1rem', { lineHeight: '1.5rem' }],
  lg: ['1.125rem', { lineHeight: '1.75rem' }],
  xl: ['1.25rem', { lineHeight: '1.75rem' }],
  '2xl': ['1.5rem', { lineHeight: '2rem' }],
  '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
  '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
}
```

### Border Radius
```js
borderRadius: {
  none: '0',
  sm: '0.25rem',   // 4px
  DEFAULT: '0.375rem', // 6px
  md: '0.5rem',    // 8px
  lg: '0.75rem',   // 12px
  xl: '1rem',      // 16px
  '2xl': '1.5rem', // 24px
  full: '9999px',
}
```

### Shadows
```js
boxShadow: {
  sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
  DEFAULT: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
  md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
  lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
  xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
}
```

---

## Testing Checklist por Componente

| Componente | Unit Tests | A11y Tests | Visual Regression |
|------------|------------|------------|-------------------|
| Navbar | ✅ | ✅ (focus, skip link, ARIA) | ✅ |
| RecipeCard | ✅ (click, imagen, badges) | ✅ (focus, alt, ARIA) | ✅ |
| CategoryBadge | ✅ (colores, variants) | ✅ (contraste) | ✅ |
| RatingStars | ✅ (fraccional, interactive) | ✅ (ARIA label) | ✅ |
| SearchBar | ✅ (debounce, chips) | ✅ (focus trap, ARIA) | ✅ |
| RecipeCard | ✅ | ✅ | ✅ |
| CookingStepper | ✅ (wake lock, voz, timer) | ✅ (voice commands) | ✅ |
| Modal/Sheet | ✅ (focus trap, ESC) | ✅ (focus trap, ARIA) | ✅ |

---

## Implementación Sugerida (Orden)

1. **Design tokens** → `tailwind.config.js` + `global.css`
2. **Base UI** (shadcn-svelte): Button, Badge, Card, Input, Select, Dialog, Sheet, Toast, Tooltip, Avatar, Skeleton
3. **Custom base**: CategoryBadge, RatingStars, AuthorAvatar, TagChip
4. **Layout**: Navbar, Footer, Breadcrumb
5. **Home**: Hero, SearchBar, RecipeGrid, RecipeCard
6. **Detail**: RecipeHero, IngredientList, InstructionSteps, RatingSection
7. **Search**: FilterSidebar, ActiveFiltersChips, TagAutocomplete, IngredientAutocomplete
8. **Auth**: AuthForm, PasswordStrengthMeter
9. **Profile**: AvatarUpload, ProfileTabs
10. **Cooking**: CookingStepper (wake lock, voz, timer)
11. **Admin**: AdminLayout, AdminTable, AdminFormModal