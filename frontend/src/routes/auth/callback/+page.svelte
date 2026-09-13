<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { auth } from '$lib/stores/auth';

	let error = '';

	onMount(async () => {
		const token = $page.url.searchParams.get('access_token');
		if (!token) {
			error = 'No se recibió el token de autenticación.';
			return;
		}
		localStorage.setItem('access_token', token);
		await auth.init();
		if ($auth.isAuthenticated) {
			await goto('/');
		} else {
			error = 'No se pudo iniciar sesión con el proveedor.';
		}
	});
</script>

<svelte:head><title>Ingresando… — Recetario IA</title></svelte:head>

<div class="flex min-h-[60vh] items-center justify-center px-4 py-10">
	<div class="w-full max-w-md rounded-lg border border-border p-6 text-center">
		{#if error}
			<p class="mb-4 text-destructive" role="alert">{error}</p>
			<a href="/login" class="btn btn-outline">Volver al login</a>
		{:else}
			<p class="text-muted-foreground" role="status">Ingresando…</p>
		{/if}
	</div>
</div>
