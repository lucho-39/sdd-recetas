# Design System — Recetario IA

> Tokens, principios y guías de implementación para SvelteKit + shadcn-svelte + Tailwind CSS.

---

## 1. Paleta de Colores

### Colores Base (Warm Palette — Temática Comida)

**Fondo principal**: `rgb(250, 249, 246)` → `#FAF9F6` (warm off-white, NO blanco puro)
**Texto principal**: `#2D2B28` (dark charcoal, NO negro puro)
**Títulos**: `#3D4034` (dark olive green — verde oliva oscuro)

> **Regla**: NO usar `#FFFFFF` (blanco puro) ni `#000000` (negro puro) en ningún token.

### Colores Semánticos (Light / Dark)

| Token | Light | Dark | Uso |
|-------|-------|------|-----|
| `background` | `#FAF9F6` (rgb 250,249,246) | `#1C1A18` | Fondo principal páginas |
| `surface` | `#F5F3F0` | `#24211F` | Cards, modales, sheets |
| `foreground` | `#2D2B28` | `#E8E5E1` | Texto principal |
| `muted` | `#F0EDE8` | `#2A2724` | Fondos secundarios |
| `muted-foreground` | `#6B6762` | `#A8A4A0` | Texto secundario, placeholders |
| `border` | `#E8E4DF` | `#3D3935` | Bordes, divisores |
| `ring` | `#3D4034` | `#8F8C84` | Focus rings (dark olive) |
| `primary` | `#3D4034` | `#A8A4A0` | CTAs principales, links (dark olive) |
| `primary-hover` | `#4A4E40` | `#B8B4AC` | Hover primary |
| `destructive` | `#B84A3A` | `#D47A6A` | Eliminar, acciones irreversibles |
| `success` | `#5A7D4A` | `#7AB86A` | Confirmaciones, guardado |
| `warning` | `#C47A2A` | `#D4A84A` | Advertencias |

### Colores de Categoría (10 categorías — Tailwind tonalities asignadas)

| Categoría | Hex | Tailwind Ref | Uso Badge |
|-----------|-----|--------------|-----------|
| Postre | `#FB923C` | orange-400 | 🍰 |
| Entrada | `#4ADE80` | green-400 | 🥗 |
| Snack | `#FACC15` | yellow-400 | 🍿 |
| Plato principal | `#60A5FA` | blue-400 | 🍽️ |
| Acompañamiento | `#C084FC` | purple-400 | 🥔 |
| Bebida | `#22D3EE` | cyan-400 | 🥤 |
| Desayuno | `#FB7185` | rose-400 | ☕ |
| Sopa/Crema | `#A3E635` | lime-400 | 🍲 |
| Ensalada | `#34D399` | emerald-400 | 🥗 |
| Horneados | `#F87171` | red-400 | 🍞 |

> **Nota**: Usar `*-400` para mejor contraste en light/dark. Texto sobre badge: **blanco** (`color: white`). El color se usa como `background-color` y `border-color` del badge.

### Dark Mode Tokens (Override)

| Token | Dark Value |
|-------|------------|
| `background` | `#1C1A18` |
| `surface` | `#24211F` |
| `foreground` | `#E8E5E1` |
| `muted` | `#2A2724` |
| `muted-foreground` | `#A8A4A0` |
| `border` | `#3D3935` |
| `ring` | `#8F8C84` |
| `primary` | `#C8C4BC` |
| `destructive` | `#D47A6A` |
| `success` | `#7AB86A` |

> Los colores de categoría **NO cambian** en dark mode (identidad visual).

---

## 2. Tipografía

### Fuentes

| Rol | Fuente | Fallback | Uso |
|-----|--------|----------|-----|
| **Títulos** | **Playfair Display** (Serif) | `Georgia, serif` | Todos los headings (h1-h6), hero title, card titles |
| **Cuerpo / UI** | **Inter** (Sans) | `system-ui, -apple-system, sans-serif` | Body, labels, inputs, botones, meta, navegación |

**Carga** (en `global.css`):
```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Playfair+Display:wght@400;500;600;700&display=swap');
```

