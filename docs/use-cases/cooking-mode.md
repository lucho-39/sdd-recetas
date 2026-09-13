# Caso de Uso: Modo Cocinando

**ID**: UC-COOKING-001
**Actor principal**: Usuario (autenticado o anónimo) cocinando
**Precondición**: La receta existe y tiene pasos (instrucciones)
**Objetivo**: Seguir los pasos manos libres, con pantalla siempre activa y sin
tocar el dispositivo

---

## Flujo Principal

1. En el detalle (`/receta/:slug`) el usuario pulsa **Cocinar** → `/cooking/:slug`.
2. El servidor carga la receta y divide `instructions` por línea en **pasos**.
3. Se muestra el overlay fullscreen con "Paso N de M" y el texto en grande.
4. El usuario navega con:
   - botones **Anterior / Siguiente**,
   - teclado **← / →**,
   - **swipe** táctil izq/der,
   - **voz** (si el navegador soporta `SpeechRecognition`).
5. El usuario puede iniciar un **timer por paso** (1/5/10 min) con beep y
   notificación al terminar.
6. Al salir (botón **Salir**, `Esc`, o voz "salir") vuelve al detalle y se
   liberan wake lock / fullscreen / reconocimiento de voz.

## Comandos de voz

| Comando | Acción |
|---------|--------|
| "siguiente" | Avanzar paso |
| "anterior" / "atrás" | Retroceder paso |
| "repite" / "repetir" | Leer el paso actual (TTS) |
| "pausa" | Pausar el timer |
| "continúa" / "empezá" | Iniciar el timer |
| "N minutos" | Programar el timer (ej: "5 minutos") |
| "salir" | Salir del modo cocinando |

## Features

- **Wake Lock API** (`navigator.wakeLock.request('screen')`) con re-adquisición
  al volver a la pestaña; liberación al salir.
- **Fullscreen** (`requestFullscreen`) y, best-effort, bloqueo de orientación
  (`screen.orientation.lock('landscape')`).
- **Timer por paso** con beep (Web Audio) y notificación (`Notification`).
- **Persistencia** en `localStorage`: paso actual, timers y tamaño de fuente.
- **Ajustes**: tamaño de texto (normal/grande/muy grande) y voz on/off.

## Reglas de Negocio

| Regla | Aplicación |
|-------|------------|
| RB-15 | El modo consume la receta por slug |
| — | La voz es opcional y degrada con aviso si no hay soporte |
| — | El timer y el paso se recuperan si se recarga la página |

## Accesibilidad

- `role="region" aria-label="Modo cocinando"`.
- Cambios de estado (paso/comando) anunciados con `aria-live="polite"`.
- Botones grandes (touch-friendly) y navegación por teclado.

## Criterios de Aceptación

| ID | Criterio |
|----|----------|
| AC-01 | `/cooking/:slug` carga en fullscreen con el primer paso |
| AC-02 | Anterior/Siguiente, teclado, swipe y voz cambian de paso |
| AC-03 | El timer cuenta, hace beep y notifica al terminar |
| AC-04 | Al recargar, se recupera el paso y los timers |
| AC-05 | Salir libera wake lock, fullscreen y reconocimiento |
| AC-06 | Si no hay `SpeechRecognition`, se avisa y el resto funciona |

## Contrato técnico

- Ruta: `frontend/src/routes/cooking/[slug]/` (`+page.server.ts` arma los pasos,
  `+page.svelte` monta el componente).
- Componente: `frontend/src/lib/components/cooking/CookingStepper.svelte`
  (props: `recipe`, `steps`, `onExit`).
- El overlay es `fixed inset-0` (cubre el navbar sin alterar el layout).

## Estado de Implementación

- ✅ Fullscreen, wake lock, navegación (botones/teclado/swipe), voz, timer por
  paso, persistencia y ajustes de texto.
- ✅ `screen.orientation.lock('landscape')` best-effort y botón de instalación PWA.
- 🔲 Prompt de instalación PWA guiado y voz continua en segundo plano
  (dependen del navegador).
