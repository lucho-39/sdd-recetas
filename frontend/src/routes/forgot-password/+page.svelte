<script lang="ts">
	import { IconHelpCircleFilled as Help } from '@tabler/icons-svelte';

	let email = '';
	let sent = false;
	let loading = false;
	let resetUrl = '';

	async function handleSubmit() {
		loading = true;
		try {
			const response = await fetch('/api/v1/auth/forgot-password', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ email })
			});
			if (response.ok) {
				const body = await response.json();
				resetUrl = body.reset_url ?? '';
			}
		} finally {
			sent = true;
			loading = false;
		}
	}
</script>

<svelte:head><title>Recuperar contraseña — Recetario IA</title></svelte:head>

<div class="flex min-h-[70vh] items-center justify-center px-4 py-10">
	<div class="w-full max-w-md">
		<div class="mb-8 text-center">
			<Help class="mx-auto h-10 w-10 text-primary" aria-hidden="true" />
			<h1 class="mt-3 font-playfair text-3xl font-medium text-foreground">Recuperar contraseña</h1>
		</div>

		<div class="card p-6">
			{#if sent}
				<p class="text-sm text-muted-foreground">
					Si el email existe, te enviamos instrucciones para restablecer la contraseña.
				</p>
				{#if resetUrl}
					<p class="mt-3 text-sm">
						<span class="text-muted-foreground">Enlace generado (entorno de desarrollo):</span>
						<a class="link" href={resetUrl}>Restablecer contraseña</a>
					</p>
				{/if}
			{:else}
				<form class="space-y-4" on:submit|preventDefault={handleSubmit}>
					<div>
						<label for="email" class="label">Email</label>
						<input id="email" type="email" bind:value={email} class="input-base" autocomplete="email" required disabled={loading} />
					</div>
					<button type="submit" class="btn btn-primary w-full" disabled={loading}>Enviar</button>
				</form>
			{/if}

			<p class="mt-4 text-center text-sm text-muted-foreground">
				<a href="/login" class="link">Volver a iniciar sesión</a>
			</p>
		</div>
	</div>
</div>
