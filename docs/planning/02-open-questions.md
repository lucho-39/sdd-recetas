# Preguntas Abiertas y Decisiones Pendientes

> Registro vivo de decisiones técnicas y de producto no resueltas. Cada entrada: pregunta, opciones, impacto, decisión (cuando se toma), fecha.

---

## ✅ RESUELTAS

| # | Pregunta | Decisión | Fecha | Impacto |
|---|----------|----------|-------|---------|
| Q1 | **Plataforma objetivo** | **Mobile-first PWA** (responsive 320px–1920px+, instalable, offline-first para guardados) | 2026-09-05 | Define UI breakpoints, touch targets, PWA requirements, no native apps MVP |
| Q2 | **Catálogo inicial** | **2-3 recetas modelo (seed data)** creadas por sistema; resto user-generated | 2026-09-05 | Define seeding strategy, "Usuario sistema" como autor, content moderation baseline |
| Q16 | **Moderación de contenido** | **Sin moderación en MVP** (confianza en comunidad; reportes/post-MVP) | 2026-09-05 | Simplifica MVP; no requiere panel admin, colas, ML; RNF-04.10 ajustado |
| Q17 | **Visualización de calificación promedio** | **Estrellas fraccionales**: promedio 4.15 → 4 estrellas llenas + 15% de la 5ta estrella rellena | 2026-09-05 | UI precisa; `avg_rating` decimal(3,2) ya soporta; frontend renderiza fill % |
| Q18 | **Alcance social** | **Compartir SÍ** (Web Share API, link copiar); **Seguimiento NO**; **Perfil público** solo muestra recetas publicadas del autor | 2026-09-05 | Simplifica social graph; no followers/following; perfil = card autor + grid recetas |
| Q19 | **Búsqueda por ingrediente** | **Parcial (ILIKE/trigram)** en `ingredients.name`; **Recetas con slug** para SEO (`/receta/<slug>`) | 2026-09-05 | `data-model.md`: slug unique en receta; búsqueda ingredientes usa `jsonb_path_query` + trigram |
| Q3 | **Stack tecnológico** | **Frontend**: SvelteKit (última versión, Svelte 5 runes) — PWA nativo, Vite<br>**Backend**: FastAPI (última versión, Python 3.12+) — REST, Pydantic v2, async<br>**DB**: PostgreSQL 16+ (pg_trgm, pgcrypto, btree_gin)<br>**Auth**: JWT RS256 (access 15min) + Refresh Token opaque (30d, HttpOnly cookie, rotation obligatoria)<br>**Sesiones**: Duración redes sociales (access 15min, refresh 30d rolling, sliding window)<br>**Imágenes**: Preparado (campo `image_url` nullable, esquema S3-compatible) — NO implementado MVP<br>**API**: REST (OpenAPI/Swagger auto-generado por FastAPI)<br>**Contenedores**: Podman — imágenes base AWS (public.ecr.aws/...) — NO Docker Hub<br>**Despliegue**: Podman Compose / Quadlet en VPS | 2026-09-05 | Define todo el stack: lenguaje, framework, DB, auth, contenedores, deployment. Base para ADR-001, ADR-002, ADR-003, ADR-004 |
| Q20 | **Sistema Admin** | **Proyecto separado SvelteKit** (independiente del frontend usuario)<br>**Auth independiente**: usuarios admin ≠ usuarios frontend<br>**Bootstrap admin**: Variables de entorno `ADMIN_INITIAL_USER`, `ADMIN_INITIAL_PASSWORD` → en primer arranque backend crea admin, `must_change_password=true`<br>**Primer login**: Fuerza cambio de contraseña obligatorio<br>**Auth admin**: JWT propio (claims `role: "admin"`), cookies HttpOnly propias, refresh rotation propia **[endpoints /api/admin/* pendientes]** | 2026-09-05 | Admin desacoplado del frontend; bootstrap por env (container-friendly); force password change; auth aislado |
| Q22 | **Color por categoría** | Campo `color` VARCHAR(7) Hex (#RRGGBB) en `categoria` — seed data con colores shadcn-svelte compatibles light/dark mode | 2026-09-05 | Badge UI consistente en cards y detalle; shadcn-svelte `Badge` component usa color para variant custom |

---

## 🔴 PENDIENTES CRÍTICAS (Bloquean ADRs + Arquitectura)

| # | Pregunta | Opciones | Impacto | Recomendación |
|---|----------|----------|---------|---------------|
| **Q7** | **ORM / Data Access (Python/FastAPI)** ✅ RESUELTA | **A.** SQLAlchemy 2.0 (async) + Alembic — estándar, maduro, type hints<br>**B.** SQLModel (basado en SQLAlchemy + Pydantic) — integra bien con FastAPI<br>**C.** Raw SQL + asyncpg + migraciones manuales (golang-migrate/dbmate) — control total<br>**D.** Prisma/Drizzle — no son Python-native | `data-model.md`, repositorios, DX, migraciones, team skills | **A** (SQLAlchemy 2.0 async + Alembic) = estándar Python, maduro, type hints, integra con Pydantic v2/FastAPI, Alembic para migraciones |

---

## 🟡 PENDIENTES IMPORTANTES (Post-MVP o Deciden Detalles)

| # | Pregunta | Opciones | Impacto |
|---|----------|----------|---------|
| Q8 | **IA Generation Provider** | OpenAI (GPT-4o-mini), Anthropic (Haiku), Ollama local, self-hosted (vLLM) | Costos, latencia, privacidad, `ai-generation.md` |
| Q9 | **Almacenamiento de imágenes** (v2+) | S3 (R2/MinIO), Cloudinary, Uploadcare, local filesystem | `data-model.md` (image_url), `03-deployment.md`, costos |
| Q10 | **Monorepo vs Multi-repo** | **A.** Monorepo (Turborepo/Nx) — FE usuario + FE admin + BE + shared types<br>**B.** Multi-repo — 3 repos separados (frontend, admin, backend)<br>**C.** Mono-repo parcial — FE+BE juntos, admin separado | CI/CD, type sharing, deploy independence, admin auth isolation |
| Q11 | **Internacionalización (i18n)** | Solo ES MVP; estructura para EN/PT/IT en v2 (next-intl, i18next, Paraglide) | `ui/`, routing, content, SEO |
| Q12 | **Analytics / Telemetría** | PostHog (self-hosted), Plausible, Umami, custom events (opt-in only) | `02-security.md`, `non-functional-requirements.md` (RNF-05) |
| Q13 | **Email Service** (verificación, reset password) | Resend, SendGrid, Mailgun, AWS SES, Postmark, self-hosted (Postal) | `authentication.md`, infra, costos, deliverability |
| Q14 | **Rate Limiting / WAF** | Arcjet, Cloudflare, custom middleware (Redis), nginx + lua | `02-security.md`, `authentication.md` (RB-AUTH-04) |
| Q15 | **Observabilidad Stack** | Prometheus+Grafana, Datadog, Honeycomb, OpenTelemetry + Tempo/Loki | `03-deployment.md`, `non-functional` (RNF-09) |
| Q21 | **Estructura proyecto Admin** | **A.** SvelteKit app separada en monorepo (compartir types/utils con frontend)<br>**B.** SvelteKit app en repo aparte (deploy independiente, auth totalmente aislado) | Q10, `03-deployment.md`, CI/CD, shared types |

---

## 🟢 DECISIONES TÉCNICAS YA TOMADAS (Implícitas en docs actuales)

| Área | Decisión | Documentada en |
|------|----------|----------------|
| **Frontend** | SvelteKit (Svelte 5 runes) — PWA nativo, Vite, TypeScript | `vision.md`, `planning/02-open-questions.md` (Q3) |
| **Backend** | FastAPI (Python 3.12+) — REST, Pydantic v2, async, OpenAPI auto | `planning/02-open-questions.md` (Q3) |
| **Base de datos** | PostgreSQL 16+ con pg_trgm, pgcrypto, btree_gin | `data-model.md` |
| **Auth (Frontend)** | JWT **HS256** (access 15min) + Refresh Token **JWT HS256** (30d, HttpOnly cookie, rotación). RS256 + opaque quedan v2 (ver ADR-000) | `authentication.md`, `decisions/ADR-000-source-of-truth.md` |
| **Auth (Admin)** | **Proyecto SvelteKit separado** — auth propia; los endpoints `/api/admin/*` están pendientes | `planning/02-open-questions.md` (Q20), `use-cases/admin.md` |
| **OAuth** | Google + GitHub (FastAPI backend callback + Lucia en SvelteKit frontend) | `planning/02-open-questions.md` (Q4) |
| **Bootstrap Admin** | Variables de entorno `ADMIN_INITIAL_EMAIL`, `ADMIN_INITIAL_PASSWORD` → crea admin en primer arranque, `force_password_change=true` | `planning/02-open-questions.md` (Q20) |
| **Sesiones** | Duración redes sociales: access 15min, refresh 30d rolling, sliding window | `planning/02-open-questions.md` (Q3) |
| **Imágenes** | Preparado (`image_url` nullable, esquema S3-compatible) — NO implementado MVP | `entities.md`, `planning/02-open-questions.md` (Q3) |
| **API** | REST (OpenAPI/Swagger auto-generado por FastAPI) | `planning/02-open-questions.md` (Q3) |
| **Contenedores** | Podman — imágenes base AWS ECR Public (`public.ecr.aws/...`) — NO Docker Hub | `planning/02-open-questions.md` (Q3) |
| **Deployment** | VPS (Hetzner/DigitalOcean) + Podman Compose / Quadlet | `planning/02-open-questions.md` (Q6) |
| **ORM** | **SQLAlchemy 2.0 async + Alembic** (estándar Python, maduro, type hints, migraciones) | `planning/02-open-questions.md` (Q7) |
| **Búsqueda** | PostgreSQL nativo (pg_trgm + GIN JSONB) — MVP | `data-model.md`, `planning/02-open-questions.md` (Q5) |
| Soft delete | `deleted_at` en recetas; usuario sistema para anonimización | `entities.md`, `data-model.md` |
| Baja usuario | Lógica (`is_active`), reactivable, GDPR irreversible | `business-rules.md` (RB-AUTH-08/09/10) |
| Visitas | Únicas por día por visitante (fingerprint/cookie + salt diario) | `business-rules.md` (RB-04), `data-model.md` |
| Favoritos | Colecciones (default "Favoritos" + custom), contadores denormalizados | `business-rules.md` (RB-05) |
| Tags | Abiertos, autocomplete prefix + usage_count ranking | `business-rules.md` (RB-02, RB-07) |
| Categorías | Cerradas (8 seed), admin-only CRUD | `entities.md`, `data-model.md` |
| Calificaciones | 1-5 estrellas + reseña, una por usuario/receta, denormalizado | `business-rules.md` (RB-06) |
| PWA | Instalable, service worker, offline para guardados | `vision.md`, `non-functional` (RNF-07) |
| Accesibilidad | WCAG 2.1 AA obligatorio | `non-functional` (RNF-06) |

---

## 📝 PRÓXIMOS PASOS INMEDIATOS

1. **Definir Q10 (Monorepo vs Multi-repo) + Q21 (Estructura Admin)** → impacta estructura de repos, CI/CD, shared types
2. **Escribir ADRs** en `docs/decisions/`: ADR-001 (Tech Stack), ADR-002 (Database), ADR-003 (Auth + Admin Auth), ADR-004 (Search), ADR-005 (Deployment), ADR-006 (ORM)
3. **Arquitectura** en `docs/architecture/`: `00-architecture.md` (C4 nivel 1-2), `01-api-design.md` (OpenAPI), `02-security.md` (authN/authZ user + admin), `03-deployment.md` (Podman + VPS)
4. **Completar casos de uso** faltantes en `docs/use-cases/`: `recipes.md`, `favorites.md`, `social.md`, `ratings.md`, `auth.md`, `admin.md`, `ai-generation.md`, `cooking-mode.md`, `visit-tracking.md`, `ingredients.md`
5. **UI/UX** en `docs/ui/`: `00-ui-overview.md`, `01-pages.md`, `02-components.md`, `03-design-system.md`
6. **Primera Delta Spec** en `docs/specs/`: `TEMPLATE.md` + `auth-system.md` (primer change)

---

## 📌 NOTAS PARA Q3 (Stack) — Contexto Mobile-First PWA

| Factor | SvelteKit + FastAPI | Next.js + NestJS | Remix + Go |
|--------|---------------------|------------------|------------|
| **PWA/Offline** | Excelente (Vite PWA plugin, service worker nativo) | Excelente (next-pwa, workbox) | Bueno (Vite PWA) |
| **Mobile DX** | Muy buena (menor bundle, sin VDOM) | Buena (RSC puede complicar offline) | Buena |
| **TypeScript E2E** | Sí (Svelte 5 + TS + FastAPI/Pydantic) | Sí (nativo) | Sí (Go + TS) |
| **Ecosistema Auth** | Lucia (Svelte), Auth.js (SvelteKit) | Auth.js (NextAuth), Clerk | Lucia, go-jwt |
| **Bundle Size** | ~Smallest | Medium (RSC overhead) | Small |
| **Learning Curve** | Baja (Svelte 5 runes) | Media (App Router, RSC) | Media (Go) |
| **Hiring/Community** | Creciente | Muy grande | Creciente |
| **Recomendación** | **Fuerte candidata** si equipo prefiere simplicidad + performance | **Fuerte candidata** si equipo prefiere React ecosystem + enterprise | Buena si equipo Go + quiere control total |

---

**Última actualización**: 2026-09-05  
**Próxima revisión**: Tras decidir Q3-Q7