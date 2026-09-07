<script lang="ts">
	import { enhance } from '$app/forms';
	import { auth } from '$lib/stores/auth';
	import { Button } from '$components/ui/Button.svelte';
	import { Loader2, AlertCircle } from 'lucide-svelte';

	let email = '';
	let password = '';
	let error = '';
	let loading = false;

	async function handleSubmit(event: Event & { currentTarget: HTMLFormElement }) {
		event.preventDefault();
		error = '';
		loading = true;

		try {
			await auth.login(email, password);
			// Navigation handled by auth store
		} catch (err: any) {
			error = err.message || 'Error al iniciar sesión';
		} finally {
			loading = false;
		}
	}
</script>

<div class="min-h-screen flex items-center justify-center bg-background px-4">
	<div class="w-full max-w-md">
		<div class="text-center mb-8">
			<h1 class="text-3xl font-playfair font-medium text-foreground mb-2">
				Panel de Administración
			</h1>
			<p class="text-muted-foreground">Inicia sesión para continuar</p>
		</div>

		<div class="card p-6 space-y-4">
			<form on:submit|preventDefault={handleSubmit} class="space-y-4">
				{#if error}
					<div class="flex items-center gap-2 p-3 bg-destructive/10 border border-destructive/20 text-destructive rounded-lg text-sm" role="alert">
						<AlertCircle class="w-5 h-5 shrink-0" />
						<p>{error}</p>
					</div>
				{/if}

				<div>
					<label for="email" class="label">Email</label>
					<input
						type="email"
						id="email"
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
						type="password"
						id="password"
						bind:value={password}
						class="input-base"
						placeholder="••••••••"
						required
						disabled={loading}
					/>
				</div>

				<Button type="submit" class="w-full" loading={loading}>
					{#if loading}
						<svg class="mr-2 h-4 w-4 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
							<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
							<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
						</svg>
						Accediendo...
					{:else}
						Iniciar sesión
					{/if}
				</Button>
			</form>
		</div>

		<p class="text-center text-sm text-muted-foreground mt-6">
			Recetario IA Admin v0.1.0
		</p>
	</div>
</div>