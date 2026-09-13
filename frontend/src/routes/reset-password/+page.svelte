<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { IconLockFilled as Lock, IconAlertCircleFilled as Alert } from '@tabler/icons-svelte';

	let token = '';
	let password = '';
	let confirmPassword = '';
	let error = '';
	let message = '';
	let loading = false;

	onMount(() => {
		token = $page.url.searchParams.get('token') ?? '';
	});

	async function handleSubmit() {
		error = '';
		message = '';
		if (!token) {
			error = 'Falta el token de restablecimiento.';
			return;
		}
		if (password.length < 8) {
			error = 'La contraseña debe tener al menos 8 caracteres.';
			return;
		}
		if (password !== confirmPassword) {
			error = 'Las contraseñas no coinciden.';
			return;
		}
		loading = true;
		try {
			const response = await fetch('/api/v1/auth/reset-password', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ token, new_password: password })
			});
			if (!response.ok) {
				const body = await response.json().catch(() => ({}));
				throw new Error(body.detail || 'No se pudo restablecer la contraseña');
			}
			message = 'Contraseña restablecida. Redirigiendo al login…';
			setTimeout(() => goto('/login'), 1500);
		} catch (err) {
			error = err instanceof Error ? err.message : 'Error';
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head><title>Restablecer contraseña — Recetario IA</title></svelte:head>

<div class="flex min-h-[70vh] items-center justify-center px-4 py-10">
	<div class="w-full max-w-md">
		<div class="mb-8 text-center">
			<Lock class="mx-auto h-10 w-10 text-primary" aria-hidden="true" />
			<h1 class="mt-3 font-playfair text-3xl font-medium text-foreground">Restablecer contraseña</h1>
		</div>

		<div class="card p-6">
			{#if message}
				<p class="text-sm text-success" role="status">{message}</p>
			{:else}
				<form class="space-y-4" on:submit|preventDefault={handleSubmit}>
					{#if error}
						<div class="flex items-center gap-2 rounded-md border border-destructive/20 bg-destructive/10 p-3 text-sm text-destructive" role="alert">
							<Alert class="h-5 w-5 shrink-0" aria-hidden="true" />
							<p>{error}</p>
						</div>
					{/if}
					<div>
						<label for="password" class="label">Nueva contraseña</label>
						<input id="password" type="password" bind:value={password} class="input-base" autocomplete="new-password" required disabled={loading} />
					</div>
					<div>
						<label for="confirm" class="label">Repetir contraseña</label>
						<input id="confirm" type="password" bind:value={confirmPassword} class="input-base" autocomplete="new-password" required disabled={loading} />
					</div>
					<button type="submit" class="btn btn-primary w-full" disabled={loading}>
						{loading ? 'Guardando…' : 'Restablecer'}
					</button>
				</form>
			{/if}

			<p class="mt-4 text-center text-sm text-muted-foreground">
				<a href="/login" class="link">Volver a iniciar sesión</a>
			</p>
		</div>
	</div>
</div>