### Escala Tipográfica

| Token | Tamaño | Line Height | Peso | Fuente | Uso |
|-------|--------|-------------|------|--------|-----|
| `text-xs` | `0.75rem` (12px) | `1rem` | 400 | Inter | Labels, captions, timestamps |
| `text-sm` | `0.875rem` (14px) | `1.25rem` | 400/500 | Inter | Body secundario, inputs, meta |
| `text-base` | `1rem` (16px) | `1.6rem` | 400 | **Inter** | **Body principal** |
| `text-lg` | `1.125rem` (18px) | `1.7rem` | 500 | Inter | Subtítulos, cards |
| `text-xl` | `1.25rem` (20px) | `1.7rem` | 600 | **Playfair Display** | Títulos cards, headers sección |
| `text-2xl` | `1.5rem` (24px) | `1.4` | 600 | **Playfair Display** | Títulos página, hero subtitle |
| `text-3xl` | `1.875rem` (30px) | `1.3` | 600 | **Playfair Display** | Hero title (mobile) |
| `text-4xl` | `2.25rem` (36px) | `1.25` | 700 | **Playfair Display** | Hero title (desktop) |
| `text-5xl` | `3rem` (48px) | `1.2` | 700 | **Playfair Display** | Hero title (large) |

### Fluid Typography — Hero Title

```css
.hero-title {
  font-family: 'Playfair Display', Georgia, serif;
  font-size: clamp(2.5rem, 6vw + 1rem, 4.5rem);
  line-height: 1.15;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: #3D4034; /* dark olive */
}
```

### Hero Copy (Frase del Espíritu)

> **"Donde cada ingrediente cuenta una historia y cada receta nace del corazón."**

---

## 3. Espaciado (Spacing Scale — 4px Base)

| Token | Valor | Px | Uso |
|-------|-------|----|-----|
| `space-1` | `0.25rem` | 4px | Gap iconos-texto, padding interno iconos |
| `space-2` | `0.5rem` | 8px | Gap interno componentes, gap grid tight |
| `space-3` | `0.75rem` | 12px | Padding cards, gap vertical estándar |
| `space-4` | `1rem` | 16px | **Padding estándar**, gap grid normal |
| `space-5` | `1.25rem` | 20px | Padding sections, gap vertical medio |
| `space-6` | `1.5rem` | 24px | Gap grid amplio, padding sections |
| `space-8` | `2rem` | 32px | Padding hero, sections grandes |
| `space-10` | `2.5rem` | 40px | Separación secciones grandes |
| `space-12` | `3rem` | 48px | Separación hero/sections XL |

### Patrones de Uso

| Patrón | Tokens | Ejemplo |
|--------|--------|---------|
| **Card padding** | `p-4` / `p-5` (lg) | `RecipeCard`, `Card` |
| **Section vertical** | `py-10 md:py-14 lg:py-20` | Sections páginas |
| **Container horizontal** | `px-4 md:px-6 lg:px-8` | Wrapper páginas |
| **Gap grid** | `gap-4 md:gap-6 lg:gap-8` | `RecipeGrid` |
| **Gap vertical stack** | `space-y-4 md:space-y-6` | Stacks verticales |
| **Icon + text gap** | `gap-2` | Badges, meta, flex items |

---

## 4. Radios & Bordes

### Border Radius Scale (Mínimos — "Radios Mínimos")

| Token | Valor | Px | Uso |
|-------|-------|----|-----|
| `rounded-none` | `0` | 0 | Tablas, inputs flush |
| `rounded-sm` | `0.125rem` | 2px | **Badges, tags, chips** |
| `rounded` / `rounded-md` | `0.25rem` | 4px | **Inputs, selects, botones** |
| `rounded-lg` | `0.375rem` | 6px | **Cards, modales, dropdowns, sheets** |
| `rounded-xl` | `0.5rem` | 8px | Hero images, modales grandes |
| `rounded-full` | `9999px` | — | **Avatares, pills, botones redondos** |

