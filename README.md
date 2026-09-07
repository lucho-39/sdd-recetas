# Recetario IA - Proyecto SDD

Aplicación de recetas de cocina construida con **Spec-Driven Development (SDD)** usando **SvelteKit + FastAPI + PostgreSQL**.

## 📋 Descripción

Aplicación mobile-first PWA para gestión de recetas de cocina con:
- **Búsqueda unificada** (nombre, ingredientes, categorías, tags)
- **Sistema de favoritos y colecciones**
- **Calificaciones y reseñas** con estrellas fraccionales
- **Modo cocinando** (fullscreen, wake lock, comandos de voz, timers)
- **Generación de recetas por IA** a partir de ingredientes
- **Panel de administración** independiente con auth separado
- **Catálogo de 300 ingredientes normalizados** con autocomplete

## 🏗️ Stack Tecnológico

| Capa | Tecnología |
|------|------------|
| **Frontend (User)** | SvelteKit 2.x + Svelte 5 (runes) + TypeScript |
| **Frontend (Admin)** | SvelteKit 2.x (proyecto separado) |
| **Backend** | FastAPI 0.115+ (Python 3.12+) |
| **Base de Datos** | PostgreSQL 16+ (pg_trgm, pgcrypto, btree_gin) |
| **ORM** | SQLAlchemy 2.0 async + Alembic |
| **Auth** | JWT RS256 (access 15min) + Refresh opaque 30d (HttpOnly cookie) |
| **OAuth** | Google + GitHub |
| **Contenedores** | Podman + Podman Compose / Quadlet |
| **Imágenes Base** | AWS ECR Public (`public.ecr.aws/...`) |
| **Deployment** | VPS (Hetzner/DigitalOcean) + Podman Compose / Quadlet |
| **Monorepo** | Turborepo (`apps/frontend`, `apps/admin`, `apps/backend`, `packages/shared`) |

## 🎨 Diseño & UX

- **Tema**: Warm palette (`#FAF9F6` fondo, sin blancos/negros puros)
- **Tipografía**: Playfair Display (serif, títulos) + Inter (sans, cuerpo)
- **Colores**: 10 categorías con Tailwind 400 tones (light/dark compatible)
- **Radios mínimos**: 2px badges, 4px inputs, 6px cards
- **Sombras tenues**: Warm charcoal alpha 0.04-0.1
- **Dark mode**: Class strategy, tokens adaptados
- **Accesibilidad**: WCAG 2.1 AA, focus visible, ARIA, touch targets ≥44px
- **Skeleton loading**: Global en toda la app
- **Scroll infinito**: En todos los grids

## 🚀 Inicio Rápido

### Prerrequisitos
- Podman instalado
- Node.js 20+ y pnpm
- Python 3.12+ (para desarrollo local)

### Desarrollo Local

```bash
# Clonar repo
git clone https://github.com/lucho-39/sdd-recetas.git
cd sdd-recetas

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores

# Levantar servicios con Podman
podman-compose up --build

# Verificar servicios
# Frontend: http://localhost:3000
# Admin: http://localhost:3001
# Backend API: http://localhost:8000/docs
```

### Variables de Entorno Principales

```bash
# .env
ENVIRONMENT=development
POSTGRES_USER=recetario
POSTGRES_PASSWORD=changeme_secure_password_here
POSTGRES_DB=recetario
JWT_SECRET=generate_a_strong_random_secret_at_least_32_chars_long
JWT_ALGORITHM=HS256
ADMIN_INITIAL_USER=admin@recetario.local
ADMIN_INITIAL_PASSWORD=ChangeMeOnFirstLogin123!
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

## 🐳 Despliegue con Podman

```bash
# Build y deploy
podman-compose -f podman-compose.yml up -d --build

# Ver logs
podman-compose logs -f backend

# Migrations (ejecutar en contenedor backend)
podman exec recetario-backend uv run alembic upgrade head

# Backup BD
podman exec recetario-postgres pg_dump -U recetario recetario > backup.sql
```

## 📁 Estructura del Monorepo

```
sdd-recetas/
├── podman-compose.yml          # Orquestación contenedores
├── .env.example                # Variables de entorno ejemplo
├── .gitignore                  # Git ignore exhaustivo
├── docs/                       # Documentación SDD completa
│   ├── vision/                 # Visión, objetivos, scope
│   ├── domain/                 # Modelo de dominio, entidades, BD
│   ├── requirements/           # Reglas negocio, reqs funcionales/no-funcionales
│   ├── use-cases/              # Casos de uso (user, admin, search, etc.)
│   ├── ui/                     # Design system, páginas, componentes
│   ├── planning/               # Roadmap, open questions, ADRs
│   └── architecture/           # ADRs, arquitectura C4, API design
├── backend/                    # FastAPI App
│   ├── Containerfile
│   ├── pyproject.toml
│   ├── app/
│   │   ├── core/               # Config, DB, Security
│   │   ├── models/             # SQLAlchemy models
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── api/v1/             # Endpoints REST
│   │   │   ├── endpoints/      # Auth, recipes, users, etc.
│   │   │   └── router.py
│   │   ├── main.py             # FastAPI app + lifespan
│   │   └── api/v1/router.py
│   └── alembic/                # Migraciones
├── frontend/                   # SvelteKit User App (puerto 3000)
│   ├── svelte.config.js
│   ├── vite.config.ts
│   ├── src/
│   │   ├── routes/             # +layout.svelte, +page.svelte
│   │   ├── lib/
│   │   │   ├── components/     # UI components (Button, Card, etc.)
│   │   │   ├── stores/         # Svelte stores (auth, recipes, theme)
│   │   │   ├── types/          # TypeScript types
│   │   │   └── utils/          # Helpers
│   │   └── app.html / app.css
│   └── Containerfile
├── admin/                      # SvelteKit Admin App (puerto 3001)
│   ├── svelte.config.js
│   ├── src/
│   │   ├── routes/
│   │   │   ├── +layout.svelte
│   │   │   └── admin/          # Dashboard, usuarios, recetas, ingredientes
│   │   ├── lib/
│   │   │   ├── components/     # Admin UI components
│   │   │   ├── stores/         # Auth admin store
│   │   │   └── types/
│   │   └── app.css / app.html
│   └── Containerfile
└── .data/                      # Persistencia PostgreSQL (bind mount)
    └── postgres/
