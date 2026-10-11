<script lang="ts">
	import { onMount } from 'svelte';
	import {
		IconCircleCheckFilled as Validate,
		IconBan as Reject,
		IconAdjustmentsFilled as Normalize,
		IconGitMerge as Merge,
		IconArrowBackUp as Recover,
		IconEyeOff as Desvalidate,
		IconChevronLeft as Prev,
		IconChevronRight as Next
	} from '@tabler/icons-svelte';
	import { adminFetch, formatDate } from '$lib/api';
	import Dialog from '$lib/components/Dialog.svelte';
	import AlertDialog from '$lib/components/AlertDialog.svelte';
	import { VALID_CATEGORIES, VALID_UNITS, REJECTION_REASONS } from '$lib/units';

	type Ingredient = {
		id: string;
		slug: string;
		name: string;
		category: string;
		default_unit: string;
		aliases: string[];
		usage_count: number;
		is_active: boolean;
		validated_by_admin: boolean;
		validated_at?: string | null;
		rejected: boolean;
		rejection_reason?: string | null;
		rejected_at?: string | null;
		created_by_email?: string | null;
		created_at: string;
	};

	type Tab = 'pending' | 'validated' | 'rejected';

	const LIMIT = 20;

	let tab: Tab = 'pending';
	let items: Ingredient[] = [];
	let page = 1;
	let total = 0;
	let search = '';
	let category = '';
	let loading = true;
	let error = '';
	let message = '';

	/** UC-013/017: validar y desvalidar son un sí/no, así que comparten confirmación. */
	let confirmKind: 'validate' | 'desvalidate' | null = null;
	let confirmItem: Ingredient | null = null;
	let busy = false;

	let rejectItem: Ingredient | null = null;
	let rejectReason: string = REJECTION_REASONS[0];
	let rejectOther = '';

	let mergeItem: Ingredient | null = null;
	let mergeQuery = '';
	let mergeCandidates: Ingredient[] = [];
	let mergeTargetId = '';

	let normalizeItem: Ingredient | null = null;
	let nName = '';
	let nSlug = '';
	let nCategory = '';
	let nUnit = '';
	let nAliases = '';

	let recoverItem: Ingredient | null = null;
	let recoverReason = '';

	const totalPages = () => Math.max(1, Math.ceil(total / LIMIT));

	async function load() {
		loading = true;
		error = '';
		try {
			const params = new URLSearchParams({
				limit: String(LIMIT),
				page: String(page)
			});
			if (search) params.set('search', search);
			if (category) params.set('category', category);
			const data = await adminFetch<{ items: Ingredient[]; total: number }>(
				`/ingredients/${tab}?${params.toString()}`
			);
			items = data.items;
			total = data.total;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Error';
		} finally {
			loading = false;
		}
	}

	function selectTab(next: Tab) {
		if (tab === next) return;
		tab = next;
		page = 1;
		load();
	}

	function goTo(next: number) {
		page = Math.min(Math.max(1, next), totalPages());
		load();
	}

	function onSearch() {
		page = 1;
		load();
	}

	function openConfirm(kind: 'validate' | 'desvalidate', item: Ingredient) {
		confirmKind = kind;
		confirmItem = item;
	}

	async function runConfirm() {
		if (!confirmKind || !confirmItem) return;
		busy = true;
		error = message = '';
		try {
			await adminFetch(`/ingredients/${confirmItem.id}/${confirmKind}`, { method: 'POST' });
			message = confirmKind === 'validate' ? 'Ingrediente validado' : 'Vuelto a pendientes';
			confirmKind = confirmItem = null;
			await load();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Error';
		} finally {
			busy = false;
		}
	}

	function openReject(item: Ingredient) {
		rejectItem = item;
		rejectReason = REJECTION_REASONS[0];
		rejectOther = '';
	}

	async function submitReject() {
		if (!rejectItem) return;
		const reason = rejectReason === 'Otro' ? rejectOther.trim() : rejectReason;
		if (reason.length < 3) {
			error = 'La razón debe tener al menos 3 caracteres';
			return;
		}
		busy = true;
		error = message = '';
		try {
			await adminFetch(`/ingredients/${rejectItem.id}/reject`, {
				method: 'POST',
				body: JSON.stringify({ reason })
			});
			message = 'Ingrediente rechazado';
			rejectItem = null;
			await load();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Error';
		} finally {
			busy = false;
		}
	}

	/** UC-015 AC1: the target is picked from the official catalogue, never typed. */
	async function searchMergeCandidates() {
		if (!mergeQuery.trim()) {
			mergeCandidates = [];
			return;
		}
		try {
			const data = await adminFetch<{ items: Ingredient[] }>(
				`/ingredients/validated?search=${encodeURIComponent(mergeQuery.trim())}&limit=10`
			);
			mergeCandidates = data.items.filter(
				(candidate: Ingredient) => candidate.id !== mergeItem?.id
			);
		} catch {
			mergeCandidates = [];
		}
	}

	function openMerge(item: Ingredient) {
		mergeItem = item;
		mergeQuery = '';
		mergeCandidates = [];
		mergeTargetId = '';
	}

	async function submitMerge() {
		if (!mergeItem || !mergeTargetId) {
			error = 'Elegí un ingrediente destino del catálogo oficial';
			return;
		}
		busy = true;
		error = message = '';
		try {
			const result = await adminFetch<{ recipes_updated: number }>(
				`/ingredients/${mergeItem.id}/merge`,
				{ method: 'POST', body: JSON.stringify({ target_id: mergeTargetId }) }
			);
			message = `Fusionado. Recetas actualizadas: ${result.recipes_updated}`;
			mergeItem = null;
			await load();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Error';
		} finally {
			busy = false;
		}
	}

	function openNormalize(item: Ingredient) {
		normalizeItem = item;
		nName = item.name;
		nSlug = item.slug;
		nCategory = item.category;
		nUnit = item.default_unit;
		nAliases = item.aliases.join(', ');
	}

	async function submitNormalize() {
		if (!normalizeItem) return;
		if (nName.trim().length < 2 || nSlug.trim().length < 2) {
			error = 'Nombre y slug son requeridos';
			return;
		}
		const aliases = nAliases
			.split(',')
			.map((a) => a.trim())
			.filter(Boolean);
		busy = true;
		error = message = '';
		try {
			await adminFetch(`/ingredients/${normalizeItem.id}/normalize`, {
				method: 'POST',
				body: JSON.stringify({
					name: nName.trim(),
					slug: nSlug.trim(),
					category: nCategory,
					default_unit: nUnit,
					aliases
				})
			});
			message = 'Ingrediente normalizado';
			normalizeItem = null;
			await load();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Error';
		} finally {
			busy = false;
		}
	}

	function openRecover(item: Ingredient) {
		recoverItem = item;
		recoverReason = '';
	}

	async function submitRecover() {
		if (!recoverItem || recoverReason.trim().length < 3) {
			error = 'La razón debe tener al menos 3 caracteres';
			return;
		}
		busy = true;
		error = message = '';
		try {
			await adminFetch(`/ingredients/${recoverItem.id}/recover`, {
				method: 'POST',
				body: JSON.stringify({ reason: recoverReason.trim() })
			});
			message = 'Ingrediente recuperado';
			recoverItem = null;
			await load();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Error';
		} finally {
			busy = false;
		}
	}

	onMount(load);