> **Regla**: Radios mínimos. `rounded-sm` (2px) para badges, `rounded-md` (4px) para inputs/botones, `rounded-lg` (6px) para cards.

### Border Width

| Token | Valor | Uso |
|-------|-------|-----|
| `border` | `1px` | **Estándar** (cards, inputs, tablas) |
| `border-0` | `0` | Reset |

---

## 5. Sombras (Tenues — "Sombras Tenues")

| Token | Valor | Uso |
|-------|-------|-----|
| `shadow-none` | `none` | Reset |
| `shadow-xs` | `0 1px 2px 0 rgb(45 43 40 / 0.04)` | **Cards estáticas**, badges |
| `shadow-sm` | `0 1px 3px 0 rgb(45 43 40 / 0.06)` | **Cards hover**, dropdowns |
| `shadow-md` | `0 4px 8px -2px rgb(45 43 40 / 0.08)` | **Modales, sheets, popovers** |
| `shadow-lg` | `0 12px 16px -4px rgb(45 43 40 / 0.1)` | **Modales grandes, fullscreen sheets** |

> **Color sombra**: `rgb(45 43 40 / alpha)` — warm charcoal, NO negro puro.
> **Intensidad**: Muy tenue (`alpha 0.04-0.1`). Sensación de profundidad sutil.

### Focus Ring (Accesibilidad)

```css
.focus-ring {
  @apply focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background;
}
```

---

## 5.5. Alert & Feedback Tokens (Network Errors & Destructive Alerts)

### Alert Variants & Tokens

| Variant | Border | Background | Text | Icon | Uso |
|---------|--------|------------|------|------|-----|
| `destructive` | `border-destructive/50` | `bg-destructive/10` | `text-destructive` | `AlertCircle` | **Errores de red, 5xx, 401, 404, validación** |
| `warning` | `border-warning/50` | `bg-warning/10` | `text-warning` | `AlertTriangle` | Offline, acciones destructivas suaves |
| `success` | `border-success/50` | `bg-success/10` | `text-success` | `CheckCircle` | Operaciones exitosas, confirmaciones |
| `default` | `border-border` | `bg-background` | `text-foreground` | `Info` | Info neutral, onboarding |

### Colores Destructive / Warning / Success (Tailwind)

| Token | Light | Dark | Uso |
|-------|-------|------|-----|
| `destructive-DEFAULT` | `#B84A3A` | `#D47A6A` | Texto/bordes destructive |
| `destructive-light` | `#FEF2F2` | `#7F1D1D` | Background alert (destructive/10) |
| `destructive-border` | `#FECACA` | `#991B1B` | Border alert |
| `warning-DEFAULT` | `#C47A2A` | `#D4A84A` | Texto/bordes warning |
| `warning-light` | `#FEF9E7` | `#78350F` | Background alert warning |
| `success-DEFAULT` | `#5A7D4A` | `#7AB86A` | Texto/bordes success |
| `success-light` | `#F0FDF4` | `#14532D` | Background alert success |

### Posicionamiento Alertas de Red

| Situación | Componente | Variante | Posición | Comportamiento |
|-----------|------------|----------|----------|----------------|
| **Error fetch** (network, timeout) | `Alert` | `destructive` | Toast superior (`top-right`) | Auto-dismiss 6s + botón "Reintentar ahora" |
| **Error 5xx** | `Alert` | `destructive` | Toast superior + persistente | No auto-dismiss, botón "Reintentar", "Reportar" |
| **Error 401/403** (auth expired) | `Alert` | `destructive` | Toast superior | Auto-redirect `/login?returnTo=...` tras 3s |
| **Error 404** | `Alert` | `destructive` | Toast superior + página 404 | Auto-dismiss 6s |
| **Error validación** (422) | `Alert` | `destructive` | Inline (debajo form) | No auto-dismiss, desaparece al corregir |
| **Offline detectado** | `Alert` | `warning` | Toast inferior | "Modo offline: funcionalidad limitada" |

### Implementación Toast Network Error (Ejemplo)

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

## 6. Animaciones & Transiciones

