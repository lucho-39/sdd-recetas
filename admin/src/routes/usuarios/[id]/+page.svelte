<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { IconArrowLeft as Back } from '@tabler/icons-svelte';
	import { adminFetch, formatDate } from '$lib/api';

	// GET /api/admin/users/{id} — UC-ADMIN-006 AC1 (panel) + AC3 (métricas).
	type Detail = {
		id: string;
		email: string;
		display_name: string;
		avatar_url?: string | null;
		role: string;
		is_active: boolean;
		is_verified: boolean;
		provider: string;
		created_at: string;
		last_login_at?: string | null;
		deactivated_at?: string | null;
		deleted_at?: string | null;
		recipes_count: number;
		recipes_public: number;
		recipes_private: number;
		recipes_deleted: number;
		favorites_count: number;
		ratings_count: number;
		ratings_average: number | null;
	};

	// UC-ADMIN-006 AC2: four tabs, four shapes, one pager.
	type Tab = 'recipes' | 'favorites' | 'ratings' | 'visits';
	type RecipeRow = {
		id: string;
		title: string;
		slug: string;
		is_public: boolean;
		deleted_at?: string | null;
		avg_rating: number;
		rating_count: number;
		visit_count: number;
		created_at: string;
	};
	type FavoriteRow = {
		recipe_id: string;
		title: string;
		slug: string;
		is_public: boolean;
		collection_name?: string | null;
		created_at: string;
	};
	type RatingRow = {
		recipe_title: string;
		recipe_slug: string;
		score: number;
		review_text?: string | null;
		created_at: string;
	};
	type VisitRow = { recipe_title: string; recipe_slug: string; visited_at: string };

	const TABS: { k: Tab; l: string }[] = [
		{ k: 'recipes', l: 'Recetas' },
		{ k: 'favorites', l: 'Favoritos' },
		{ k: 'ratings', l: 'Calificaciones' },
		{ k: 'visits', l: 'Visitas' }
	];

	let user: Detail | null = null;
	let error = '';

	let tab: Tab = 'recipes';
	let currentPage = 1;
	const limit = 20;
	let total = 0;
	let rows: (RecipeRow | FavoriteRow | RatingRow | VisitRow)[] = [];
	let loadingTab = false;

	$: pages = Math.max(1, Math.ceil(total / limit));

	// One endpoint per tab means one shape per tab; narrowing here keeps the
	// markup free of casts while the union stays a single load() target.
	$: recipeRows = tab === 'recipes' ? (rows as RecipeRow[]) : [];
	$: favoriteRows = tab === 'favorites' ? (rows as FavoriteRow[]) : [];
	$: ratingRows = tab === 'ratings' ? (rows as RatingRow[]) : [];
	$: visitRows = tab === 'visits' ? (rows as VisitRow[]) : [];

	async function loadUser() {
		error = '';
		try {
			user = await adminFetch<Detail>(`/users/${$page.params.id}`);
		} catch (err) {
			error = err instanceof Error ? err.message : 'No se pudo cargar el usuario';
		}
	}

	async function loadTab() {
		loadingTab = true;
		error = '';
		try {
			const data = await adminFetch<{
				items: (RecipeRow | FavoriteRow | RatingRow | VisitRow)[];
				total: number;
			}>(`/users/${$page.params.id}/${tab}?page=${currentPage}&limit=${limit}`);
			rows = data.items;
			total = data.total;
		} catch (err) {
			error = err instanceof Error ? err.message : 'No se pudo cargar la pestaña';
		} finally {
			loadingTab = false;
		}
	}

	function selectTab(next: Tab) {
		if (tab === next) return;
		tab = next;
		currentPage = 1;
		void loadTab();
	}

	function go(delta: number) {
		const next = currentPage + delta;
		if (next < 1 || next > pages) return;
		currentPage = next;
		void loadTab();
	}

	// UC-ADMIN-006 AC4: three states, three colours — and "deleted" is not
	// the same as "inactive" even though both carry is_active=false.
	function accountState(d: Detail) {
		if (d.deleted_at)
			return { label: 'Eliminado (GDPR)', cls: 'bg-destructive/10 text-destructive' };
		if (!d.is_active) return { label: 'Inactivo', cls: 'bg-warning/10 text-warning' };
		return { label: 'Activo', cls: 'bg-success/10 text-success' };
	}

	// UC-ADMIN-006 AC3: the breakdown is its own rows, not a tooltip — an
	// admin auditing an account wants public vs private vs deleted at a
	// glance, not derived from one total.
	function metrics(d: Detail) {
		return [
			{ label: 'Recetas', value: String(d.recipes_count) },
			{ label: 'Públicas', value: String(d.recipes_public) },
			{ label: 'Privadas', value: String(d.recipes_private) },
			{ label: 'Borradas', value: String(d.recipes_deleted) },
			{ label: 'Favoritos', value: String(d.favorites_count) },
			{ label: 'Calificaciones dadas', value: String(d.ratings_count) },
			{
				label: 'Promedio dado',
				value: d.ratings_average === null ? '—' : d.ratings_average.toFixed(1)
			}
		];
	}

	function facts(d: Detail) {
		return [
			{ label: 'Email', value: d.email },
			{ label: 'Proveedor', value: d.provider },
			{ label: 'Rol', value: d.role },
			{ label: 'Verificada', value: d.is_verified ? 'Sí' : 'No' },
			{ label: 'Alta', value: formatDate(d.created_at) },
			{ label: 'Último login', value: d.last_login_at ? formatDate(d.last_login_at) : '—' },
			{ label: 'Desactivada', value: d.deactivated_at ? formatDate(d.deactivated_at) : '—' }
		];
	}

	onMount(async () => {
		await loadUser();
		await loadTab();
	});
