<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';

	let status: 'loading' | 'ok' | 'error' = 'loading';
	let message = 'Verificando tu email…';

	onMount(async () => {
		const token = $page.url.searchParams.get('token');
		if (!token) {
			status = 'error';
			message = 'Falta el token de verificación.';
			return;
		}
		try {
			const res = await fetch('/api/v1/auth/verify-email', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ token })
			});
			if (res.ok) {
				status = 'ok';
				message = 'Tu email fue verificado. Ya podés iniciar sesión.';
			} else {
				const body = await res.json().catch(() => ({}));
				status = 'error';
				message = body.detail ?? 'No se pudo verificar el email.';
			}
		} catch {
			status = 'error';
			message = 'No se pudo verificar el email.';
		}
	});
</script>

<svelte:head><title>Verificar email — Recetario IA</title></svelte:head>

<div class="container flex min-h-[60vh] items-center justify-center py-10">
	<div class="w-full max-w-md rounded-lg border border-border p-6 text-center">
		<h1 class="mb-3 font-playfair text-2xl font-medium text-foreground">Verificación de email</h1>

		{#if status === 'loading'}
			<p class="text-muted-foreground">{message}</p>
		{:else if status === 'ok'}
			<p class="mb-5 text-foreground" role="status">{message}</p>
			<a href="/login" class="btn btn-primary">Iniciar sesión</a>
		{:else}
			<p class="mb-5 text-destructive" role="alert">{message}</p>
			<a href="/" class="btn btn-outline">Volver al inicio</a>
		{/if}
	</div>
</div>