### Duraciones

| Token | Valor | Uso |
|-------|-------|-----|
| `duration-100` | `100ms` | Micro-interacciones (hover iconos) |
| `duration-150` | `150ms` | **Estándar** (hover, focus, toggle) |
| `duration-200` | `200ms` | Dropdowns, tooltips |
| `duration-300` | `300ms` | **Modales, sheets, tabs, skeletons** |
| `duration-500` | `500ms` | Transiciones página |

### Easings

| Token | Valor | Uso |
|-------|-------|-----|
| `ease-out` | `cubic-bezier(0, 0, 0.2, 1)` | **Estándar** (entrada, salida suave) |
| `ease-in-out` | `cubic-bezier(0.4, 0, 0.2, 1)` | Modales, sheets |

### Skeleton Loading (Global — En Toda la App)

```css
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
.animate-shimmer {
  animation: shimmer 1.8s infinite linear;
  background: linear-gradient(90deg, 
    hsl(var(--muted)) 25%, 
    hsl(var(--muted-foreground) / 0.08) 50%, 
    hsl(var(--muted)) 75%
  );
  background-size: 200% 100%;
}
```

**Aplicación**: **TODAS las páginas** usan skeleton loaders durante fetch:
- `RecipeCardSkeleton` → Grid home, búsqueda, favoritos
- `SearchSkeleton` → Buscador + sidebar
- `DetailSkeleton` → Página detalle receta
- `ProfileSkeleton` → Perfil usuario
- `AdminTableSkeleton` → Tablas admin

---

## 7. Breakpoints & Responsive

### Breakpoints

| Breakpoint | Prefijo | Ancho | Uso |
|------------|---------|-------|-----|
| `sm` | `sm:` | 640px | Grid 2 cols, navbar compacto |
| `md` | `md:` | 768px | **Sidebar fija**, grid 3 cols |
| `lg` | `lg:` | 1024px | Grid 4 cols, sidebar ancha |
| `xl` | `xl:` | 1280px | Max-width container 1200px |

### Container

```css
.container {
  @apply mx-auto px-4 md:px-6 lg:px-8 max-w-7xl; /* 1280px */
}
```

### Patrones Responsive

| Patrón | Clases |
|--------|--------|
| **Grid responsive** | `grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4` |
| **Sidebar colapsable** | `hidden lg:block` + `lg:hidden` (hamburger) |
| **Texto fluido** | `text-base md:text-lg lg:text-xl` |
| **Padding responsive** | `px-4 md:px-6 lg:px-8` |
| **Gap responsive** | `gap-4 md:gap-6 lg:gap-8` |

---

## 8. Modo Oscuro (Dark Mode)

### Estrategia: `class` (Tailwind)

```html
<html class="dark">  <!-- activado por JS / prefers-color-scheme -->
```

### Tokens que Cambian (Light → Dark)

| Token | Light | Dark |
|-------|-------|------|
| `background` | `#FAF9F6` | `#1C1A18` |
| `surface` | `#F5F3F0` | `#24211F` |
| `foreground` | `#2D2B28` | `#E8E5E1` |
| `muted` | `#F0EDE8` | `#2A2724` |
| `muted-foreground` | `#6B6762` | `#A8A4A0` |
| `border` | `#E8E4DF` | `#3D3935` |
| `ring` | `#3D4034` | `#8F8C84` |
| `primary` | `#3D4034` | `#C8C4BC` |

### Colores que NO Cambian

| Token | Por qué |
|-------|---------|
| Colores categoría | Identidad visual |
| Rating amber | Estrellas siempre ámbar |

### Toggle Implementation

```typescript
// stores/theme.ts
import { persisted } from 'svelte-local-storage-store';

export const theme = persisted<'light' | 'dark' | 'system'>('theme', 'system');

export function initTheme() {
  const stored = theme.get();
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const isDark = stored === 'dark' || (stored === 'system' && prefersDark);
  document.documentElement.classList.toggle('dark', isDark);
}
```

---

## 9. Componentes Clave — Especificaciones Actualizadas

