# Estrategia de pruebas

Este documento describe cómo se prueban los endpoints del backend, con qué
herramientas, cómo se ejecutan las pruebas y qué queda pendiente.

---

## 1. Objetivo y alcance

El objetivo es cubrir con tests automáticos el comportamiento de los
**endpoints importantes de la API** (salud, autenticación, usuarios, recetas,
categorías, etiquetas, ingredientes, favoritos, calificaciones y visitas).

Alcance actual:

- Nivel de prueba: **unitario de endpoint** (se ejercita la capa HTTP + lógica
  del endpoint + acceso a datos real).
- Se prueba el backend FastAPI; el frontend y el panel admin no tienen tests
  en esta etapa.

Fuera de alcance por ahora:

- OAuth (Google/GitHub) — no implementado.
- `forgot-password` / `reset-password` reales (hoy son stubs sin envío de email).
- Endpoints administrativos del panel admin (proyecto separado).

---

## 2. Niveles y enfoque

| Nivel | Qué ejercita | Herramienta |
| ----- | ------------ | ----------- |
| Unitario de endpoint | Ruta HTTP → dependencias → lógica → base de datos | `pytest` + `httpx` + PostgreSQL real |
| (Futuro) Integración E2E | Frontend + API + DB | Playwright / Vitest |

Se optó por probar contra una **base de datos PostgreSQL real** en lugar de
mocks o SQLite porque los modelos usan tipos específicos de PostgreSQL
(`UUID`, `JSONB`, `ENUM` nativo) y se quiere validar el comportamiento real de
SQL. Esto también permite detectar errores de mapper, de SQL y de serialización
que los mocks ocultarían.

---

## 3. Herramientas

| Herramienta | Rol |
| ----------- | --- |
| `pytest` | Runner de pruebas |
| `pytest-asyncio` | Soporte `async/await` (modo `auto`) |
| `httpx.AsyncClient` + `ASGITransport` | Cliente HTTP contra la app ASGI sin levantar servidor |
| PostgreSQL 16 | Base de datos de test (`recetario_test`) |
| `pytest-cov` | Reporte de cobertura (opcional) |

Las dependencias de test están declaradas en `backend/pyproject.toml`
(`[project.optional-dependencies].test`).

---

## 4. Base de datos de pruebas

- Se usa una base dedicada: **`recetario_test`**, derivada de `DATABASE_URL`
  (o de `TEST_DATABASE_URL` si está definida).
- `tests/conftest.py` **crea la base si no existe** y crea el esquema una vez
  por sesión.
- Cada test corre dentro de una **transacción externa con savepoint**
  (`join_transaction_mode="create_savepoint"`). Los `commit()` del código bajo
  prueba liberan el savepoint, no la transacción externa; al terminar el test
  se hace `rollback`. Resultado: aislamiento total y tests independientes del
  orden.

---

## 5. Cómo ejecutar las pruebas

> Importante: el entorno virtual del host (`backend/.venv`) fue generado dentro
> del contenedor, por lo que sus shebangs apuntan a `/app`. Las pruebas deben
> ejecutarse **dentro del contenedor backend**.

### Suite completa

```bash
podman exec recetario-backend sh -c 'cd /app && .venv/bin/python -m pytest'
```

### Un archivo o un test

```bash
podman exec recetario-backend sh -c 'cd /app && .venv/bin/python -m pytest tests/test_auth.py'
podman exec recetario-backend sh -c 'cd /app && .venv/bin/python -m pytest tests/test_recipes.py::test_create_recipe_generates_slug'
```

### Con cobertura

```bash
podman exec recetario-backend sh -c 'cd /app && .venv/bin/python -m pytest --cov=app --cov-report=term-missing'
```

### Requisitos previos

- El contenedor `recetario-postgres` debe estar corriendo y healthy.
- El contenedor `recetario-backend` debe estar corriendo (sus archivos se
  montan desde `./backend`, por lo que los tests usan el código actual).

---

## 6. Convenciones

- Un archivo de tests por recurso: `tests/test_<recurso>.py`.
- Nombres descriptivos: `test_<acción>_<condición>`.
- Fixtures compartidas en `tests/conftest.py` (`client`, `db_session`,
  `user`, `admin_user`, `auth_headers`, `admin_headers`, `category`, `recipe`).
