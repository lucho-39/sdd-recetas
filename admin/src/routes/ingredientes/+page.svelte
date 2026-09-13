<script lang="ts">
	import { onMount } from 'svelte';
	import { IconCircleCheckFilled as Validate, IconBan as Reject, IconAdjustmentsFilled as Normalize } from '@tabler/icons-svelte';
	import { adminFetch } from '$lib/api';

	type Ingredient = {
		id: string;
		slug: string;
		name: string;
		category: string;
		default_unit: string;
		aliases: string[];
		validated_by_admin: boolean;
		rejected: boolean;
		rejection_reason?: string | null;
	};

	let tab: 'pending' | 'validated' | 'rejected' = 'pending';
	let items: Ingredient[] = [];
	let search = '';
	let loading = true;
	let error = '';
	let message = '';

	let editing: Ingredient | null = null;
	let editName = '';
	let editUnit = '';

	async function load() {
		loading = true;
		error = '';
		try {
			const params = new URLSearchParams({ limit: '100' });
			if (search) params.set('search', search);
			const data = await adminFetch<{ items: Ingredient[] }>(`/ingredients/${tab}?${params.toString()}`);
			items = data.items;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Error';
		} finally {
			loading = false;
		}
	}

	function selectTab(next: typeof tab) {
		tab = next;
		load();
	}

	async function validate(item: Ingredient) {
		message = error = '';
		try {
			await adminFetch(`/ingredients/${item.id}/validate`, { method: 'POST' });
			message = 'Ingrediente validado';
			await load();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Error';
		}
	}

	async function reject(item: Ingredient) {
		const reason = prompt(`Razón del rechazo de "${item.name}":`, 'Duplicado');
		if (!reason) return;
		message = error = '';
		try {
			await adminFetch(`/ingredients/${item.id}/reject`, {
				method: 'POST',
				body: JSON.stringify({ reason })
			});
			message = 'Ingrediente rechazado';
			await load();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Error';
		}
	}

	function openNormalize(item: Ingredient) {
		editing = item;
		editName = item.name;
		editUnit = item.default_unit;
	}

	async function saveNormalize() {
		if (!editing) return;
		message = error = '';
		try {
			await adminFetch(`/ingredients/${editing.id}/normalize`, {
				method: 'POST',
				body: JSON.stringify({ name: editName, default_unit: editUnit, mark_validated: true })
			});
			message = 'Ingrediente normalizado';
			editing = null;
			await load();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Error';
		}
	}

	onMount(load);
</script>

<svelte:head><title>Ingredientes — Recetario Admin</title></svelte:head>

<div class="space-y-6">
	<div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
		<h1 class="font-playfair text-2xl font-medium text-foreground">Ingredientes</h1>
		<input type="search" bind:value={search} on:input={load} placeholder="Buscar…" class="input-base sm:max-w-xs" />
	</div>

	<div class="flex gap-2">
		{#each [{ k: 'pending', l: 'Pendientes' }, { k: 'validated', l: 'Validados' }, { k: 'rejected', l: 'Rechazados' }] as t}
			<button type="button" class="btn {tab === t.k ? 'btn-primary' : 'btn-outline'} btn-sm" on:click={() => selectTab(t.k)}>{t.l}</button>
		{/each}
	</div>

	{#if message}<p class="text-sm text-success">{message}</p>{/if}
	{#if error}<p class="text-sm text-destructive" role="alert">{error}</p>{/if}

	{#if editing}
		<form class="card flex flex-col gap-3 p-4 sm:flex-row sm:items-end" on:submit|preventDefault={saveNormalize}>
			<div class="flex-1"><label for="n-name" class="label">Nombre</label><input id="n-name" bind:value={editName} class="input-base" /></div>
			<div class="flex-1"><label for="n-unit" class="label">Unidad por defecto</label><input id="n-unit" bind:value={editUnit} class="input-base" /></div>
			<button type="submit" class="btn btn-primary btn-sm">Guardar y validar</button>
			<button type="button" class="btn btn-outline btn-sm" on:click={() => (editing = null)}>Cancelar</button>
		</form>
	{/if}

	<div class="card overflow-x-auto">
		<table class="w-full text-sm">
			<thead class="border-b border-border text-left text-muted-foreground">
				<tr><th class="p-3">Nombre</th><th class="p-3">Categoría</th><th class="p-3">Unidad</th>{#if tab === 'rejected'}<th class="p-3">Razón</th>{/if}<th class="p-3 text-right">Acciones</th></tr>
			</thead>
			<tbody>
				{#each items as item (item.id)}
					<tr class="border-b border-border last:border-0">
						<td class="p-3 font-medium text-foreground">{item.name}<span class="ml-2 text-xs text-muted-foreground">{item.slug}</span></td>
						<td class="p-3 text-muted-foreground">{item.category}</td>
						<td class="p-3 text-muted-foreground">{item.default_unit}</td>
						{#if tab === 'rejected'}<td class="p-3 text-muted-foreground">{item.rejection_reason ?? '—'}</td>{/if}
						<td class="p-3 text-right">
							{#if tab === 'pending'}
								<button type="button" class="btn btn-ghost btn-sm text-success" on:click={() => validate(item)} title="Validar"><Validate class="h-4 w-4" aria-hidden="true" /></button>
							{/if}
							<button type="button" class="btn btn-ghost btn-sm" on:click={() => openNormalize(item)} title="Normalizar"><Normalize class="h-4 w-4" aria-hidden="true" /></button>
							{#if tab !== 'rejected'}
								<button type="button" class="btn btn-ghost btn-sm text-destructive" on:click={() => reject(item)} title="Rechazar"><Reject class="h-4 w-4" aria-hidden="true" /></button>
							{/if}
						</td>
					</tr>
				{/each}
				{#if !loading && items.length === 0}
					<tr><td class="p-6 text-center text-muted-foreground" colspan="5">Sin ingredientes</td></tr>
				{/if}
			</tbody>
		</table>
	</div>
</div>