### Navbar (`components/layout/Navbar.svelte`)

**Estructura**:
- **Izquierda**: Logo "Recetas App" (Playfair Display, text-xl, dark olive)
- **Derecha (reactivo)**:
  - No auth: `Login` (ghost) + `Registrarse` (primary)
  - Auth: `Mis Recetas` + `Mis Favoritos` + `AvatarDropdown` (Perfil, Config, Logout)
- **Fijo**: `fixed top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur-sm`
- **Persistente**: En toda la app

### Hero (`components/home/Hero.svelte`)

```html
<section class="py-16 md:py-20 px-4 text-center" aria-labelledby="hero-title">
  <div class="max-w-3xl mx-auto">
    <h1 id="hero-title" class="hero-title">
      Donde cada ingrediente cuenta una historia y cada receta nace del corazón
    </h1>
    <p class="mt-4 text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto">
      Descubre, guarda y cocina con alma. Tu cocina, tus reglas.
    </p>
  </div>
</section>
```

### Buscador Live (`components/home/SearchBar.svelte`)

**Mecánica**: Live search con **debounce 300ms**
- Input: `type="search"`, placeholder "Buscar por nombre, ingrediente..."
- Debounce: 300ms → `onSearch(filters)`
- Clear button (X) aparece al escribir
- Loading spinner durante fetch
- **Chips activos** debajo: Categoría, Tags, Ingredientes — cada uno con ✕ para quitar
- Botón "Limpiar todo" si hay filtros
- **Sticky**: `sticky top-16 z-40 bg-background/95 backdrop-blur-sm border-b border-border`

### Search Sidebar (Filtros)

- **Categoría**: Radio group (una sola)
- **Tags**: `TagAutocomplete` multi-select + chips
- **Ingredientes**: `IngredientAutocomplete` multi-select
- **Responsive**: `< lg` → Sheet (Drawer right), `≥ lg` → Aside sticky (`w-72 md:w-80`)

### RecipeCard (`components/recipe/RecipeCard.svelte`)

**Estructura**:
```
┌─────────────────────────────────────┐
│  Imagen (aspect-[4/3], 400x400)     │  ← placehold.co/400x400
│  Badge Categoría (esquina sup-izq)   │  ← usa category.color
├─────────────────────────────────────┤
│  Título (2 líneas, truncate)        │  ← Playfair Display
│  ⭐ Rating fraccional  📖 Favs  👤   │  ← Inter, text-sm
└─────────────────────────────────────┘
```

**Imagen**: `placehold.co/400x400/{bg}/{color}?text={slug}` — bg = category.color lightened, color = category.color
**Badge Categoría**: `CategoryBadge` — `variant="outline"`, `style="background: {color}; border: {color}; color: white"`, `rounded-sm` (2px)
**Click**: Navega a `/receta/{recipe.slug}`

### Detalle Receta — `/receta/<slug>`

**Layout**: Navbar + Breadcrumb + Hero imagen + Meta + Ingredientes + Instrucciones + Rating + Comentarios
**Modo Cocinando**: Botón "Cocinar" → `/cooking/:slug` (fullscreen, wake lock, swipe, voz, timer)

### Infinite Scroll (Global)

- **Paginación**: NO. **Scroll infinito** en todos los grids (Home, Búsqueda, Favoritos, Mis Recetas, Perfil autor)
- **Mecánica**: `IntersectionObserver` en sentinel (div después de última card) → `onLoadMore()`
- **Loading**: Append skeletons al final (no replace)

### Estados Vacíos & 404

#### Empty States (por contexto)
| Contexto | Ilustración | Mensaje | CTA |
|----------|-------------|---------|-----|
| Búsqueda sin resultados | 🔍 Lupa + ? | "No hay recetas con esos filtros" | "Quitar filtros", "Ver todas" |
| Sin favoritos | 🤍 Corazón vacío | "Tu despensa está vacía" | "Explorar recetas" |
| Sin recetas propias | 🍳 Chef | "Tu cocina espera tu primera receta" | "Crear receta" |
| Sin resultados admin | 📋 Clipboard | "No hay elementos" | "Crear nuevo" |

