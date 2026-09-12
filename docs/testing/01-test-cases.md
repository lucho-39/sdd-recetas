# Casos de prueba

Catálogo de los casos de prueba de los endpoints del backend. Cada caso indica
el endpoint, la condición evaluada y el test que lo implementa.

Estado actual: **81 casos, todos en verde** (ver `00-strategy.md` para correr la suite).

---

## Convención de IDs

`<ÁREA>-<n>` donde ÁREA es H (health), A (auth), U (users), R (recipes),
C (categories), T (tags), I (ingredients), F (favorites), RT (ratings),
V (visits).

---

## 1. Health — `tests/test_health.py`

| ID | Endpoint | Caso | Resultado esperado | Test |
| -- | -------- | ---- | ------------------ | ---- |
| H-1 | `GET /health` | Liveness raíz | 200, `status=healthy`, `service=recetario-backend` | `test_root_health` |
| H-2 | `GET /healthz` | Liveness raíz (k8s) | 200, `status=ok` | `test_root_healthz` |
| H-3 | `GET /api/v1/health` | Liveness bajo prefijo API | 200, `status=healthy` | `test_v1_health` |
| H-4 | `GET /api/v1/healthz` | Liveness bajo prefijo (k8s) | 200, `status=ok` | `test_v1_healthz` |
| H-5 | `GET /api/v1/ready` | Readiness con DB | 200, `status=ready`, `database=connected` | `test_ready_reports_database_connected` |

---

## 2. Autenticación — `tests/test_auth.py`

| ID | Endpoint | Caso | Resultado esperado | Test |
| -- | -------- | ---- | ------------------ | ---- |
| A-1 | `POST /auth/register` | Registro válido | 201; usuario creado; `is_verified=false` | `test_register_creates_unverified_user` |
| A-2 | `POST /auth/register` | Email ya registrado | 400 | `test_register_rejects_duplicate_email` |
| A-3 | `POST /auth/register` | Email con formato inválido | 422 | `test_register_validates_email_format` |
| A-4 | `POST /auth/register` | Contraseña demasiado corta | 422 | `test_register_validates_password_length` |
| A-5 | `POST /auth/login` | Credenciales válidas | 200; access token; cookie `refresh_token` | `test_login_returns_token_and_sets_refresh_cookie` |
| A-6 | `POST /auth/login` | Contraseña incorrecta | 401 | `test_login_rejects_wrong_password` |
| A-7 | `POST /auth/login` | Email inexistente | 401 | `test_login_rejects_unknown_email` |
| A-8 | `POST /auth/login` | Usuario no verificado | 403 | `test_login_rejects_unverified_user` |
| A-9 | `GET /auth/me` | Token válido | 200; `email` y `role=user` | `test_me_returns_current_user` |
| A-10 | `GET /auth/me` | Sin credenciales | 401 | `test_me_requires_authentication` |
| A-11 | `GET /auth/me` | Token inválido | 401 | `test_me_rejects_invalid_token` |
| A-12 | `POST /auth/refresh` | Refresh válido | 200; nuevo access token distinto; nueva cookie | `test_refresh_rotates_tokens` |
| A-13 | `POST /auth/refresh` | Sin cookie de refresh | 401 | `test_refresh_without_cookie_fails` |
| A-14 | `POST /auth/change-password` | Cambio válido | 200; login con la nueva contraseña | `test_change_password_updates_credentials` |
| A-15 | `POST /auth/change-password` | Contraseña actual incorrecta | 400 | `test_change_password_rejects_wrong_current` |
| A-16 | `POST /auth/logout` | Logout | 200 | `test_logout_returns_success` |
| A-17 | `POST /auth/forgot-password` | Email conocido vs. inexistente | 200 idéntico (no filtra existencia) | `test_forgot_password_never_leaks_account_existence` |
| A-18 | `POST /auth/bootstrap-admin` | Bootstrap idempotente | 201 (2×); admin `must_change_password=true`; login OK; `/me` OK con TLD reservado | `test_bootstrap_admin_creates_admin_and_is_idempotent` |

---

## 3. Usuarios — `tests/test_users.py`