</script>

<svelte:head>
	<title>{user?.display_name ?? 'Usuario'} — Recetario Admin</title>
</svelte:head>

<div class="space-y-6">
	<a
		href="/usuarios"
		class="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
	>
		<Back class="h-4 w-4" aria-hidden="true" />
		Volver a usuarios
	</a>

	{#if error}<p class="text-sm text-destructive" role="alert">{error}</p>{/if}

	{#if user}
		<!-- UC-ADMIN-006 AC1: the basic panel, AC4's badge alongside it. -->
		<div class="flex flex-wrap items-center gap-4">
			{#if user.avatar_url}
				<img
					src={user.avatar_url}
					alt=""
					class="h-14 w-14 rounded-full object-cover"
					referrerpolicy="no-referrer"
				/>
			{:else}
				<span
					class="flex h-14 w-14 items-center justify-center rounded-full bg-muted text-lg font-medium text-muted-foreground"
					aria-hidden="true"
				>
					{user.display_name.slice(0, 1).toUpperCase()}
				</span>
			{/if}
			<div class="min-w-0">
				<div class="flex flex-wrap items-center gap-2">
					<h1 class="font-playfair text-2xl font-medium text-foreground">
						{user.display_name}
					</h1>
					<span class="badge {accountState(user).cls}">{accountState(user).label}</span>
					<span class="badge bg-muted text-muted-foreground">{user.role}</span>
				</div>
				<p class="truncate text-muted-foreground">{user.email}</p>
			</div>
		</div>

		<div class="grid gap-4 md:grid-cols-2">
			<section class="card p-4">
				<h2 class="mb-3 text-sm font-medium text-muted-foreground">Cuenta</h2>
				<dl class="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
					{#each facts(user) as fact (fact.label)}
						<dt class="text-muted-foreground">{fact.label}</dt>
						<dd class="text-foreground">{fact.value}</dd>
					{/each}
				</dl>
			</section>

			<section class="card p-4">
				<h2 class="mb-3 text-sm font-medium text-muted-foreground">Actividad</h2>
				<dl class="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
					{#each metrics(user) as metric (metric.label)}
						<dt class="text-muted-foreground">{metric.label}</dt>
						<dd class="text-right font-medium text-foreground">{metric.value}</dd>
					{/each}
				</dl>
			</section>
		</div>

		<!-- UC-ADMIN-006 AC2 -->
		<div class="flex gap-2">
			{#each TABS as t (t.k)}
				<button
					type="button"
					class="btn {tab === t.k ? 'btn-primary' : 'btn-outline'} btn-sm"
					on:click={() => selectTab(t.k)}
				>
					{t.l}
				</button>
			{/each}
		</div>

		{#if loadingTab}
			<p class="text-muted-foreground">Cargando…</p>
		{:else}
			<div class="card overflow-x-auto">
				<table class="w-full text-sm">
					<thead class="border-b border-border text-left text-muted-foreground">
						<tr>
							{#if tab === 'recipes'}
								<th class="p-3">Receta</th>
								<th class="p-3">Visibilidad</th>
								<th class="p-3">Rating</th>
								<th class="p-3">Visitas</th>
								<th class="p-3">Alta</th>
							{:else if tab === 'favorites'}
								<th class="p-3">Receta</th>
								<th class="p-3">Colección</th>
								<th class="p-3">Guardada</th>
							{:else if tab === 'ratings'}
								<th class="p-3">Receta</th>
								<th class="p-3">Puntaje</th>
								<th class="p-3">Reseña</th>
								<th class="p-3">Fecha</th>
							{:else}
								<th class="p-3">Receta</th>
								<th class="p-3">Visita</th>
							{/if}
						</tr>
					</thead>
					<tbody>
						{#if tab === 'recipes'}
							{#each recipeRows as r (r.id)}
								<tr class="border-b border-border last:border-0">
									<td class="p-3 font-medium text-foreground">{r.title}</td>
									<td class="p-3">
										<span class="badge {r.is_public ? 'bg-success/10 text-success' : 'bg-muted text-muted-foreground'}">
											{r.is_public ? 'Pública' : 'Privada'}
										</span>
									</td>
									<td class="p-3 text-muted-foreground">{r.avg_rating.toFixed(1)} ({r.rating_count})</td>
									<td class="p-3 text-muted-foreground">{r.visit_count}</td>
									<td class="p-3 text-muted-foreground">{formatDate(r.created_at)}</td>
								</tr>
							{/each}
						{:else if tab === 'favorites'}
							{#each favoriteRows as r (r.recipe_id)}
								<tr class="border-b border-border last:border-0">
									<td class="p-3 font-medium text-foreground">{r.title}</td>
									<td class="p-3 text-muted-foreground">{r.collection_name ?? '—'}</td>
									<td class="p-3 text-muted-foreground">{formatDate(r.created_at)}</td>
								</tr>
							{/each}
						{:else if tab === 'ratings'}
							{#each ratingRows as r, i (i)}
								<tr class="border-b border-border last:border-0">
									<td class="p-3 font-medium text-foreground">{r.recipe_title}</td>
									<td class="p-3">{r.score}/5</td>
									<td class="p-3 text-muted-foreground">{r.review_text ?? '—'}</td>
									<td class="p-3 text-muted-foreground">{formatDate(r.created_at)}</td>
								</tr>
							{/each}
						{:else}
							{#each visitRows as r, i (i)}
								<tr class="border-b border-border last:border-0">
									<td class="p-3 font-medium text-foreground">{r.recipe_title}</td>
									<td class="p-3 text-muted-foreground">{formatDate(r.visited_at)}</td>
								</tr>
							{/each}
						{/if}
						{#if rows.length === 0}
							<tr>
								<td class="p-6 text-center text-muted-foreground" colspan="5">Sin resultados</td>
							</tr>
						{/if}
					</tbody>
				</table>
			</div>

			<div class="flex items-center justify-between">
				<span class="text-sm text-muted-foreground">{total} registros</span>
				<div class="flex items-center gap-2">
					<button
						type="button"
						class="btn btn-outline btn-sm"
						on:click={() => go(-1)}
						disabled={currentPage <= 1}
					>
						Anterior
					</button>
					<span class="text-sm text-muted-foreground">{currentPage} / {pages}</span>
					<button
						type="button"
						class="btn btn-outline btn-sm"
						on:click={() => go(1)}
						disabled={currentPage >= pages}
					>
						Siguiente
					</button>
				</div>
			</div>
		{/if}
	{/if}
</div>
