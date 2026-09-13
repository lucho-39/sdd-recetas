<script lang="ts">
	import { onMount } from 'svelte';
	import { adminFetch, formatDate } from '$lib/api';

	type AuditItem = {
		id: string;
		actor_name: string | null;
		action: string;
		target_type: string | null;
		target_id: string | null;
		detail: Record<string, unknown> | null;
		created_at: string;
	};

	let items: AuditItem[] = [];
	let total = 0;
	let page = 1;
	let limit = 20;
	let actionFilter = '';
	let targetFilter = '';
	let loading = true;
	let error = '';

	$: pages = Math.max(1, Math.ceil(total / limit));

	function buildQuery(): string {
		const params = new URLSearchParams({ page: String(page), limit: String(limit) });
		if (actionFilter) params.set('action', actionFilter);
		if (targetFilter) params.set('target_type', targetFilter);
		return params.toString();
	}

	async function load() {
		loading = true;
		error = '';
		try {
			const data = await adminFetch<{ items: AuditItem[]; total: number }>(
				`/audit-log?${buildQuery()}`
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

	function summarize(detail: Record<string, unknown> | null): string {
		if (!detail || Object.keys(detail).length === 0) return '—';
		const text = JSON.stringify(detail);
		return text.length > 80 ? `${text.slice(0, 77)}…` : text;
	}

	onMount(load);
</script>

<svelte:head><title>Audit log — Recetario Admin</title></svelte:head>

<div class="space-y-6">
	<div>
		<h1 class="font-playfair text-2xl font-medium text-foreground md:text-3xl">Audit log</h1>
		<p class="mt-1 text-muted-foreground">Registro de acciones administrativas</p>
	</div>

	<div class="flex flex-wrap items-end gap-3">
		<label class="block">
			<span class="mb-1 block text-xs text-muted-foreground">Acción</span>
			<input class="input-base" placeholder="p. ej. user, recipe" bind:value={actionFilter} on:keydown={(e) => e.key === 'Enter' && apply()} />
		</label>
		<label class="block">
			<span class="mb-1 block text-xs text-muted-foreground">Tipo</span>
			<input class="input-base" placeholder="recipe, user, tag…" bind:value={targetFilter} on:keydown={(e) => e.key === 'Enter' && apply()} />
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
						<th class="py-2">Actor</th>
						<th class="py-2">Acción</th>
						<th class="py-2">Objetivo</th>
						<th class="py-2">Detalle</th>
					</tr>
				</thead>
				<tbody>
					{#each items as item (item.id)}
						<tr class="border-b border-border/60">
							<td class="whitespace-nowrap py-2 text-muted-foreground">{formatDate(item.created_at)}</td>
							<td class="py-2">{item.actor_name ?? '—'}</td>
							<td class="py-2"><span class="badge bg-muted text-muted-foreground">{item.action}</span></td>
							<td class="py-2 text-muted-foreground">
								{item.target_type ?? '—'}{item.target_id ? ` · ${item.target_id.slice(0, 8)}` : ''}
							</td>
							<td class="py-2 font-mono text-xs text-muted-foreground">{summarize(item.detail)}</td>
						</tr>
					{/each}
					{#if items.length === 0}
						<tr><td class="py-6 text-center text-muted-foreground" colspan="5">Sin resultados</td></tr>
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