</script>

<svelte:head><title>Ingredientes — Recetario Admin</title></svelte:head>

<div class="space-y-6">
	<div class="flex flex-col gap-3 sm:flex-row sm:items-end">
		<div class="flex-1">
			<h1 class="font-playfair text-2xl font-medium text-foreground">Ingredientes</h1>
			<p class="text-sm text-muted-foreground">{total} en esta vista</p>
		</div>
		<div class="flex flex-1 flex-wrap gap-2 sm:max-w-md">
			<label class="sr-only" for="q">Buscar por nombre o slug</label>
			<input
				id="q"
				type="search"
				bind:value={search}
				on:input={onSearch}
				placeholder="Buscar…"
				class="input-base flex-1"
			/>
			<label class="sr-only" for="cat">Filtrar por categoría</label>
			<select id="cat" bind:value={category} on:change={onSearch} class="input-base">
				<option value="">Todas las categorías</option>
				{#each VALID_CATEGORIES as c}
					<option value={c}>{c}</option>
				{/each}
			</select>
		</div>
	</div>

	<div class="flex gap-2">
		{#each [{ k: 'pending', l: 'Pendientes' }, { k: 'validated', l: 'Validados' }, { k: 'rejected', l: 'Rechazados' }] as t}
			<button
				type="button"
				class="btn {tab === t.k ? 'btn-primary' : 'btn-outline'} btn-sm"
				on:click={() => selectTab(t.k as Tab)}
			>
				{t.l}
			</button>
		{/each}
	</div>

	{#if message}<p class="text-sm text-success" role="status">{message}</p>{/if}
	{#if error}<p class="text-sm text-destructive" role="alert">{error}</p>{/if}

	<div class="card overflow-x-auto">
		<table class="w-full text-sm">
			<thead class="border-b border-border text-left text-muted-foreground">
				<tr>
					<th class="p-3">Nombre</th>
					<th class="p-3">Categoría</th>
					<th class="p-3">Unidad</th>
					<th class="p-3">Usos</th>
					<th class="p-3">Aliases</th>
					<th class="p-3">Creado por</th>
					<th class="p-3">Fecha</th>
					{#if tab === 'rejected'}
						<th class="p-3">Razón</th>
					{/if}
					<th class="p-3 text-right">Acciones</th>
				</tr>
			</thead>
			<tbody>
				{#each items as item (item.id)}
					<tr class="border-b border-border last:border-0">
						<td class="p-3 font-medium text-foreground">
							{item.name}
							<span class="ml-2 text-xs text-muted-foreground">{item.slug}</span>
						</td>
						<td class="p-3 text-muted-foreground">{item.category}</td>
						<td class="p-3 text-muted-foreground">{item.default_unit}</td>
						<td class="p-3 text-muted-foreground">{item.usage_count}</td>
						<td class="p-3 text-muted-foreground">
							{#if item.aliases.length}
								{item.aliases.join(', ')}
							{:else}
								—
							{/if}
						</td>
						<td class="p-3 text-muted-foreground">{item.created_by_email ?? 'seed'}</td>
						<td class="p-3 text-muted-foreground">{formatDate(item.created_at)}</td>
						{#if tab === 'rejected'}
							<td class="p-3 text-muted-foreground">{item.rejection_reason ?? '—'}</td>
						{/if}
						<td class="p-3 text-right">
							{#if tab === 'pending'}
								<button
									type="button"
									class="btn btn-ghost btn-sm text-success"
									title="Validar"
									aria-label="Validar {item.name}"
									on:click={() => openConfirm('validate', item)}
								>
									<Validate class="h-4 w-4" aria-hidden="true" />
								</button>
							{/if}
							{#if tab === 'validated'}
								<button
									type="button"
									class="btn btn-ghost btn-sm"
									title="Desvalidar"
									aria-label="Desvalidar {item.name}"
									on:click={() => openConfirm('desvalidate', item)}
								>
									<Desvalidate class="h-4 w-4" aria-hidden="true" />
								</button>
							{/if}
							<button
								type="button"
								class="btn btn-ghost btn-sm"
								title="Normalizar"
								aria-label="Normalizar {item.name}"
								on:click={() => openNormalize(item)}
							>
								<Normalize class="h-4 w-4" aria-hidden="true" />
							</button>
							{#if tab !== 'rejected'}
								<button
									type="button"
									class="btn btn-ghost btn-sm"
									title="Fusionar en otro"
									aria-label="Fusionar {item.name}"
									on:click={() => openMerge(item)}
								>
									<Merge class="h-4 w-4" aria-hidden="true" />
								</button>
								<button
									type="button"
									class="btn btn-ghost btn-sm text-destructive"
									title="Rechazar"
									aria-label="Rechazar {item.name}"
									on:click={() => openReject(item)}
								>
									<Reject class="h-4 w-4" aria-hidden="true" />
								</button>
							{:else}
								<button
									type="button"
									class="btn btn-ghost btn-sm"
									title="Recuperar a pendientes"
									aria-label="Recuperar {item.name}"
									on:click={() => openRecover(item)}
								>
									<Recover class="h-4 w-4" aria-hidden="true" />
								</button>
							{/if}
						</td>
					</tr>
				{/each}
				{#if !loading && items.length === 0}
					<tr>
						<td class="p-6 text-center text-muted-foreground" colspan="8">Sin ingredientes</td>
					</tr>
				{/if}
			</tbody>
		</table>
	</div>

	{#if totalPages() > 1}
		<div class="flex items-center justify-between">
			<p class="text-sm text-muted-foreground">
				Página {page} de {totalPages()}
			</p>
			<div class="flex gap-2">
				<button
					type="button"
					class="btn btn-outline btn-sm"
					disabled={page <= 1}
					on:click={() => goTo(page - 1)}
				>
					<Prev class="h-4 w-4" aria-hidden="true" /> Anterior
				</button>
				<button
					type="button"
					class="btn btn-outline btn-sm"
					disabled={page >= totalPages()}
					on:click={() => goTo(page + 1)}
				>
					Siguiente <Next class="h-4 w-4" aria-hidden="true" />
				</button>
			</div>
		</div>
	{/if}
</div>

<!-- UC-013 AC1 / UC-017 AC3: both are a yes/no, so they share one confirmation. -->
<AlertDialog
	open={confirmKind !== null && confirmItem !== null}
	title={confirmKind === 'desvalidate' ? 'Desvalidar ingrediente' : 'Validar ingrediente'}
	description={confirmKind === 'desvalidate'
		? 'Vuelve a la cola de pendientes. Las recetas que ya lo usan no se tocan.'
		: 'Pasa al catálogo oficial y aparece en el autocomplete público.'}
	confirmLabel={confirmKind === 'desvalidate' ? 'Desvalidar' : 'Validar'}
	loading={busy}
	onConfirm={runConfirm}
	onClose={() => ((confirmKind = null), (confirmItem = null))}
>
	{#if confirmItem}
		<dl class="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
			<dt class="text-muted-foreground">Nombre</dt>
			<dd class="text-foreground">{confirmItem.name}</dd>
			<dt class="text-muted-foreground">Slug</dt>
			<dd class="text-foreground">{confirmItem.slug}</dd>
			<dt class="text-muted-foreground">Categoría</dt>
			<dd class="text-foreground">{confirmItem.category}</dd>
			<dt class="text-muted-foreground">Unidad</dt>
			<dd class="text-foreground">{confirmItem.default_unit}</dd>
			<dt class="text-muted-foreground">Aliases</dt>
			<dd class="text-foreground">{confirmItem.aliases.join(', ') || '—'}</dd>
		</dl>
	{/if}
</AlertDialog>

<!-- UC-016 AC1: preset reasons, and "Otro" opens a free-text field. -->
<Dialog
	open={rejectItem !== null}
	title="Rechazar ingrediente"
	description={rejectItem ? `Vas a rechazar "${rejectItem.name}".` : null}
	onClose={() => ((rejectItem = null), (error = ''))}
>
	<div class="space-y-3">
		<label class="label" for="reject-reason">Razón</label>
		<select id="reject-reason" bind:value={rejectReason} class="input-base">
			{#each REJECTION_REASONS as r}
				<option value={r}>{r}</option>
			{/each}
		</select>
		{#if rejectReason === 'Otro'}
			<label class="label" for="reject-other">Detalle</label>
			<input
				id="reject-other"
				type="text"
				bind:value={rejectOther}
				placeholder="Contá por qué"
				class="input-base"
			/>
		{/if}
	</div>
	<svelte:fragment slot="footer">
		<button type="button" class="btn btn-outline btn-sm" on:click={() => (rejectItem = null)}>
			Cancelar
		</button>
		<button
			type="button"
			class="btn btn-destructive btn-sm"
			disabled={busy}
			on:click={submitReject}
		>
			Rechazar
		</button>
	</svelte:fragment>
</Dialog>

<!-- UC-015 AC1: the destination is picked from the official catalogue. -->
<Dialog
	open={mergeItem !== null}
	title="Fusionar ingrediente"
	description={mergeItem
		? `Las recetas de "${mergeItem.name}" pasan al ingrediente destino y el duplicado se elimina.`
		: null}
	onClose={() => ((mergeItem = null), (error = ''))}
>
	<div class="space-y-3">
		<label class="label" for="merge-q">Buscar en el catálogo oficial</label>
		<input
			id="merge-q"
			type="search"
			bind:value={mergeQuery}
			on:input={searchMergeCandidates}
			placeholder="Nombre o slug…"
			class="input-base"
		/>
		{#if mergeCandidates.length}
			<label class="label" for="merge-target">Destino</label>
			<select id="merge-target" bind:value={mergeTargetId} class="input-base">
				<option value="">Elegí un destino…</option>
				{#each mergeCandidates as c}
					<option value={c.id}>{c.name} ({c.slug})</option>
				{/each}
			</select>
		{:else if mergeQuery.trim()}
			<p class="text-sm text-muted-foreground">Sin coincidencias en el catálogo oficial.</p>
		{/if}
	</div>
	<svelte:fragment slot="footer">
		<button type="button" class="btn btn-outline btn-sm" on:click={() => (mergeItem = null)}>
			Cancelar
		</button>
		<button
			type="button"
			class="btn btn-destructive btn-sm"
			disabled={busy || !mergeTargetId}
			on:click={submitMerge}
		>
			Fusionar
		</button>
	</svelte:fragment>
</Dialog>

<!-- UC-014/019: every catalogue field is editable before it is saved. -->
<Dialog
	open={normalizeItem !== null}
	title="Normalizar ingrediente"
	description={normalizeItem ? `Editando "${normalizeItem.name}".` : null}
	onClose={() => ((normalizeItem = null), (error = ''))}
>
	<div class="space-y-3">
		<div>
			<label class="label" for="n-name">Nombre</label>
			<input id="n-name" type="text" bind:value={nName} class="input-base" />
		</div>
		<div>
			<label class="label" for="n-slug">Slug</label>
			<input id="n-slug" type="text" bind:value={nSlug} class="input-base" />
		</div>
		<div class="grid grid-cols-2 gap-3">
			<div>
				<label class="label" for="n-cat">Categoría</label>
				<select id="n-cat" bind:value={nCategory} class="input-base">
					{#each VALID_CATEGORIES as c}
						<option value={c}>{c}</option>
					{/each}
				</select>
			</div>
			<div>
				<label class="label" for="n-unit">Unidad por defecto</label>
				<select id="n-unit" bind:value={nUnit} class="input-base">
					{#each VALID_UNITS as u}
						<option value={u}>{u}</option>
					{/each}
				</select>
			</div>
		</div>
		<div>
			<label class="label" for="n-aliases">Aliases (separados por coma)</label>
			<textarea id="n-aliases" bind:value={nAliases} rows="2" class="input-base"></textarea>
		</div>
	</div>
	<svelte:fragment slot="footer">
		<button type="button" class="btn btn-outline btn-sm" on:click={() => (normalizeItem = null)}>
			Cancelar
		</button>
		<button type="button" class="btn btn-primary btn-sm" disabled={busy} on:click={submitNormalize}>
			Guardar
		</button>
	</svelte:fragment>
</Dialog>

<!-- UC-018 AC3: recovery needs a reason, which lands in the audit log. -->
<Dialog
	open={recoverItem !== null}
	title="Recuperar ingrediente"
	description={recoverItem
		? `"${recoverItem.name}" vuelve a la cola de pendientes.`
		: null}
	onClose={() => ((recoverItem = null), (error = ''))}
>
	<div>
		<label class="label" for="recover-reason">Por qué se recupera</label>
		<input
			id="recover-reason"
			type="text"
			bind:value={recoverReason}
			placeholder="Ej.: era un falso positivo"
			class="input-base"
		/>
	</div>
	<svelte:fragment slot="footer">
		<button type="button" class="btn btn-outline btn-sm" on:click={() => (recoverItem = null)}>
			Cancelar
		</button>
		<button
			type="button"
			class="btn btn-primary btn-sm"
			disabled={busy || recoverReason.trim().length < 3}
			on:click={submitRecover}
		>
			Recuperar
		</button>
	</svelte:fragment>
</Dialog>