```

## 🔐 Autenticación

### Usuario (Frontend)
- **Access Token**: JWT RS256, 15 min, en memoria
- **Refresh Token**: Opaco 30 días, HttpOnly cookie, rotación obligatoria
- **OAuth**: Google + GitHub (backend callback)
- **Bootstrap Admin**: Variables `ADMIN_INITIAL_USER` + `ADMIN_INITIAL_PASSWORD` → `force_password_change=true`

### Admin (Proyecto Separado)
- **Proyecto SvelteKit independiente** (`recetario-admin`)
- **Auth independiente**: JWT RS256 propio (`role: "admin"`)
- **Cookies separadas**: `Path=/admin` o subdominio `admin.recetario.com`
- **Bootstrap**: Variables `ADMIN_INITIAL_*` → force password change en primer login

## 🗄️ Base de Datos - Esquema Principal

```sql
-- 10 Categorías predefinidas
postre, entrada, snack, plato-principal, acompañamiento, bebida, desayuno, sopa-crema, ensalada, horneados

-- Tablas principales
users, categories, tags, recipes, recipe_tags, favorites, visits, ratings, ingredients

-- Características clave
- UUID primary keys
- Soft deletes (deleted_at)
- JSONB para ingredients (FK a catálogo)
- Full-text search con pg_trgm
- Triggers para contadores denormalizados (visit_count, save_count, avg_rating)
- Soft delete admin con anonimización GDPR
```

## 🔍 Búsqueda Unificada

```
GET /api/recipes?category=postre&tags=vegano,sin-tacc&ingredients=almendra&q=brownie
```

- **AND** entre dimensiones (categoría, tags, ingredientes, texto)
- **OR** dentro de cada dimensión multi-valor
- **Debounce 300ms** en frontend
- **Chips removibles** + "Limpiar todo"
- **Slug SEO**: `/receta/<slug>` (ej: `/receta/tortilla-patatas-clasica-a1b2`)

## 🧪 Testing

```bash
# Backend
cd backend && uv run pytest --cov=app --cov-report=html

# Frontend
cd frontend && pnpm run check && pnpm test

# Admin
cd admin && pnpm run check

# E2E
pnpm run test:e2e
```

## 📦 Comandos Útiles

```bash
# Desarrollo
podman-compose up --build          # Levantar todo
podman-compose logs -f backend     # Logs backend
podman exec -it recetario-backend bash  # Shell backend

# Migraciones
cd backend && uv run alembic revision --autogenerate -m "descripción"
cd backend && uv run alembic upgrade head

# Linting
cd frontend && pnpm run lint
cd admin && pnpm run lint
cd backend && uv run ruff check .

# Formatting
cd frontend && pnpm run format
cd admin && pnpm run format
cd backend && uv run ruff format .
```

## 🔐 Seguridad

- ✅ JWT RS256 (asymmetric) con rotación de claves
- ✅ Refresh token rotación + detección robo (blacklist)
- ✅ HttpOnly + Secure + SameSite=Lax cookies
- ✅ Rate limiting (login: 5/15min, register: 5/15min)
- ✅ CORS restringido a orígenes permitidos
- ✅ Rate limiting por IP/usuario
- ✅ Password policy: 8 chars, 1 mayús, 1 minús, 1 num, 1 especial
- ✅ Bcrypt/Argon2 para hash de contraseñas
- ✅ CSP, HSTS, X-Frame-Options headers
- ✅ No secrets en repo (`.gitignore` exhaustivo)

## 📚 Documentación SDD

La documentación completa está en `docs/` siguiendo el flujo SDD:
1. **Vision** → Problema, usuarios, objetivos, scope
2. **Domain** → Modelo conceptual, entidades, BD
3. **Requirements** → Business rules, RF/RNF, User stories, Auth spec
4. **Use Cases** → Flujos detallados (Search, Admin, Auth, etc.)
5. **UI/UX** → Design system, páginas, componentes, design tokens
6. **Planning** → Open questions, roadmap, ADRs
7. **Architecture** → ADRs, C4 diagrams, API design, Security, Deployment

## 🤝 Contribuir

1. Fork del repo
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit con mensajes convencionales (`feat:`, `fix:`, `docs:`, etc.)
3. Push y abrir Pull Request
4. Review y merge tras CI passing

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE) para detalles.

---

**¿Preguntas?** Abre un [issue](https://github.com/lucho-39/sdd-recetas/issues) o revisa la [documentación completa](docs/).