#### Página 404 Temática (`/404`)

```html
<div class="min-h-[70vh] flex flex-col items-center justify-center px-4 text-center">
  <div class="mb-6 text-6xl">🍪</div>
  <h1 class="text-3xl md:text-4xl font-playfair font-medium text-foreground mb-2">
    ¡Ups! Esta receta se perdió en el horno
  </h1>
  <p class="text-muted-foreground mb-8 max-w-md mx-auto">
    La página que buscas no existe o se quemó. 
    Pero no te preocupes, tenemos muchas más deliciosas esperándote.
  </p>
  <div class="flex flex-col sm:flex-row gap-3 justify-center">
    <Button variant="primary" on:click={() => goto('/')}>Volver al inicio</Button>
    <Button variant="outline" on:click={() => goto('/buscar')}>Buscar recetas</Button>
  </div>
</div>
```

---

## 10. Footer Persistente (`components/layout/Footer.svelte`)

**En toda la app** (incluye páginas auth, 404, admin):

```html
<footer class="border-t border-border bg-surface/50 py-6 md:py-8">
  <div class="container mx-auto px-4 md:px-6 lg:px-8">
    <div class="flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-muted-foreground">
      <p class="font-playfair font-medium text-foreground">
        Recetas App — Hecho con amor y buenos ingredientes
      </p>
      <nav class="flex flex-wrap items-center gap-4 md:gap-6">
        <a href="/sobre-nosotros" class="hover:text-primary transition-colors">Nosotros</a>
        <a href="/privacidad" class="hover:text-primary transition-colors">Privacidad</a>
        <a href="/terminos" class="hover:text-primary transition-colors">Términos</a>
        <a href="/contacto" class="hover:text-primary transition-colors">Contacto</a>
      </nav>
      <p class="text-xs text-muted-foreground/70">
        © 2025 Recetas App. Hecho con 🍳 en Argentina.
      </p>
    </div>
  </div>
</footer>
```

**Estilos**: `fixed bottom-0 w-full` NO (usa layout normal con `min-h-screen flex flex-col` en layout principal, footer al final con `mt-auto`)

---

## 11. Páginas — Resumen Completo

| Ruta | Descripción | Componentes Clave |
|------|-------------|-------------------|
| `/` | Home: Hero + Buscador live + Grid infinito | Hero, SearchBar, RecipeGrid |
| `/receta/:slug` | Detalle completo | RecipeHero, IngredientList, InstructionSteps, RatingSection |
| `/buscar` | Búsqueda avanzada (sidebar + grid) | FilterSidebar, SearchToolbar, RecipeGrid |
| `/login` `/register` | Auth forms | AuthForm, PasswordStrengthMeter |
| `/mis-recetas` | CRUD propias (tabs) | RecipeTable, RecipeCardCompact |
| `/mis-favoritos` | Colecciones + grid | CollectionSidebar, RecipeGrid |
| `/perfil` | Perfil + seguridad + cuenta | ProfileTabs, AvatarUpload |
| `/usuario/:id` | Perfil público + grid recetas | ProfileHeader, RecipeGrid |
| `/cooking/:slug` | Modo cocinando (fullscreen) | CookingStepper (wake lock, voz, timer) |
| `/404` | Página 404 temática | — |

---

## 12. Implementación Checklist (Tailwind Config)