- Factorías reutilizables: `create_user`, `create_category`, `create_recipe`,
  `create_tag`, `create_ingredient`.
- Cada regla de negocio relevante de `docs/requirements/` debe tener al menos
  un caso de prueba (ver `01-test-cases.md`).

---

## 7. Cobertura actual

Estado: **81 tests, 100 % pasando**.

| Área | Archivo | Endpoints cubiertos |
| ---- | ------- | ------------------- |
| Salud | `tests/test_health.py` | `/health`, `/healthz`, `/api/v1/health`, `/api/v1/healthz`, `/api/v1/ready` |
| Autenticación | `tests/test_auth.py` | register, login, refresh, logout, me, change-password, forgot-password, bootstrap-admin |
| Usuarios | `tests/test_users.py` | `GET/PATCH /api/v1/users/me` |
| Recetas | `tests/test_recipes.py` | listar, obtener, crear, actualizar, borrar, similares |
| Categorías | `tests/test_categories.py` | listar, obtener |
| Etiquetas | `tests/test_tags.py` | listar/buscar, populares |
| Ingredientes | `tests/test_ingredients.py` | buscar, categorías, obtener |
| Favoritos | `tests/test_favorites.py` | listar, agregar, quitar, colecciones |
| Calificaciones | `tests/test_ratings.py` | calificar (upsert), agregados, listar |
| Visitas | `tests/test_visits.py` | registrar visita, deduplicación diaria |

---

## 8. Decisiones relevantes

- **PostgreSQL real en tests** en vez de SQLite: los modelos dependen de tipos
  nativos de PostgreSQL.
- **Aislamiento por savepoint** en vez de recrear el esquema por test: más
  rápido y mantiene independencia entre tests.
- **`JWT_ALGORITHM=HS256`** en desarrollo. `podman-compose.yml` forzaba `RS256`
  con un secreto simétrico, lo que rompía la firma de tokens; se alineó con el
  `.env`. El conftest fuerza `HS256` para que los tests no dependan del entorno.
- **Tokens con `jti`**: se agregó un identificador único a los JWT para que la
  rotación de refresh tokens sea observable y el blacklist funcione por token.
- **bcrypt directo** en lugar de `passlib`: `passlib 1.7.4` es incompatible con
  `bcrypt >= 4.1` (falla al inicializar el backend). Se usa `bcrypt` directamente
  manteniendo el formato de hash estándar.

---

## 9. Bugs encontrados y corregidos al construir la suite

La suite expuso varios defectos reales de los endpoints, corregidos junto con
los tests:

1. `core/security.py`: `get_current_active_user` no era una dependencia válida
   de FastAPI (parámetros sin `Depends`), por lo que todos los endpoints
   autenticados fallaban.
2. `endpoints/auth.py`: usaba `uuid4(sub)` en lugar de `UUID(sub)` para ubicar
   al usuario; y `await` sobre `blacklist_token` (función sincrónica).
3. `endpoints/favorites.py`: `selectinload` sin importar; borrado por
   `Favorite.id` inexistente (PK compuesta); conteos por columna inexistente.
4. `endpoints/ratings.py` y `endpoints/visits.py`: referencia incorrecta a
   `result` en lugar de la variable del resultado.
5. `endpoints/ingredients.py`: ordenaba por `usage_count`, columna inexistente.
6. `endpoints/tags.py`: el parámetro de búsqueda `query` quedaba tapado por el
   statement SQL.
7. `models`: relación ambigua `Ingredient.created_by_user` (múltiples FK a
   `users`); `selectinload(User.recipes)` inválido sobre relación `dynamic`.
8. `schemas/recipe.py`: `similar_recipes` no existía en el response model.
9. `schemas/auth.py`: `UserResponse.email` era `EmailStr` y rechazaba el email
   del admin bootstrap (`admin@recetario.local`, TLD reservado).
10. `recipes.py`: el conteo total ignoraba los filtros aplicados.

---

## 10. Próximos pasos

- [ ] Tests para OAuth cuando se implemente.
- [ ] Tests de `forgot-password`/`reset-password` reales (token + email mockeado).
- [ ] Tests de paginación y ordenamientos de recetas (`sort=visited`, `top_rated`).
- [ ] Tests de degradación/errores de base de datos (reintentos, timeouts).
- [ ] Tests del panel admin (proyecto separado).
