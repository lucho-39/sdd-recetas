<script lang="ts">
	import { goto } from '$app/navigation';
	import { IconChefHatFilled as ChefHat, IconAlertCircleFilled as AlertCircle, IconLoader2 as Loader } from '@tabler/icons-svelte';
	import { auth } from '$lib/stores/auth';

	let email = '';
	let displayName = '';
	let password = '';
	let confirm = '';
	let error = '';
	let loading = false;

	async function handleSubmit() {
		error = '';
		if (password.length < 8) {
			error = 'La contraseña debe tener al menos 8 caracteres';
			return;
		}
		if (password !== confirm) {
			error = 'Las contraseñas no coinciden';
			return;
		}

		loading = true;
		try {
			const res = await fetch('/api/v1/auth/register', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ email, display_name: displayName, password })
			});
			if (!res.ok) {
				const body = await res.json().catch(() => ({}));
				throw new Error(body.detail || 'No se pudo crear la cuenta');
			}
			// Email verification delivery is v2, so registrations are usable immediately.
			await auth.login(email, password);
			await goto('/');
		} catch (err) {
			error = err instanceof Error ? err.message : 'No se pudo crear la cuenta';
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head><title>Crear cuenta — Recetario IA</title></svelte:head>

<div class="flex min-h-[70vh] items-center justify-center px-4 py-10">
	<div class="w-full max-w-md">
		<div class="mb-8 text-center">
			<ChefHat class="mx-auto h-10 w-10 text-primary" aria-hidden="true" />
			<h1 class="mt-3 font-playfair text-3xl font-medium text-foreground">Crear cuenta</h1>
			<p class="mt-2 text-muted-foreground">Empezá a guardar y compartir tus recetas</p>
		</div>

		<div class="card p-6">
			<form class="space-y-4" on:submit|preventDefault={handleSubmit}>
				{#if error}
					<div class="flex items-center gap-2 rounded-md border border-destructive/20 bg-destructive/10 p-3 text-sm text-destructive" role="alert">
						<AlertCircle class="h-5 w-5 shrink-0" aria-hidden="true" />
						<p>{error}</p>
					</div>
				{/if}

				<div>
					<label for="display_name" class="label">Nombre</label>
					<input id="display_name" type="text" bind:value={displayName} class="input-base" maxlength="100" required disabled={loading} />
				</div>
				<div>
					<label for="email" class="label">Email</label>
					<input id="email" type="email" bind:value={email} class="input-base" autocomplete="email" required disabled={loading} />
				</div>
				<div>
					<label for="password" class="label">Contraseña</label>
					<input id="password" type="password" bind:value={password} class="input-base" autocomplete="new-password" required disabled={loading} />
				</div>
				<div>
					<label for="confirm" class="label">Repetir contraseña</label>
					<input id="confirm" type="password" bind:value={confirm} class="input-base" autocomplete="new-password" required disabled={loading} />
				</div>

				<button type="submit" class="btn btn-primary w-full" disabled={loading}>
					{#if loading}<Loader class="h-4 w-4 animate-spin" aria-hidden="true" />{/if}
					Crear cuenta
				</button>
			</form>

			<p class="mt-4 text-center text-sm text-muted-foreground">
				¿Ya tenés cuenta? <a href="/login" class="link">Iniciar sesión</a>
			</p>
		</div>
	</div>
</div>
