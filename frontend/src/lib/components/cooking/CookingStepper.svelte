<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { browser } from '$app/environment';
	import {
		IconX as X,
		IconPlayerPlayFilled as Play,
		IconPlayerPauseFilled as Pause,
		IconRefresh as Reset,
		IconChevronLeft as ChevronLeft,
		IconChevronRight as ChevronRight,
		IconVolume as Volume,
		IconVolumeOff as Mute,
		IconSettingsFilled as Settings,
		IconClockFilled as Clock,
		IconMaximize as Maximize,
		IconMinimize as Minimize
	} from '@tabler/icons-svelte';
	import type { Recipe } from '$lib/types';

	export let recipe: Recipe;
	export let steps: string[] = [];
	export let onExit: () => void = () => {};

	const STORAGE_KEY = `cooking:${recipe.slug}`;
	const FONT_KEY = 'cooking:font';

	const QUICK_MINUTES = [1, 5, 10];

	let index = 0;
	let voiceOn = false;
	let settingsOpen = false;
	let fontScale: 'base' | 'lg' | 'xl' = 'base';
	let wakeLock: any = null;
	let recognition: any = null;
	let voiceSupported = false;
	let fullscreen = false;
	let announced = '';
	let installPrompt: any = null;
	let canInstall = false;

	// Remaining seconds per step (persisted)
	let timers: Record<number, number> = {};
	let running = false;
	let tick: ReturnType<typeof setInterval> | null = null;

	$: safeSteps = steps.length > 0 ? steps : ['Esta receta no tiene pasos cargados.'];
	$: currentStep = safeSteps[index] ?? '';
	$: remaining = timers[index] ?? 0;
	$: display = `${String(Math.floor(remaining / 60)).padStart(2, '0')}:${String(remaining % 60).padStart(2, '0')}`;
	$: fontClass =
		fontScale === 'xl'
			? 'text-4xl md:text-5xl'
			: fontScale === 'lg'
				? 'text-3xl md:text-4xl'
				: 'text-2xl md:text-3xl';
	$: if (browser && safeSteps && (index >= safeSteps.length)) index = safeSteps.length - 1;

	function announce(message: string) {
		announced = message;
	}

	function persist() {
		if (!browser) return;
		localStorage.setItem(STORAGE_KEY, JSON.stringify({ index, timers }));
	}

	function go(target: number) {
		pauseTimer();
		index = Math.max(0, Math.min(safeSteps.length - 1, target));
		persist();
		announce(`Paso ${index + 1} de ${safeSteps.length}`);
	}

	function next() {
		if (index < safeSteps.length - 1) go(index + 1);
	}

	function prev() {
		if (index > 0) go(index - 1);
	}

	// --- Timer ---
	function setTimer(seconds: number) {
		timers = { ...timers, [index]: seconds };
		running = false;
		stopTick();
		persist();
		announce(`Timer de ${Math.round(seconds / 60)} minutos`);
	}

	function startTimer() {
		if (remaining <= 0) return;
		running = true;
		if ('Notification' in window && Notification.permission === 'default') {
			Notification.requestPermission().catch(() => {});
		}
		stopTick();
		tick = setInterval(() => {
			const value = (timers[index] ?? 0) - 1;
			if (value <= 0) {
				timers = { ...timers, [index]: 0 };
				pauseTimer();
				onTimerEnd();
			} else {
				timers = { ...timers, [index]: value };
			}
			persist();
		}, 1000);
	}

	function pauseTimer() {
		running = false;
		stopTick();
		persist();
	}

	function resetTimer() {
		pauseTimer();
		timers = { ...timers, [index]: 0 };
		persist();
	}

	function stopTick() {
		if (tick) {
			clearInterval(tick);
			tick = null;
		}
	}

	function beep() {
		try {
			const Ctx = window.AudioContext || (window as any).webkitAudioContext;
			const ctx = new Ctx();
			const oscillator = ctx.createOscillator();
			const gain = ctx.createGain();
			oscillator.connect(gain);
			gain.connect(ctx.destination);
			oscillator.type = 'sine';
			oscillator.frequency.value = 880;
			gain.gain.setValueAtTime(0.25, ctx.currentTime);
			oscillator.start();
			oscillator.stop(ctx.currentTime + 0.5);
		} catch {
			/* audio no disponible */
		}
	}

	function onTimerEnd() {
		beep();
		announce('¡Tiempo cumplido!');
		try {
			if ('Notification' in window && Notification.permission === 'granted') {
				new Notification('¡Timer listo!', { body: `Paso ${index + 1}: ${recipe.title}` });
			}
		} catch {
			/* notificaciones no disponibles */
		}
	}

	// --- Voice ---
	function speak(text: string) {
		try {
			if ('speechSynthesis' in window) {
				speechSynthesis.cancel();
				speechSynthesis.speak(new SpeechSynthesisUtterance(text));
			}
		} catch {
			/* tts no disponible */
		}
	}

	function handleVoice(transcript: string) {
		const t = transcript.toLowerCase();
		if (t.includes('siguiente')) next();
		else if (t.includes('anterior') || t.includes('atrás') || t.includes('atras')) prev();
		else if (t.includes('repite') || t.includes('repetir')) speak(currentStep);
		else if (t.includes('pausa')) pauseTimer();
		else if (t.includes('contin') || t.includes('empez')) startTimer();
		else if (t.includes('salir')) handleExit();
		else {
			const match = t.match(/(\d+)\s*min/);
			if (match) setTimer(Number(match[1]) * 60);
		}
	}

	function startVoice() {
		if (!voiceSupported || !recognition) {
			announce('El reconocimiento de voz no está disponible en este navegador.');
			return;
		}
		try {
			recognition.start();
			voiceOn = true;
		} catch {
			/* ya iniciado */
		}
	}

	function stopVoice() {
		voiceOn = false;
		try {
			recognition?.stop();
		} catch {
			/* no iniciado */
		}
	}

	function toggleVoice() {
		if (voiceOn) stopVoice();
		else startVoice();
	}

	// --- Wake lock / fullscreen ---
	async function requestWakeLock() {
		try {
			if (browser && 'wakeLock' in navigator) {
				wakeLock = await (navigator as any).wakeLock.request('screen');
			}
		} catch {
			/* no disponible */
		}
	}

	function releaseWakeLock() {
		try {
			wakeLock?.release?.();
		} catch {
			/* ignore */
		}
		wakeLock = null;
	}

	async function toggleFullscreen() {
		try {
			if (!document.fullscreenElement) {
				await document.documentElement.requestFullscreen?.();
				fullscreen = true;
				try {
					await (screen as any).orientation?.lock?.('landscape');
				} catch {
					/* orientation lock not supported */
				}
			} else {
				await document.exitFullscreen?.();
				fullscreen = false;
				try {
					(screen as any).orientation?.unlock?.();
				} catch {
					/* ignore */
				}
			}
		} catch {
			/* bloqueado sin gesto */
		}
	}

	function handleBeforeInstall(event: Event) {
		event.preventDefault();
		installPrompt = event;
		canInstall = true;
	}

	async function installApp() {
		if (!installPrompt) return;
		installPrompt.prompt();
		try {
			await installPrompt.userChoice;
		} catch {
			/* ignore */
		}
		installPrompt = null;
		canInstall = false;
	}

	function handleVisibility() {
		if (document.visibilityState === 'visible') requestWakeLock();
	}

	function handleFullscreenChange() {
		fullscreen = !!document.fullscreenElement;
	}

	// --- Swipe ---
	let touchX = 0;
	let touchY = 0;
	function onTouchStart(e: TouchEvent) {
		touchX = e.changedTouches[0].clientX;
		touchY = e.changedTouches[0].clientY;
	}
	function onTouchEnd(e: TouchEvent) {
		const dx = e.changedTouches[0].clientX - touchX;
		const dy = e.changedTouches[0].clientY - touchY;
		if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy)) {
			if (dx < 0) next();
			else prev();
		}
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'ArrowRight') next();
		else if (e.key === 'ArrowLeft') prev();
		else if (e.key === 'Escape') handleExit();
	}

	function handleExit() {
		stopVoice();
		pauseTimer();
		releaseWakeLock();
		try {
			if (document.fullscreenElement) document.exitFullscreen?.();
		} catch {
			/* ignore */
		}
		onExit();
	}

	onMount(() => {
		if (browser) {
			const stored = localStorage.getItem(STORAGE_KEY);
			if (stored) {
				try {
					const parsed = JSON.parse(stored);
					if (typeof parsed.index === 'number') index = parsed.index;
					if (parsed.timers) timers = parsed.timers;
				} catch {
					/* ignore corrupt state */
				}
			}
			const savedFont = localStorage.getItem(FONT_KEY) as typeof fontScale | null;
			if (savedFont) fontScale = savedFont;

			const SR = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
			if (SR) {
				voiceSupported = true;
				recognition = new SR();
				recognition.lang = 'es-AR';
				recognition.continuous = true;
				recognition.interimResults = false;
				recognition.onresult = (event: any) => {
					const result = event.results[event.results.length - 1];
					if (result.isFinal) {
						const transcript = result[0].transcript.trim();
						announce(`Escuchado: ${transcript}`);
						handleVoice(transcript);
					}
				};
				recognition.onend = () => {
					if (voiceOn) {
						try {
							recognition.start();
						} catch {
							/* ignore */
						}
					}
				};
			}

			document.body.style.overflow = 'hidden';
			requestWakeLock();
			document.addEventListener('visibilitychange', handleVisibility);
			document.addEventListener('fullscreenchange', handleFullscreenChange);
			window.addEventListener('beforeinstallprompt', handleBeforeInstall);
		}

		return () => {
			stopTick();
			stopVoice();
			releaseWakeLock();
			if (browser) {
				document.body.style.overflow = '';
				document.removeEventListener('visibilitychange', handleVisibility);
				document.removeEventListener('fullscreenchange', handleFullscreenChange);
				window.removeEventListener('beforeinstallprompt', handleBeforeInstall);
			}
		};
	});

	function saveFont(value: typeof fontScale) {
		fontScale = value;
		if (browser) localStorage.setItem(FONT_KEY, value);
	}

	onDestroy(() => {
		stopTick();
		releaseWakeLock();
	});
