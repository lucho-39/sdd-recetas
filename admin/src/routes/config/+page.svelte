<script lang="ts">
	import { onMount } from 'svelte';
	import { get } from 'svelte/store';
	import { adminFetch } from '$lib/api';
	import { auth } from '$lib/stores/auth';

	let settings: Record<string, unknown> = {};
	let loading = true;
	let saving = false;
	let error = '';
	let success = '';

	async function load() {
		loading = true;
		error = '';
		try {
			settings = (await adminFetch<{ settings: Record<string, unknown> }>('/config')).settings;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Error al cargar la configuración';
		} finally {
			loading = false;
		}
	}

	async function save() {
		saving = true;
		error = '';
		success = '';
		try {
			const { accessToken } = get(auth);
			const res = await fetch('/api/admin/config', {
				method: 'PUT',
				headers: {
					'Content-Type': 'application/json',
					Authorization: `Bearer ${accessToken}`
				},
				body: JSON.stringify({ settings })
			});
			if (!res.ok) {
				const body = await res.json().catch(() => ({}));
				throw new Error(body.detail ?? `API ${res.status}`);
			}
			settings = (await res.json()).settings;
			success = 'Configuración guardada.';
		} catch (err) {
			error = err instanceof Error ? err.message : 'No se pudo guardar';
		} finally {
			saving = false;
		}
	}

	onMount(load);
</script>

<svelte:head><title>Configuración — Recetario Admin</title></svelte:head>

<div class="max-w-2xl space-y-6">
	<div>
		<h1 class="font-playfair text-2xl font-medium text-foreground md:text-3xl">Configuración</h1>
		<p class="mt-1 text-muted-foreground">Flags de la aplicación, editables en caliente</p>
	</div>

	{#if error}
		<div class="rounded-md border border-destructive/30 bg-destructive/10 p-3 text-sm text-destructive" role="alert">{error}</div>
	{/if}
	{#if success}
		<div class="rounded-md border border-border bg-accent/40 p-3 text-sm text-foreground" role="status">{success}</div>
	{/if}

	{#if loading}
		<p class="text-muted-foreground">Cargando…</p>
	{:else}
		<div class="card space-y-5 p-5">
			<label class="flex items-start justify-between gap-4">
				<span>
					<span class="block text-sm font-medium text-foreground">Registro abierto</span>
					<span class="block text-xs text-muted-foreground">Permitir la creación de cuentas nuevas.</span>
				</span>
				<input type="checkbox" class="mt-1 h-4 w-4" bind:checked={settings.registration_open} />
			</label>

			<label class="flex items-start justify-between gap-4">
				<span>
					<span class="block text-sm font-medium text-foreground">Requerir verificación de email</span>
					<span class="block text-xs text-muted-foreground">Si está activo, el registro no verifica automáticamente.</span>
				</span>
				<input type="checkbox" class="mt-1 h-4 w-4" bind:checked={settings.require_email_verification} />
			</label>

			<label class="block">
				<span class="mb-1 block text-sm font-medium text-foreground">Tamaño máximo de imagen (MB)</span>
				<input
					type="number"
					min="1"
					max="50"
					class="input-base w-32"
					bind:value={settings.max_upload_size_mb}
				/>
			</label>

			<div>
				<button type="button" class="btn btn-primary" on:click={save} disabled={saving}>
					{saving ? 'Guardando…' : 'Guardar cambios'}
				</button>
			</div>
		</div>
	{/if}
</div>