```js
// tailwind.config.js
export default {
  darkMode: 'class',
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        background: '#FAF9F6',
        surface: '#F5F3F0',
        foreground: '#2D2B28',
        muted: '#F0EDE8',
        'muted-foreground': '#6B6762',
        border: '#E8E4DF',
        primary: {
          DEFAULT: '#3D4034',
          hover: '#4A4E40',
        },
        destructive: { DEFAULT: '#B84A3A', hover: '#A03A2A' },
        success: { DEFAULT: '#5A7D4A', hover: '#4A6D3A' },
        warning: { DEFAULT: '#C47A2A', hover: '#A86820' },
        category: {
          postre: '#FB923C',
          entrada: '#4ADE80',
          snack: '#FACC15',
          'plato-principal': '#60A5FA',
          acompañamiento: '#C084FC',
          bebida: '#22D3EE',
          desayuno: '#FB7185',
          'sopa-crema': '#A3E635',
          ensalada: '#34D399',
          horneados: '#F87171',
        },
        rating: { 500: '#FBBF24' },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        serif: ['Playfair Display', 'Georgia', 'serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      borderRadius: {
        sm: '0.125rem',   // 2px — badges
        md: '0.25rem',    // 4px — inputs, botones
        lg: '0.375rem',   // 6px — cards
        xl: '0.5rem',     // 8px — hero
        full: '9999px',
      },
      boxShadow: {
        xs: '0 1px 2px 0 rgb(45 43 40 / 0.04)',
        sm: '0 1px 3px 0 rgb(45 43 40 / 0.06)',
        md: '0 4px 8px -2px rgb(45 43 40 / 0.08)',
        lg: '0 12px 16px -4px rgb(45 43 40 / 0.1)',
      },
      animation: {
        shimmer: 'shimmer 1.8s infinite linear',
      },
      keyframes: {
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
    },
  },
  plugins: [require('@tailwindcss/forms'), require('@tailwindcss/typography')],
};
```

---

## 13. CSS Variables para Colores Categoría (Dinámicos)

```css
/* global.css */
:root {
  --color-postre: #FB923C;
  --color-entrada: #4ADE80;
  --color-snack: #FACC15;
  --color-plato-principal: #60A5FA;
  --color-acompanamiento: #C084FC;
  --color-bebida: #22D3EE;
  --color-desayuno: #FB7185;
  --color-sopa-crema: #A3E635;
  --color-ensalada: #34D399;
  --color-horneados: #F87171;
  
  --bg-main: #FAF9F6;
  --text-main: #2D2B28;
  --title-color: #3D4034;
}

.dark {
  --bg-main: #1C1A18;
  --text-main: #E8E5E1;
  --title-color: #C8C4BC;
}

/* Uso en CategoryBadge */
.badge-category {
  background-color: var(--color-[category-slug]);
  border-color: var(--color-[category-slug]);
  color: white;
  border-radius: 2px; /* rounded-sm */
}
```

---

## 14. Definición de Hecho (DoD) UI

| Ítem | Verificación |
|------|--------------|
| **Tokens** | Todos en `tailwind.config.js` + `global.css` |
| **Componentes base** | Button, Badge, Card, Input, Select, Dialog, Sheet, Toast, Tooltip, Avatar, Skeleton |
| **Componentes custom** | CategoryBadge, RatingStars, AuthorAvatar, TagChip, RecipeCard, SearchBar, CookingStepper |
| **Layout** | Navbar (reactivo), Footer persistente, Hero, SearchBar, RecipeGrid, Breadcrumb |
| **Páginas** | Home, Detalle (/receta/:slug), Búsqueda, Auth, Perfil, Favoritos, Mis Recetas, Cooking, 404 |
| **Dark mode** | Toggle funcional, tokens adaptados, sin flash |
| **Skeleton loading** | En TODAS las páginas durante fetch |
| **Infinite scroll** | Home, Búsqueda, Favoritos, Mis Recetas, Perfil autor |
| **Buscador live** | Debounce 300ms, chips activos, limpiar todo |
| **Accesibilidad** | axe-core 0 violations, focus visible, ARIA, skip links, touch targets ≥44px |
| **Responsive** | 320px, 768px, 1024px, 1440px — sin overflow horizontal |
| **Performance** | Lighthouse > 90 (Performance, A11y, Best Practices, SEO, PWA) |
| **Footer** | Persistente en toda la app |
| **404** | Temática, ilustración, CTAs funcionales |

---

**Próximo paso**: Implementar tokens en `tailwind.config.js` + `global.css` → crear componentes base shadcn-svelte → maquetar páginas según `01-pages.md` y `02-components.md`.