</script>

<svelte:window on:keydown={handleKeydown} />

<div
	class="fixed inset-0 z-[100] flex flex-col bg-background text-foreground"
	role="region"
	aria-label="Modo cocinando"
	on:touchstart={onTouchStart}
	on:touchend={onTouchEnd}
>
	<!-- Header -->
	<header class="flex items-center justify-between gap-2 border-b border-border px-3 py-3 md:px-6">
		<button type="button" class="btn btn-ghost btn-sm" on:click={handleExit} aria-label="Salir del modo cocinando">
			<X class="h-5 w-5" aria-hidden="true" /> Salir
		</button>
		<div class="flex items-center gap-1">
			{#if canInstall}
				<button type="button" class="btn btn-ghost btn-sm" on:click={installApp} aria-label="Instalar aplicación">
					Instalar
				</button>
			{/if}
			<button
				type="button"
				class="btn btn-ghost btn-sm"
				on:click={toggleFullscreen}
				aria-label={fullscreen ? 'Salir de pantalla completa' : 'Pantalla completa'}
			>
				{#if fullscreen}<Minimize class="h-5 w-5" aria-hidden="true" />{:else}<Maximize class="h-5 w-5" aria-hidden="true" />{/if}
			</button>
			<button
				type="button"
				class="btn btn-ghost btn-sm"
				on:click={() => (settingsOpen = !settingsOpen)}
				aria-expanded={settingsOpen}
				aria-label="Ajustes"
			>
				<Settings class="h-5 w-5" aria-hidden="true" />
			</button>
			<button
				type="button"
				class="btn btn-sm {voiceOn ? 'btn-primary' : 'btn-ghost'}"
				on:click={toggleVoice}
				aria-pressed={voiceOn}
				aria-label={voiceOn ? 'Desactivar voz' : 'Activar voz'}
			>
				{#if voiceOn}<Volume class="h-5 w-5" aria-hidden="true" />{:else}<Mute class="h-5 w-5" aria-hidden="true" />{/if}
				Voz
			</button>
		</div>
	</header>

	<!-- Settings panel -->
	{#if settingsOpen}
		<div class="border-b border-border bg-muted/40 px-3 py-3 md:px-6" aria-label="Ajustes del modo cocinando">
			<div class="flex flex-wrap items-center gap-4 text-sm">
				<span class="font-medium">Tamaño de texto:</span>
				{#each [{ v: 'base', l: 'Normal' }, { v: 'lg', l: 'Grande' }, { v: 'xl', l: 'Muy grande' }] as opt}
					<button
						type="button"
						class="badge {fontScale === opt.v ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'}"
						on:click={() => saveFont(opt.v as typeof fontScale)}
					>
						{opt.l}
					</button>
				{/each}
				{#if !voiceSupported}<span class="text-muted-foreground">Reconocimiento de voz no disponible en este navegador.</span>{/if}
			</div>
		</div>
	{/if}

	<!-- Step -->
	<main class="flex flex-1 flex-col items-center justify-center overflow-y-auto px-4 py-8 text-center">
		<p class="mb-4 text-sm font-medium uppercase tracking-wide text-muted-foreground">
			Paso {index + 1} de {safeSteps.length}
		</p>
		<p class="{fontClass} mx-auto max-w-3xl font-medium leading-relaxed text-foreground">
			{currentStep}
		</p>

		<!-- Progress dots -->
		{#if safeSteps.length > 1}
			<div class="mt-8 flex flex-wrap items-center justify-center gap-2">
				{#each safeSteps as _s, i}
					<button
						type="button"
						class="h-2.5 w-2.5 rounded-full {i === index ? 'bg-primary' : 'bg-muted-foreground/30'}"
						on:click={() => go(i)}
						aria-label={`Ir al paso ${i + 1}`}
						aria-current={i === index ? 'step' : 'false'}
					></button>
				{/each}
			</div>
		{/if}
	</main>

	<!-- Navigation + timer -->
	<footer class="border-t border-border px-3 py-4 md:px-6">
		<div class="mx-auto flex max-w-3xl items-center justify-between gap-4">
			<button
				type="button"
				class="btn btn-outline min-h-14 min-w-14 flex-1"
				on:click={prev}
				disabled={index === 0}
			>
				<ChevronLeft class="h-6 w-6" aria-hidden="true" /> Anterior
			</button>
			<button type="button" class="btn btn-ghost btn-sm whitespace-nowrap" on:click={() => speak(currentStep)}>
				Repetir
			</button>
			<button
				type="button"
				class="btn btn-primary min-h-14 min-w-14 flex-1"
				on:click={next}
				disabled={index === safeSteps.length - 1}
			>
				Siguiente <ChevronRight class="h-6 w-6" aria-hidden="true" />
			</button>
		</div>

		<div class="mx-auto mt-4 flex max-w-3xl flex-wrap items-center justify-center gap-2">
			<span class="inline-flex items-center gap-2 rounded-lg bg-muted px-4 py-2 font-mono text-2xl tabular-nums">
				<Clock class="h-5 w-5 text-muted-foreground" aria-hidden="true" />
				{display}
			</span>
			{#each QUICK_MINUTES as m}
				<button type="button" class="badge bg-muted text-muted-foreground hover:bg-accent" on:click={() => setTimer(m * 60)}>
					{m} min
				</button>
			{/each}
			{#if running}
				<button type="button" class="btn btn-outline btn-sm" on:click={pauseTimer}>
					<Pause class="h-4 w-4" aria-hidden="true" /> Pausar
				</button>
			{:else}
				<button type="button" class="btn btn-outline btn-sm" on:click={startTimer} disabled={remaining <= 0}>
					<Play class="h-4 w-4" aria-hidden="true" /> Iniciar
				</button>
			{/if}
			<button type="button" class="btn btn-ghost btn-sm" on:click={resetTimer}>
				<Reset class="h-4 w-4" aria-hidden="true" /> Reset
			</button>
		</div>
	</footer>

	<p class="sr-only" aria-live="polite">{announced}</p>
</div>
