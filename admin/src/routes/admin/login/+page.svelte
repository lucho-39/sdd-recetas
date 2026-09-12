<script lang="ts">
	import { goto } from '$app/navigation';
	import { auth } from '$lib/stores/auth';
	import { Loader2, AlertCircle } from 'lucide-svelte';

	let email = '';
	let password = '';
	let error = '';
	let loading = false;

	async function handleSubmit() {
		error = '';
		loading = true;
		try {
			await auth.login(email, password);
			await goto('/');
		} catch (err) {
			error = err instanceof Error ? err.message : 'Error al iniciar sesión';
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>Ingresar — Recetario Admin</title>
</svelte:head>

<div class="flex min-h-screen items-center justify-center bg-background px-4">
	<div class="w-full max-w-md">
		<div class="mb-8 text-center">
			<h1 class="font-playfair text-3xl font-medium text-foreground">Panel de Administración</h1>
			<p class="mt-2 text-muted-foreground">Iniciá sesión para continuar</p>
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
					<label for="email" class="label">Email</label>
					<input
						id="email"
						type="email"
						bind:value={email}
						class="input-base"
						placeholder="admin@recetario.local"
						autocomplete="email"
						required
						disabled={loading}
					/>
				</div>

				<div>
					<label for="password" class="label">Contraseña</label>
					<input
						id="password"
						type="password"
						bind:value={password}
						class="input-base"
						placeholder="••••••••"
						autocomplete="current-password"
						required
						disabled={loading}
					/>
				</div>

				<button type="submit" class="btn btn-primary w-full" disabled={loading}>
					{#if loading}
						<Loader2 class="h-4 w-4 animate-spin" aria-hidden="true" />
						Accediendo…
					{:else}
						Iniciar sesión
					{/if}
				</button>
			</form>
		</div>

		<p class="mt-6 text-center text-sm text-muted-foreground">Recetario IA Admin v0.1.0</p>
	</div>
</div>
