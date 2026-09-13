<script lang="ts">
	import { onMount } from 'svelte';
	import { IconPlus as Plus, IconTrashFilled as Trash } from '@tabler/icons-svelte';
	import { adminFetch } from '$lib/api';

	type Tag = { id: string; slug: string; name: string; usage_count: number };

	let items: Tag[] = [];
	let search = '';
	let loading = true;
	let message = '';
	let error = '';
	let newName = '';
	let newSlug = '';

	async function load() {
		loading = true;
		try {
			const data = await adminFetch<{ items: Tag[] }>(
				`/tags?limit=200${search ? `&search=${encodeURIComponent(search)}` : ''}`
			);
			items = data.items;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Error';
		} finally {
			loading = false;
		}
	}

	async function create() {
		error = message = '';
		try {
			await adminFetch('/tags', { method: 'POST', body: JSON.stringify({ slug: newSlug, name: newName }) });
			newName = newSlug = '';
			message = 'Tag creado';
			await load();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Error';
		}
	}

	async function remove(item: Tag) {
		error = message = '';
		try {
			await adminFetch(`/tags/${item.id}`, { method: 'DELETE' });
			message = 'Tag eliminado';
			await load();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Error';
		}
	}

	onMount(load);
</script>

<svelte:head><title>Tags — Recetario Admin</title></svelte:head>

<div class="space-y-6">
	<div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
		<h1 class="font-playfair text-2xl font-medium text-foreground">Tags</h1>
		<input type="search" bind:value={search} on:input={load} placeholder="Buscar…" class="input-base sm:max-w-xs" />
	</div>

	{#if message}<p class="text-sm text-success">{message}</p>{/if}
	{#if error}<p class="text-sm text-destructive" role="alert">{error}</p>{/if}

	<form class="card flex flex-col gap-3 p-4 sm:flex-row sm:items-end" on:submit|preventDefault={create}>
		<div class="flex-1"><label for="tag-name" class="label">Nombre</label><input id="tag-name" bind:value={newName} class="input-base" required /></div>
		<div class="flex-1"><label for="tag-slug" class="label">Slug</label><input id="tag-slug" bind:value={newSlug} class="input-base" required /></div>
		<button type="submit" class="btn btn-primary btn-sm"><Plus class="h-4 w-4" aria-hidden="true" /> Crear</button>
	</form>

	<div class="card overflow-x-auto">
		<table class="w-full text-sm">
			<thead class="border-b border-border text-left text-muted-foreground">
				<tr><th class="p-3">Nombre</th><th class="p-3">Slug</th><th class="p-3">Uso</th><th class="p-3 text-right">Acciones</th></tr>
			</thead>
			<tbody>
				{#each items as item (item.id)}
					<tr class="border-b border-border last:border-0">
						<td class="p-3 font-medium text-foreground">{item.name}</td>
						<td class="p-3 text-muted-foreground">{item.slug}</td>
						<td class="p-3">{item.usage_count}</td>
						<td class="p-3 text-right">
							<button type="button" class="btn btn-ghost btn-sm text-destructive" on:click={() => remove(item)}><Trash class="h-4 w-4" aria-hidden="true" /></button>
						</td>
					</tr>
				{/each}
				{#if !loading && items.length === 0}
					<tr><td class="p-6 text-center text-muted-foreground" colspan="4">Sin tags</td></tr>
				{/if}
			</tbody>
		</table>
	</div>
</div>
