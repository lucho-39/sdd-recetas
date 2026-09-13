<script lang="ts">
	import { onMount } from 'svelte';
	import { IconEyeOff as Hide, IconEye as Show, IconTrashFilled as Trash } from '@tabler/icons-svelte';
	import { adminFetch, formatDate } from '$lib/api';

	type RecipeRow = {
		id: string;
		slug: string;
		title: string;
		status: string;
		category?: string | null;
		author?: string | null;
		visit_count: number;
		save_count: number;
		avg_rating: number;
		created_at: string;
	};

	let items: RecipeRow[] = [];
	let search = '';
	let status = '';
	let loading = true;
	let error = '';

	async function load() {
		loading = true;
		error = '';
		try {
			const params = new URLSearchParams({ limit: '100' });
			if (search) params.set('search', search);
			if (status) params.set('status', status);
			const data = await adminFetch<{ items: RecipeRow[] }>(`/recipes?${params.toString()}`);
			items = data.items;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Error';
		} finally {
			loading = false;
		}
	}

	async function toggleVisibility(row: RecipeRow) {
		await adminFetch(`/recipes/${row.id}/visibility`, {
			method: 'PATCH',
			body: JSON.stringify({ is_public: row.status !== 'public' })
		});
		await load();
	}

	async function remove(row: RecipeRow) {
		if (!confirm(`¿Eliminar (soft delete) la receta "${row.title}"?`)) return;
		await adminFetch(`/recipes/${row.id}`, { method: 'DELETE' });
		await load();
	}

	onMount(load);
</script>

<svelte:head><title>Recetas — Recetario Admin</title></svelte:head>

<div class="space-y-6">
	<div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
		<h1 class="font-playfair text-2xl font-medium text-foreground">Recetas</h1>
		<div class="flex gap-2">
			<select bind:value={status} on:change={load} class="input-base" aria-label="Estado">
				<option value="">Todas</option>
				<option value="public">Públicas</option>
				<option value="private">Privadas</option>
				<option value="deleted">Borradas</option>
			</select>
			<input type="search" bind:value={search} on:input={load} placeholder="Buscar…" class="input-base" />
		</div>
	</div>

	{#if error}<p class="text-sm text-destructive" role="alert">{error}</p>{/if}

	<div class="card overflow-x-auto">
		<table class="w-full text-sm">
			<thead class="border-b border-border text-left text-muted-foreground">
				<tr><th class="p-3">Título</th><th class="p-3">Autor</th><th class="p-3">Categoría</th><th class="p-3">Estado</th><th class="p-3">Visitas</th><th class="p-3">Alta</th><th class="p-3 text-right">Acciones</th></tr>
			</thead>
			<tbody>
				{#each items as row (row.id)}
					<tr class="border-b border-border last:border-0">
						<td class="p-3 font-medium text-foreground">{row.title}</td>
						<td class="p-3 text-muted-foreground">{row.author ?? '—'}</td>
						<td class="p-3 text-muted-foreground">{row.category ?? '—'}</td>
						<td class="p-3">
							<span class="badge {row.status === 'public' ? 'bg-success/10 text-success' : row.status === 'deleted' ? 'bg-destructive/10 text-destructive' : 'bg-muted text-muted-foreground'}">{row.status}</span>
						</td>
						<td class="p-3">{row.visit_count}</td>
						<td class="p-3 text-muted-foreground">{formatDate(row.created_at)}</td>
						<td class="p-3 text-right">
							<button type="button" class="btn btn-ghost btn-sm" on:click={() => toggleVisibility(row)} title={row.status === 'public' ? 'Ocultar' : 'Publicar'}>
								{#if row.status === 'public'}<Hide class="h-4 w-4" aria-hidden="true" />{:else}<Show class="h-4 w-4" aria-hidden="true" />{/if}
							</button>
							<button type="button" class="btn btn-ghost btn-sm text-destructive" on:click={() => remove(row)} disabled={row.status === 'deleted'}><Trash class="h-4 w-4" aria-hidden="true" /></button>
						</td>
					</tr>
				{/each}
				{#if !loading && items.length === 0}
					<tr><td class="p-6 text-center text-muted-foreground" colspan="7">Sin recetas</td></tr>
				{/if}
			</tbody>
		</table>
	</div>
</div>