| ID | Endpoint | Caso | Resultado esperado | Test |
| -- | -------- | ---- | ------------------ | ---- |
| U-1 | `GET /users/me` | Perfil autenticado | 200; `id`, `email`, `display_name` | `test_get_me_returns_profile` |
| U-2 | `GET /users/me` | Sin credenciales | 401 | `test_get_me_requires_authentication` |
| U-3 | `PATCH /users/me` | Actualizar `display_name` | 200; valor actualizado | `test_patch_me_updates_display_name` |
| U-4 | `PATCH /users/me` | Actualizar `avatar_url` | 200; persiste (GET posterior) | `test_patch_me_updates_avatar_and_persists` |
| U-5 | `PATCH /users/me` | Sin credenciales | 401 | `test_patch_me_requires_authentication` |

---

## 4. Recetas — `tests/test_recipes.py`

| ID | Endpoint | Caso | Resultado esperado | Test |
| -- | -------- | ---- | ------------------ | ---- |
| R-1 | `GET /recipes` | Sin credenciales | 401 | `test_list_recipes_requires_authentication` |
| R-2 | `GET /recipes` | Listar públicas | 200; `total=1`; receta presente | `test_list_recipes_returns_public_recipes` |
| R-3 | `GET /recipes` | Excluir privadas | `total=0` | `test_list_recipes_excludes_private_recipes` |
| R-4 | `GET /recipes?query=` | Búsqueda por texto | Coincide; 0 si no hay match | `test_list_recipes_filters_by_query` |
| R-5 | `GET /recipes?category=` | Filtro por categoría | `total=1` | `test_list_recipes_filters_by_category` |
| R-6 | `GET /recipes/{slug}` | Detalle por slug | 200; `slug`, `title` | `test_get_recipe_by_slug` |
| R-7 | `GET /recipes/{slug}` | Slug inexistente | 404 | `test_get_unknown_recipe_returns_404` |
| R-8 | `POST /recipes` | Crear receta | 201; slug autogenerado; `similar_recipes=[]` | `test_create_recipe_generates_slug` |
| R-9 | `POST /recipes` | Título duplicado | 201; slug desambiguado (`-2`) | `test_create_recipe_disambiguates_duplicate_slug` |
| R-10 | `POST /recipes` | Título similar | 201; `similar_recipes` incluye la existente | `test_create_recipe_suggests_similar_titles` |
| R-11 | `POST /recipes` | Categoría inexistente | 400 | `test_create_recipe_rejects_unknown_category` |
| R-12 | `POST /recipes` | Sin credenciales | 401 | `test_create_recipe_requires_authentication` |
| R-13 | `PATCH /recipes/{slug}` | Editar la propia | 200; campo actualizado | `test_update_own_recipe` |
| R-14 | `PATCH /recipes/{slug}` | Cambio de título | 200; slug regenerado | `test_update_recipe_regenerates_slug_on_title_change` |
| R-15 | `PATCH /recipes/{slug}` | Editar receta ajena | 404 | `test_update_other_users_recipe_returns_404` |
| R-16 | `DELETE /recipes/{slug}` | Borrar la propia | 204; luego GET 404 (soft delete) | `test_delete_recipe_soft_deletes` |
| R-17 | `DELETE /recipes/{slug}` | Borrar receta ajena | 404 | `test_delete_other_users_recipe_returns_404` |
| R-18 | `GET /recipes/{slug}/similar` | Buscar similares | 200; incluye slug similar | `test_find_similar_recipes` |

---

## 5. Categorías — `tests/test_categories.py`

| ID | Endpoint | Caso | Resultado esperado | Test |
| -- | -------- | ---- | ------------------ | ---- |
| C-1 | `GET /categories` | Listar activas | 200; incluye la categoría | `test_list_categories_returns_active_categories` |
| C-2 | `GET /categories` | Excluir inactivas | No incluye inactiva | `test_list_categories_excludes_inactive` |
| C-3 | `GET /categories` | Sin credenciales | 401 | `test_list_categories_requires_authentication` |
| C-4 | `GET /categories/{slug}` | Detalle | 200; `name` | `test_get_category_by_slug` |
| C-5 | `GET /categories/{slug}` | Slug inexistente | 404 | `test_get_unknown_category_returns_404` |

