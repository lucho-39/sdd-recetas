# UI Overview — Recetario IA

## Visión General

Aplicación **mobile-first PWA** para descubrir, guardar y cocinar recetas. Interfaz limpia, rápida y accesible (WCAG 2.1 AA), construida con **SvelteKit 5 + shadcn-svelte + Tailwind CSS**.

---

## Principios de Diseño

| Principio | Descripción |
|-----------|-------------|
| **Contenido primero** | La receta es la protagonista; UI invisible, sin ruido visual |
| **Mobile-first** | Breakpoints: `sm: 640px`, `md: 768px`, `lg: 1024px`, `xl: 1280px` |
| **Velocidad percibida** | Skeleton loaders, lazy images, optimistic UI, cache agresivo |
| **Accesibilidad real** | Contraste 4.5:1, focus visible, ARIA labels, touch targets 44×44px |
| **Consistencia** | Design tokens centralizados, componentes shadcn-svelte como base |
| **Modo oscuro nativo** | `class` strategy en Tailwind, todos los tokens tienen variante dark |

---

## Arquitectura de Páginas (Mapa del Sitio)

```
/                          → Home: Hero + Buscador + Grid recetas
/receta/:slug              → Detalle receta (ingredientes, pasos, autor, rating, etc.)
/buscar                    → Búsqueda avanzada (sidebar filtros + grid resultados)
/mis-recetas               → CRUD propias (tabs: Publicadas / Privadas / Borradas)
/mis-favoritos             → Colecciones + grid guardados
/perfil                    → Perfil usuario + acciones (editar, avatar, baja)
/login                     → Login email/password + OAuth
/register                  → Registro + verificación email
/usuario/:id               → Perfil público autor + grid recetas publicadas
/cooking/:slug             → Modo cocinando (fullscreen, wake lock, swipe/voz)

--- Admin (proyecto separado) ---
/admin                     → Dashboard métricas
/admin/categorias          → CRUD categorías
/admin/usuarios            → Gestión usuarios + reactivación/GDPR
/admin/ingredientes        → Validación catálogo (pendientes, merge, rechazar)
/admin/metricas            → Dashboard global, contenido, usuarios
/admin/config              → Feature flags, rate limits, email templates, mantenimiento
```

---

## Breakpoints & Layout

| Breakpoint | Ancho | Uso principal |
|------------|-------|---------------|
| `base` (mobile) | < 640px | Stack vertical, sidebar colapsable, grid 1 col |
| `sm` | 640px | Grid 2 cols, navbar compacto |
| `md` | 768px | Sidebar fija, grid 3 cols |
| `lg` | 1024px | Grid 4 cols, navegación lateral expandida |
| `xl` | 1280px | Max-width container 1200px, sidebar ancha |

---

## Estados Globales

| Estado | Descripción | Componentes afectados |
|--------|-------------|----------------------|
| **Autenticado** | Usuario con access token válido | Navbar, Botones guardar/calificar, Mis recetas, Favoritos |
| **No autenticado** | Visitante anónimo | Navbar (Login/Register), CTAs login en acciones protegidas |
| **Cargando** | Skeleton loaders globales | Grid recetas, buscador, detalle, perfiles |
| **Error** | Toast global + fallback UI | Cualquier fetch fallido |
| **Offline** | Service worker + cache | Guardados disponibles, banner "Modo offline" |

---

## Design Tokens (Referencia rápida)

| Token | Valor | Uso |
|-------|-------|-----|
| **Colores categoría** | Ver `domain/entities.md` → Categoría.color | Badges, chips, acentos |
| **Primary** | `#3D4034` / `#A8A4A0` (dark olive) | CTAs principales, links |
| **Destructive** | `#B84A3A` / `#D47A6A` | Eliminar, acciones peligrosas |
| **Success** | `#5A7D4A` / `#7AB86A` | Guardado, confirmaciones |
| **Warning** | `#C47A2A` / `#D4A84A` | Advertencias, baja cuenta |
| **Radius** | `2px` badges, `4px` inputs/botones, `6px` cards | Consistencia visual |
| **Shadow** | `shadow-sm` cards, `shadow-lg` modales/dropdowns | Jerarquía profundidad |
| **Spacing** | base 4px; `space-y-4` vertical, `gap-4` grid | Ritmo visual |
| **Typography** | `Playfair Display` (títulos), `Inter` (cuerpo) | Legibilidad |

> Estos tokens siguen a `03-design-system.md` (paleta warm/olive). Una versión
> anterior de este archivo proponía indigo/slate; quedó obsoleta.

---

## Componentes Base (shadcn-svelte + custom)

Ver `docs/ui/02-components.md` para especificación completa.

| Componente | Base shadcn | Customizaciones |
|------------|-------------|-----------------|
| `Button` | ✅ | Variants: `primary`, `secondary`, `ghost`, `destructive`, `outline` |
| `Badge` | ✅ | Variant `category` (usa `category.color`), `rating` (estrellas fraccionales) |
| `Card` | ✅ | `RecipeCard` (imagen, badges categoría, rating, favoritos, autor) |
| `Input` / `Textarea` | ✅ | Con label flotante, error state, icon leading/trailing |
| `Select` / `Combobox` | ✅ | `CategorySelect`, `TagAutocomplete`, `IngredientSelector` |
| `Sheet` / `Drawer` | ✅ | Sidebar móvil (filtros, navegación), modal compartir |
| `Dialog` / `AlertDialog` | ✅ | Confirmaciones (borrar, baja, GDPR) |
| `DropdownMenu` | ✅ | Navbar usuario, acciones receta (editar, borrar, compartir) |
| `Avatar` | ✅ | Fallback iniciales, upload futuro |
| `Skeleton` | ✅ | `RecipeCardSkeleton`, `SearchSkeleton`, `DetailSkeleton` |
| `Toast` / `Sonner` | ✅ | Notificaciones globales (éxito, error, info) |
| `Tooltip` | ✅ | Iconos info, truncamiento texto |
| `Pagination` / `InfiniteScroll` | ✅ | Grid recetas, listados paginados |
| `RatingStars` | Custom | Estrellas fraccionales (fill % basado en `avg_rating`) |
| `CategoryBadge` | Custom | Usa `category.color` + icon, variant `outline` con color custom |
| `IngredientSelector` | Custom | Autocomplete catálogo 300 items + crear nuevo + cantidad/unidad/notas |
| `CookingStepper` | Custom | Fullscreen, wake lock, swipe/voz, timer por paso |
| `NotificationBell` | Custom | Campanita con badge de no leídas + dropdown (Socket.IO en tiempo real) |

---

## Próximos Documentos

1. **`01-pages.md`** — Definición detallada de cada pantalla (Home, Detalle, Búsqueda, Auth, Perfil, Cooking, Admin)
2. **`02-components.md`** — Especificación completa de cada componente (props, states, a11y, variants)
3. **`03-design-system.md`** — Design tokens completos, paleta, tipografía, espaciado, dark mode, animaciones