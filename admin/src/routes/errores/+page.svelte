<script lang="ts">
	import { onMount } from 'svelte';
	import { adminFetch, formatDate } from '$lib/api';

	type ErrorRow = {
		id: string;
		path: string;
		method: string;
		status_code: number;
		message: string | null;
		created_at: string;
	};

	let items: ErrorRow[] = [];
	let total = 0;
	let page = 1;
	let limit = 20;
	let statusFilter = '';
	let pathFilter = '';
	let loading = true;
	let error = '';

	$: pages = Math.max(1, Math.ceil(total / limit));

	function buildQuery(): string {
		const params = new URLSearchParams({ page: String(page), limit: String(limit) });
		if (statusFilter) params.set('status_code', statusFilter);
		if (pathFilter) params.set('path', pathFilter);
		return params.toString();
	}

	async function load() {
		loading = true;
		error = '';
		try {
			const data = await adminFetch<{ items: ErrorRow[]; total: number }>(
				`/error-log?${buildQuery()}`
			);
			items = data.items;
			total = data.total;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Error al cargar el registro';
		} finally {
			loading = false;
		}
	}

	function apply() {
		page = 1;
		load();
	}

	function go(delta: number) {
		const next = page + delta;
		if (next < 1 || next > pages) return;
		page = next;
		load();
	}

	onMount(load);
</script>

<svelte:head><title>Errores — Recetario Admin</title></svelte:head>

<div class="space-y-6">
	<div>
		<h1 class="font-playfair text-2xl font-medium text-foreground md:text-3xl">Errores del servidor</h1>
		<p class="mt-1 text-muted-foreground">Respuestas 5xx registradas</p>
	</div>

	<div class="flex flex-wrap items-end gap-3">
		<label class="block">
			<span class="mb-1 block text-xs text-muted-foreground">Status</span>
			<input class="input-base w-28" placeholder="500" bind:value={statusFilter} on:keydown={(e) => e.key === 'Enter' && apply()} />
		</label>
		<label class="block">
			<span class="mb-1 block text-xs text-muted-foreground">Ruta</span>
			<input class="input-base" placeholder="/api/v1/…" bind:value={pathFilter} on:keydown={(e) => e.key === 'Enter' && apply()} />
		</label>
		<button type="button" class="btn btn-outline" on:click={apply}>Filtrar</button>
	</div>

	{#if error}
		<div class="rounded-md border border-destructive/30 bg-destructive/10 p-3 text-sm text-destructive" role="alert">{error}</div>
	{/if}

	{#if loading}
		<p class="text-muted-foreground">Cargando…</p>
	{:else}
		<div class="card overflow-x-auto p-4">
			<table class="w-full text-sm">
				<thead>
					<tr class="border-b border-border text-left text-xs uppercase text-muted-foreground">
						<th class="py-2">Fecha</th>
						<th class="py-2">Método</th>
						<th class="py-2">Ruta</th>
						<th class="py-2">Status</th>
						<th class="py-2">Mensaje</th>
					</tr>
				</thead>
				<tbody>
					{#each items as item (item.id)}
						<tr class="border-b border-border/60">
							<td class="whitespace-nowrap py-2 text-muted-foreground">{formatDate(item.created_at)}</td>
							<td class="py-2">{item.method}</td>
							<td class="py-2 font-mono text-xs">{item.path}</td>
							<td class="py-2"><span class="badge bg-destructive/10 text-destructive">{item.status_code}</span></td>
							<td class="py-2 text-muted-foreground">{item.message ?? '—'}</td>
						</tr>
					{/each}
					{#if items.length === 0}
						<tr><td class="py-6 text-center text-muted-foreground" colspan="5">Sin errores registrados</td></tr>
					{/if}
				</tbody>
			</table>
		</div>

		<div class="flex items-center justify-between">
			<span class="text-sm text-muted-foreground">{total} entradas</span>
			<div class="flex items-center gap-2">
				<button type="button" class="btn btn-outline btn-sm" on:click={() => go(-1)} disabled={page <= 1}>Anterior</button>
				<span class="text-sm text-muted-foreground">{page} / {pages}</span>
				<button type="button" class="btn btn-outline btn-sm" on:click={() => go(1)} disabled={page >= pages}>Siguiente</button>
			</div>
		</div>
	{/if}
</div>