---

## 6. Tags — `tests/test_tags.py`

| ID | Endpoint | Caso | Resultado esperado | Test |
| -- | -------- | ---- | ------------------ | ---- |
| T-1 | `GET /tags` | Sin credenciales | 401 | `test_list_tags_requires_authentication` |
| T-2 | `GET /tags` | Solo con uso | Incluye `usage>0`; excluye `usage=0` | `test_list_tags_returns_only_used_tags` |
| T-3 | `GET /tags?query=` | Búsqueda | Solo coincidencias | `test_list_tags_filters_by_query` |
| T-4 | `GET /tags/popular` | Ranking por uso | Mayor uso primero | `test_popular_tags_are_ordered_by_usage` |

---

## 7. Ingredientes — `tests/test_ingredients.py`

| ID | Endpoint | Caso | Resultado esperado | Test |
| -- | -------- | ---- | ------------------ | ---- |
| I-1 | `GET /ingredients` | Sin credenciales | 401 | `test_search_ingredients_requires_authentication` |
| I-2 | `GET /ingredients` | Solo activos | Excluye inactivos | `test_search_ingredients_returns_active_ingredients` |
| I-3 | `GET /ingredients?query=` | Coincidencia por nombre | Devuelve el ingrediente | `test_search_ingredients_matches_name` |
| I-4 | `GET /ingredients?query=` | Coincidencia por alias | Devuelve el ingrediente | `test_search_ingredients_matches_alias` |
| I-5 | `GET /ingredients?category=` | Filtro por categoría | Solo la categoría pedida | `test_search_ingredients_filters_by_category` |
| I-6 | `GET /ingredients/categories` | Conteo por categoría | `{categoria: count}` correcto | `test_ingredient_categories_returns_counts` |
| I-7 | `GET /ingredients/{id}` | Detalle por UUID | 200; `slug` | `test_get_ingredient_by_id` |
| I-8 | `GET /ingredients/{id}` | UUID inexistente | 404 | `test_get_unknown_ingredient_returns_404` |

---

## 8. Favoritos — `tests/test_favorites.py`

| ID | Endpoint | Caso | Resultado esperado | Test |
| -- | -------- | ---- | ------------------ | ---- |
| F-1 | `POST /favorites/{recipe_id}` | Agregar favorito | 201; `message=Added to favorites` | `test_add_favorite` |
| F-2 | `POST /favorites/{recipe_id}` | Duplicado | 400 | `test_add_favorite_is_idempotent_guard` |
| F-3 | `POST /favorites/{recipe_id}` | Receta inexistente | 404 | `test_add_favorite_unknown_recipe_returns_404` |
| F-4 | `GET /favorites` | Listar | 200; incluye `recipe_id` | `test_list_favorites_includes_recipe` |
| F-5 | `DELETE /favorites/{recipe_id}` | Quitar | 204; lista vacía | `test_remove_favorite` |
| F-6 | `DELETE /favorites/{recipe_id}` | No estaba | 404 | `test_remove_missing_favorite_returns_404` |
| F-7 | `GET /favorites/collections` | Colecciones | Incluye default (`null`) y la nombrada | `test_list_collections_includes_default` |
| F-8 | `GET /favorites` | Sin credenciales | 401 | `test_favorites_require_authentication` |

---

## 9. Calificaciones — `tests/test_ratings.py`

