# Glosario del Dominio: Recetario IA

> Términos específicos del proyecto (además del glosario SDD global en `docs/GLOSSARY.md`).

| Término | Definición |
|---------|------------|
| **Receta** | Entidad principal: conjunto de ingredientes, instrucciones, metadatos (categoría, tags, tiempos, dificultad) y autoría. |
| **Ingrediente** | Item individual dentro de una receta: nombre, cantidad, unidad, notas opcionales. Almacenado como JSONB. |
| **Categoría** | Clasificación cerrada y mutuamente excluyente de la receta (ej: Postre, Entrada, Plato principal). Administrable solo por admins. |
| **Tag / Etiqueta** | Clasificación abierta y multi-valor (ej: vegano, sin-TACC, keto). Creada por usuarios con autocompletado; normalizada a slug. |
| **Colección** | Agrupación personal de recetas guardadas por un usuario (ej: "Cenas rápidas", "Favoritos"). Una receta puede estar en múltiples colecciones. |
| **Favorito** | Caso especial de guardado: colección por defecto (collection_name = NULL). |
| **Visita única** | Evento de visualización de detalle de receta, contabilizado una vez por receta por visitante por día calendario. Visitante = user_id (logueado) o fingerprint/cookie (anónimo). |
| **Contador de visitas** | `receta.visit_count`: agregado denormalizado de visitas únicas. |
| **Contador de guardados** | `receta.save_count`: agregado denormalizado de veces que la receta está en cualquier colección de cualquier usuario. |
| **Calificación (Rating)** | Puntuación 1-5 estrellas + reseña textual opcional, por usuario logueado. Una por usuario por receta. |
| **Promedio de calificación** | `receta.avg_rating`: media aritmética de scores, 2 decimales. |
| **Conteo de calificaciones** | `receta.rating_count`: número de ratings recibidos. |
| **Modo cocinando** | Vista full-screen optimizada para uso en cocina: wake lock, pasos grandes, navegación swipe/voz, timers por paso. |
| **Generación IA** | Función que crea una receta completa a partir de ingredientes disponibles y preferencias dietéticas (tags). |
| **Búsqueda unificada** | Query que combina: categoría (single), tags (multi, AND), texto libre (título/descripción, OR), ingredientes (multi, OR) — todo AND entre dimensiones. |
| **Autocompletado de tags** | Sugerencia de tags existentes por prefijo en slug, ordenados por `usage_count` descendente. |
| **Slug de tag** | Versión normalizada del tag para URL/identificación: lowercase, sin acentos, espacios→guiones, solo alfanum+guion. Ej: "Sin TACC" → "sin-tacc". |
| **Soft delete** | Borrado lógico: `deleted_at` timestamp; la entidad persiste pero se excluye de consultas públicas. |
| **Fingerprint de visitante** | Hash SHA256(IP + User-Agent + salt_diario) o cookie UUID persistente para identificar visitantes anónimos en conteo de visitas. |
| **Salt diario** | Valor rotativo cada 24h (HMAC(secret, date)) para que fingerprint no sea linkable cross-day. |
| **PWA (Progressive Web App)** | Aplicación web instalable, con service worker para offline, manifest, icons. |
| **Offline-first** | Recetas guardadas (favoritos/colecciones) disponibles sin conexión vía cache de service worker. |
| **Wake Lock API** | API del navegador para mantener pantalla encendida durante modo cocinando. |
| **Schema.org/Recipe** | Formato estándar de datos estructurados para SEO de recetas (futuro: import/export). |

---

## Abreviaturas del proyecto

| Sigla | Significado |
|-------|-------------|
| **RB** | Business Rule (Regla de Negocio) — prefijo en `docs/requirements/business-rules.md` |
| **RF** | Functional Requirement (Requisito Funcional) — prefijo en `functional-requirements.md` |
| **RNF** | Non-Functional Requirement (Requisito No Funcional) — prefijo en `non-functional-requirements.md` |
| **US** | User Story — prefijo en `user-stories.md` |
| **AC** | Acceptance Criteria (Criterio de Aceptación) |
| **MVP** | Mínimo Producto Viable |
| **PWA** | Progressive Web App |
| **JSONB** | JSON Binario (PostgreSQL) — índice GIN, query eficiente |
| **FK** | Foreign Key |
| **PK** | Primary Key |
| **N:M** | Relación Muchos a Muchos |
| **1:N** | Relación Uno a Muchos |