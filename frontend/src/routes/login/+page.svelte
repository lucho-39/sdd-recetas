<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { IconChefHatFilled as ChefHat, IconAlertCircleFilled as AlertCircle, IconLoader2 as Loader } from '@tabler/icons-svelte';
	import { auth } from '$lib/stores/auth';

	let email = '';
	let password = '';
	let error = '';
	let loading = false;
	let needsVerification = false;
	let verifyMessage = '';
	let verifyUrl = '';

	let returnTo = '/';
	$: returnTo = $page.url.searchParams.get('returnTo') ?? '/';

	async function handleSubmit() {
		error = '';
		loading = true;
		try {
			await auth.login(email, password);
			await goto(returnTo);
		} catch (err) {
			const message = err instanceof Error ? err.message : 'No se pudo iniciar sesión';
			error = message;
			needsVerification = /not verified/i.test(message);
		} finally {
			loading = false;
		}
	}

	async function resendVerification() {
		verifyMessage = '';
		verifyUrl = '';
		const res = await fetch('/api/v1/auth/request-verification', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ email })
		});
		if (res.ok) {
			const body = await res.json();
			if (body.verification_url) {
				verifyUrl = body.verification_url;
				verifyMessage = 'Enlace generado (entorno de desarrollo):';
			} else {
				verifyMessage = body.message ?? 'Revisá tu correo.';
			}
		} else {
			verifyMessage = 'No se pudo generar el enlace.';
		}
	}
</script>

<svelte:head><title>Iniciar sesión — Recetario IA</title></svelte:head>

<div class="flex min-h-[70vh] items-center justify-center px-4 py-10">
	<div class="w-full max-w-md">
		<div class="mb-8 text-center">
			<ChefHat class="mx-auto h-10 w-10 text-primary" aria-hidden="true" />
			<h1 class="mt-3 font-playfair text-3xl font-medium text-foreground">Iniciar sesión</h1>
			<p class="mt-2 text-muted-foreground">Entrá para guardar y crear tus recetas</p>
		</div>

		<div class="card p-6">
			<form class="space-y-4" on:submit|preventDefault={handleSubmit}>
				{#if error}
					<div class="flex items-center gap-2 rounded-md border border-destructive/20 bg-destructive/10 p-3 text-sm text-destructive" role="alert">
						<AlertCircle class="h-5 w-5 shrink-0" aria-hidden="true" />
						<p>{error}</p>
					</div>
				{/if}

				{#if needsVerification}
					<div class="rounded-md border border-border bg-muted/40 p-3 text-sm">
						<p class="mb-2 text-muted-foreground">Tu email todavía no está verificado.</p>
						<div class="flex flex-wrap items-center gap-3">
							<button type="button" class="btn btn-outline btn-sm" on:click={resendVerification}>
								Reenviar verificación
							</button>
							{#if verifyMessage}<span class="text-muted-foreground">{verifyMessage}</span>{/if}
							{#if verifyUrl}<a class="text-primary underline" href={verifyUrl}>Verificar ahora</a>{/if}
						</div>
					</div>
				{/if}

				<div>
					<label for="email" class="label">Email</label>
					<input id="email" type="email" bind:value={email} class="input-base" autocomplete="email" required disabled={loading} />
				</div>
				<div>
					<label for="password" class="label">Contraseña</label>
					<input id="password" type="password" bind:value={password} class="input-base" autocomplete="current-password" required disabled={loading} />
				</div>

				<button type="submit" class="btn btn-primary w-full" disabled={loading}>
					{#if loading}<Loader class="h-4 w-4 animate-spin" aria-hidden="true" />{/if}
					Entrar
				</button>
			</form>

			<div class="mt-4 flex flex-col gap-2 text-center text-sm">
				<a href="/forgot-password" class="link">¿Olvidaste tu contraseña?</a>
				<p class="text-muted-foreground">
					¿No tenés cuenta? <a href="/register" class="link">Crear cuenta</a>
				</p>
			</div>
		</div>
	</div>
</div>
