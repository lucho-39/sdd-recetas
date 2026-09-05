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

---

## 🔴 PENDIENTES CRÍTICAS (Bloquean ADRs + Arquitectura)

| # | Pregunta | Opciones | Impacto | Recomendación |
|---|----------|----------|---------|---------------|
| **Q3** | **Stack tecnológico** (Frontend + Backend) | **A.** SvelteKit + FastAPI (Python)<br>**B.** Next.js (App Router) + NestJS/Express (TypeScript)<br>**C.** Remix + Go (Chi/Gin)<br>**D.** Astro + Hono (edge) + Go/Python<br>**E.** Vue/Nuxt + Laravel/Django | **TODO**: framework choice, language, ecosystem, hiring, DX, performance | **A o B** por madurez, TypeScript end-to-end, buena DX, PWA support nativo |
| **Q4** | **Estrategia de autenticación** | **A.** Custom JWT (RS256) + refresh rotation + OAuth (Lucia/Auth.js helpers)<br>**B.** Auth.js (NextAuth) completo<br>**C.** Clerk / Supabase Auth / Firebase Auth (managed)<br>**D.** Ory Kratos (self-hosted identity) | **authentication.md**, `02-security.md`, `ADR-003`, session mgmt, OAuth | **A** (custom con Lucia/Auth.js helpers) = control total, sin vendor lock-in, RS256 + rotation ya especificado |
| **Q5** | **Búsqueda unificada** (categoría + tags + texto + ingredientes) | **A.** PostgreSQL nativo (pg_trgm + GIN JSONB) — MVP<br>**B.** Meilisearch (self-hosted) — mejor relevancia, typo-tolerance<br>**C.** Typesense (self-hosted) — similar Meilisearch, más ligero<br>**D.** Elasticsearch/OpenSearch — overkill MVP | `data-model.md` (función `buscar_recetas`), `01-api-design.md`, `search.md`, infra | **A para MVP** (ya implementado en SQL), **B/C evaluar en M3** si UX lo requiere |
| **Q6** | **Deployment target** | **A.** Vercel (FE) + Railway/Render/Fly.io (BE) — managed, scale-to-zero<br>**B.** Docker Compose en VPS (Hetzner/DigitalOcean) — control total, costo fijo<br>**C.** Kubernetes (k3s/managed) — overkill MVP<br>**D.** Cloudflare Pages + Workers — edge, nuevo paradigma | `03-deployment.md`, CI/CD, costs, observabilidad, migrations | **A** para velocidad + costo bajo inicio; **B** si se prefiere control/privacidad |
| **Q7** | **ORM / Data Access** | **A.** Prisma (TypeScript, migraciones, type-safe)<br>**B.** Drizzle ORM (ligero, SQL-like, TypeScript)<br>**C.** sqlc (Go) / PgTyped (TS) — SQL raw + type gen<br>**D.** Raw SQL + migraciones manuales (golang-migrate, dbmate) | `data-model.md`, repositorios, DX, migraciones, team skills | **B (Drizzle)** si TS stack; **A (Prisma)** si prioridad DX/migraciones; **D** si equipo prefiere SQL puro |

---

## 🟡 PENDIENTES IMPORTANTES (Post-MVP o Deciden Detalles)

| # | Pregunta | Opciones | Impacto |
|---|----------|----------|---------|
| Q8 | **IA Generation Provider** | OpenAI (GPT-4o-mini), Anthropic (Haiku), Ollama local, self-hosted (vLLM) | Costos, latencia, privacidad, `ai-generation.md` |
| Q9 | **Almacenamiento de imágenes** (v2+) | S3 (R2/MinIO), Cloudinary, Uploadcare, local filesystem | `data-model.md` (image_url), `03-deployment.md`, costos |
| Q10 | **Monorepo vs Multi-repo** | Turborepo/Nx monorepo (FE+BE+shared), repos separados | CI/CD, type sharing, deploy independence |
| Q11 | **Internacionalización (i18n)** | Solo ES MVP; estructura para EN/PT/IT en v2 (next-intl, i18next, Paraglide) | `ui/`, routing, content, SEO |
| Q12 | **Analytics / Telemetría** | PostHog (self-hosted), Plausible, Umami, custom events (opt-in only) | `02-security.md`, `non-functional-requirements.md` (RNF-05) |
| Q13 | **Email Service** (verificación, reset password) | Resend, SendGrid, Mailgun, AWS SES, Postmark, self-hosted (Postal) | `authentication.md`, infra, costos, deliverability |
| Q14 | **Rate Limiting / WAF** | Arcjet, Cloudflare, custom middleware (Redis), nginx + lua | `02-security.md`, `authentication.md` (RB-AUTH-04) |
| Q15 | **Observabilidad Stack** | Prometheus+Grafana, Datadog, Honeycomb, OpenTelemetry + Tempo/Loki | `03-deployment.md`, `non-functional` (RNF-09) |

---

## 🟢 DECISIONES TÉCNICAS YA TOMADAS (Implícitas en docs actuales)

| Área | Decisión | Documentada en |
|------|----------|----------------|
| Base de datos | PostgreSQL 16+ con pg_trgm, pgcrypto, btree_gin | `data-model.md` |
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

1. **Decidir Q3 (Stack) + Q4 (Auth) + Q5 (Search) + Q6 (Deploy) + Q7 (ORM)** → permite escribir ADR-001 a ADR-004
2. **Escribir ADRs** en `docs/decisions/`
3. **Arquitectura** en `docs/architecture/00-architecture.md` + `01-api-design.md` + `02-security.md`
4. **Completar casos de uso** faltantes en `docs/use-cases/`
5. **UI/UX** en `docs/ui/`
6. **Primera Delta Spec** en `docs/specs/`

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