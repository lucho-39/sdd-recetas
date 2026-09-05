# Visión del Proyecto: Recetario IA

## Problema que resuelve

Los cocineros caseros y entusiastas de la cocina necesitan una forma organizada de:
- Encontrar recetas confiables sin perderse en blogs con mucha publicidad
- Guardar y organizar sus recetas favoritas en un solo lugar
- Descubrir nuevas recetas basadas en ingredientes que tienen a mano
- Confiar en las calificaciones de una comunidad real, no en reviews compradas
- Tener una experiencia limpia, sin distracciones, enfocada en cocinar

## Usuarios objetivo

| Usuario principal | Descripción |
|-------------------|-------------|
| **Cocinero casero cotidiano** | Cocina 3-7 veces por semana, busca recetas probadas, quiere guardar favoritas y acceder rápido desde el móvil en la cocina |
| **Entusiasta que experimenta** | Busca inspiración, quiere generar variaciones, califica y comenta recetas, busca por ingrediente |
| **Principiante que aprende** | Necesita instrucciones claras, pasos detallados, tiempos realistas, y filtros por dificultad |

## Objetivos del sistema

1. **Búsqueda y descubrimiento unificada**: Encontrar recetas combinando filtros de categoría (lista cerrada), etiquetas/tags (abiertas con autocompletado), nombre de receta e ingredientes — todo en una sola búsqueda
2. **Colección personal**: Guardar favoritas, crear colecciones/temas (ej: "Cenas rápidas", "Postres navideños"); contador de guardados por receta
3. **Generación asistida**: Crear recetas nuevas a partir de ingredientes disponibles o preferencias dietéticas
4. **Confianza social**: Calificaciones 1-5 estrellas + reseña textual, fotos de usuarios reales, verificación de "hecho y probado"
5. **Experiencia en cocina**: Modo "cocinando" — pantalla siempre encendida, pasos grandes, navegación por voz/gestos
6. **Offline-first**: Ver recetas guardadas sin conexión
7. **Métricas de popularidad**: Contador de visitas únicas por receta (usuario anónimo o logueado, no incrementa en F5/refresh) y contador de veces guardada

## Alcance inicial (MVP)

| Incluido | Fuera de alcance (v1) |
|----------|----------------------|
| Registro/login (email + OAuth Google/GitHub) | Suscripciones pagas / premium |
| CRUD de recetas (crear, leer, actualizar, borrar propias) | Marketplace de recetas / monetización |
| **Categorías cerradas** (postre, entrada, snack, plato principal, acompañamiento, bebida, desayuno, otro) | Seguimiento nutricional avanzado / macros |
| **Etiquetas/tags abiertas** con autocompletado (sin TACC, keto, vegano, vegetariano, bajo-carb, alto-proteina, etc.) | Planificación de menús semanales / lista de compras automática |
| **Búsqueda unificada**: categoría + tags + nombre + ingredientes | Compartir social / feed de actividad |
| Favoritos y colecciones personales (+ contador de guardados) | Modo colaborativo / recetas multi-autor |
| Calificación 1-5 estrellas + reseña textual | App nativa iOS/Android (solo PWA responsive) |
| Generación de recetas por IA (ingredientes → receta) | Importar de URLs externas (schema.org/Recipe) |
| Modo "cocinando" (pantalla siempre activa, pasos grandes) | |
| PWA instalable, offline para recetas guardadas | |
| **Imagen representativa única por receta** (campo nullable en MVP) | |
| **Contador de visitas únicas** (anónimos + logueados, anti-F5 via cookie 24h) | |
| **Contador de guardados** (incrementa al guardar, decrementa al quitar) | |

## Métricas de éxito (MVP)

- **Activación**: % usuarios que guardan ≥1 favorita en su primera semana > 40%
- **Retención**: % usuarios activos a 30 días > 25%
- **Calidad**: % recetas con ≥3 calificaciones y promedio ≥4.0 > 60%
- **Generación**: % usuarios que usan "generar receta" al menos 1 vez/mes > 30%

## Principios de diseño

1. **Contenido ante todo** — la receta es la protagonista; UI invisible
2. **Velocidad percibida** — skeleton loaders, imágenes progresivas, cache agresivo
3. **Accesibilidad real** — contraste, tamaños de toque, lectores de pantalla, modo alto contraste
4. **Privacidad por defecto** — datos del usuario no se venden; analytics anonimas y opt-in
5. **Extensible** — arquitectura modular para añadir features sin reescribir