| ID | Endpoint | Caso | Resultado esperado | Test |
| -- | -------- | ---- | ------------------ | ---- |
| RT-1 | `POST /ratings/{recipe_id}?score=` | Calificar | 201; `message=Rating saved` | `test_rate_recipe` |
| RT-2 | `POST /ratings/{recipe_id}?score=` | Score fuera de 1–5 | 400 | `test_rate_recipe_rejects_out_of_range_score` |
| RT-3 | `POST /ratings/{recipe_id}?score=` | Receta inexistente | 404 | `test_rate_unknown_recipe_returns_404` |
| RT-4 | `POST /ratings/{recipe_id}?score=` | Sin credenciales | 401 | `test_rate_requires_authentication` |
| RT-5 | `POST /ratings/{recipe_id}?score=` | Actualiza agregados | `rating_count=1`, `avg_rating=4.0` | `test_rating_updates_recipe_aggregates` |
| RT-6 | `POST /ratings/{recipe_id}?score=` | Upsert por usuario | 1 sola fila; score actualizado | `test_rating_is_upserted_per_user` |
| RT-7 | `GET /ratings/{recipe_id}` | Listar | 200; score y `review_text` | `test_get_recipe_ratings` |

---

## 10. Visitas — `tests/test_visits.py`

| ID | Endpoint | Caso | Resultado esperado | Test |
| -- | -------- | ---- | ------------------ | ---- |
| V-1 | `POST /visits/{recipe_id}` | Registrar visita | 201; `visit_count` incrementa | `test_record_visit_increments_counter` |
| V-2 | `POST /visits/{recipe_id}` | Visita repetida (mismo día) | `visit_count` no se duplica (RB-04) | `test_repeated_visit_same_day_does_not_double_count` |
| V-3 | `POST /visits/{recipe_id}` | Receta inexistente | 404 | `test_record_visit_unknown_recipe_returns_404` |

---

## Trazabilidad con reglas de negocio

Referencia: `docs/requirements/business-rules.md`.

| Regla | Cubierta por | Estado |
| ----- | ------------ | ------ |
| RB-01 (categoría única) | R-8, R-11 | Cubierta |
| RB-02 (tags múltiples) | R-2, R-6 (tags en respuesta) | Parcial |
| RB-03 (búsqueda unificada) | R-4, R-5 | Parcial (texto/categoría; falta trigram) |
| RB-04 (visita única anti-F5) | V-2 | Cubierta |
| RB-05 (contador de guardados) | F-1, F-5 | Pendiente: `save_count` depende de triggers de DB no presentes en el esquema de test |
| RB-06 (calificación 1-5) | RT-1, RT-2, RT-5, RT-6 | Cubierta |
| RB-07 (autocompletado de tags) | T-3, T-4 | Cubierta |
| RB-08 (imagen nullable) | — | No aplica (MVP) |
| RB-09 (recetas públicas por defecto) | R-2, R-3 | Cubierta |
| RB-10 (soft delete) | R-16 | Cubierta |
| RB-11 (ingredientes JSONB) | I-7, I-8, R-8 | Parcial |
| RB-12 (dificultad tres niveles) | — | Pendiente |
| RB-13 (tiempos enteros) | — | Pendiente |
| RB-14 (porciones positivas) | — | Pendiente |
| RB-15 (slug único) | R-8, R-9, R-14 | Cubierta con desambiguación numérica (ver nota) |
| RB-16 (búsqueda por ingrediente parcial) | — | Pendiente |
| RB-AUTH-05 (JWT + rotación) | A-5, A-12, A-13, A-16 | Cubierta (HS256; ver nota) |
| RB-AUTH-06 (verificación de email) | A-1, A-8 | Cubierta |
| RB-AUTH-07 (recuperación de contraseña) | A-17 | Parcial (stub) |
| RB-ING-03 (autocompletado de ingredientes) | I-3, I-4 | Cubierta |

### Notas de discrepancia con la especificación

- **RB-15** especifica `slugify(title) + "-" + nanoid(4)`; la implementación
  actual desambigua con un sufijo numérico (`pizza-de-mozzarella` →
  `pizza-de-mozzarella-2`), tal como se definió como requisito de producto. La
  spec debería actualizarse para reflejar esta decisión.
- **RB-AUTH-05** especifica JWT RS256; la implementación y los tests usan
  HS256 con secreto simétrico. `podman-compose.yml` fue corregido porque forzaba
  RS256 con un secreto que no es una clave RSA (rompía la firma de tokens).
- **RB-05** asume triggers de base de datos para `save_count`; el esquema creado
  por los modelos no define esos triggers, por lo que el contador no se
  actualiza en los tests.
