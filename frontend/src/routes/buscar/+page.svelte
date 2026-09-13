<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { browser } from '$app/environment';
	import { IconSearch, IconAdjustments } from '@tabler/icons-svelte';
	import {
		recipesStore,
		recipes,
		loading,
		loadingMore,
		hasMore
	} from '$lib/stores/recipes';
	import { categoriesStore } from '$lib/stores/categories';
	import CategoryFilter from '$components/search/CategoryFilter.svelte';
	import TagAutocomplete from '$components/search/TagAutocomplete.svelte';
	import IngredientAutocomplete from '$components/search/IngredientAutocomplete.svelte';
	import RecipeGrid from '$components/recipe/RecipeGrid.svelte';

	const DIFFICULTIES = [
		{ v: '', l: 'Todas' },
		{ v: 'easy', l: 'Fácil' },
		{ v: 'medium', l: 'Media' },
		{ v: 'hard', l: 'Difícil' }
	];
	const TIMES = [
		{ v: 0, l: 'Cualquiera' },
		{ v: 15, l: '≤ 15 min' },
		{ v: 30, l: '≤ 30 min' },
		{ v: 60, l: '≤ 60 min' }
	];
	const SORTS = [
		{ v: 'recent', l: 'Recientes' },
		{ v: 'top_rated', l: 'Mejor calificadas' },
		{ v: 'visited', l: 'Más vistas' },
		{ v: 'saved', l: 'Más guardadas' }
	];

	let query = '';
	let category: string | undefined = undefined;
	let tags: string[] = [];
	let ingredients: string[] = [];
	let difficulty = '';
	let maxTime = 0;
	let sort = 'recent';
	let mobileOpen = false;
	let debounceTimer: ReturnType<typeof setTimeout>;

	$: activeFilters = [
		query,
		category,
		difficulty,
		maxTime ? String(maxTime) : '',
		sort !== 'recent' ? sort : '',
		...tags,
		...ingredients
	].filter(Boolean).length;

	function readUrl() {
		const sp = $page.url.searchParams;
		query = sp.get('query') ?? sp.get('q') ?? '';
		category = sp.get('category') ?? undefined;
		tags = sp.getAll('tag');
		ingredients = sp.getAll('ingredient');
		difficulty = sp.get('difficulty') ?? '';
		maxTime = Number(sp.get('max_time') ?? 0);
		sort = sp.get('sort') ?? 'recent';
	}

	function buildParams(): URLSearchParams {
		const p = new URLSearchParams();
		if (query) p.set('query', query);
		if (category) p.set('category', category);
		tags.forEach((t) => p.append('tag', t));
		ingredients.forEach((i) => p.append('ingredient', i));
		if (difficulty) p.set('difficulty', difficulty);
		if (maxTime) p.set('max_time', String(maxTime));
		if (sort && sort !== 'recent') p.set('sort', sort);
		return p;
	}

	async function search() {
		recipesStore.setFilters({
			query: query || undefined,
			category,
			tags,
			ingredients,
			difficulty: difficulty || undefined,
			maxTime: maxTime || undefined,
			sort: sort as 'recent' | 'visited' | 'saved' | 'top_rated'
		});
		await recipesStore.fetchRecipes();
	}

	function apply() {
		if (browser) {
			const qs = buildParams().toString();
			goto(`/buscar${qs ? `?${qs}` : ''}`, {
				replace: true,
				noScroll: true,
				keepFocus: true
			});
		}
		search();
	}

	function onSearchInput() {
		if (debounceTimer) clearTimeout(debounceTimer);
		debounceTimer = setTimeout(apply, 300);
	}

	function clearAll() {
		query = '';
		category = undefined;
		tags = [];
		ingredients = [];
		difficulty = '';
		maxTime = 0;
		sort = 'recent';
		apply();
	}

	onMount(() => {
		readUrl();
		categoriesStore.fetchCategories();
		search();
	});
</script>

<svelte:head>
	<title>Buscar recetas — Recetario IA</title>
	<meta name="description" content="Encontrá recetas por categoría, etiquetas, ingredientes y más." />
</svelte:head>

<div class="container py-6 md:py-8">
	<div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
		<h1 class="font-playfair text-2xl font-medium text-foreground md:text-3xl">Buscar recetas</h1>
		<button
			type="button"
			class="btn btn-outline btn-sm self-start lg:hidden"
			on:click={() => (mobileOpen = !mobileOpen)}
			aria-expanded={mobileOpen}
		>
			<IconAdjustments class="h-4 w-4" aria-hidden="true" />
			Filtros{activeFilters ? ` (${activeFilters})` : ''}
		</button>
	</div>

	<div class="grid gap-8 lg:grid-cols-[260px_1fr]">
		<!-- Filters sidebar -->
		<aside class={mobileOpen ? 'block' : 'hidden lg:block'} aria-label="Filtros de búsqueda">
			<div class="space-y-6 rounded-lg border border-border p-4">
				<div>
					<label for="search-input" class="mb-2 block text-sm font-medium text-foreground">
						Buscar
					</label>
					<div class="relative">
						<IconSearch class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" aria-hidden="true" />
						<input
							id="search-input"
							type="search"
							bind:value={query}
							on:input={onSearchInput}
							placeholder="Nombre o descripción..."
							class="input-base pl-9"
						/>
					</div>
				</div>

				<CategoryFilter selected={category} onChange={(slug) => { category = slug; apply(); }} />

				<div>
					<span class="mb-2 block text-sm font-medium text-foreground">Etiquetas</span>
					<TagAutocomplete selected={tags} onChange={(t) => { tags = t; apply(); }} />
				</div>

				<div>
					<span class="mb-2 block text-sm font-medium text-foreground">Ingredientes</span>
					<IngredientAutocomplete selected={ingredients} onChange={(i) => { ingredients = i; apply(); }} />
				</div>

				<div>
					<label for="difficulty" class="mb-2 block text-sm font-medium text-foreground">Dificultad</label>
					<select
						id="difficulty"
						bind:value={difficulty}
						on:change={apply}
						class="input-base"
					>
						{#each DIFFICULTIES as d}<option value={d.v}>{d.l}</option>{/each}
					</select>
				</div>

				<div>
					<label for="max-time" class="mb-2 block text-sm font-medium text-foreground">Tiempo total</label>
					<select id="max-time" bind:value={maxTime} on:change={apply} class="input-base">
						{#each TIMES as t}<option value={t.v}>{t.l}</option>{/each}
					</select>
				</div>

				{#if activeFilters}
					<button type="button" class="btn btn-outline btn-sm w-full" on:click={clearAll}>
						Limpiar filtros
					</button>
				{/if}
			</div>
		</aside>

		<!-- Results -->
		<main>
			<div class="mb-4 flex items-center justify-between gap-4">
				<span class="text-sm text-muted-foreground">
					{$loading ? 'Buscando…' : `${$recipes.length} receta${$recipes.length === 1 ? '' : 's'}`}
				</span>
				<label class="flex items-center gap-2 text-sm text-muted-foreground">
					<span class="hidden sm:inline">Ordenar por</span>
					<select bind:value={sort} on:change={apply} class="input-base py-1.5">
						{#each SORTS as s}<option value={s.v}>{s.l}</option>{/each}
					</select>
				</label>
			</div>

			<RecipeGrid
				recipes={$recipes}
				loading={$loading}
				loadingMore={$loadingMore}
				hasMore={$hasMore}
				emptyVariant="search"
				onLoadMore={() => recipesStore.fetchMore()}
			/>
		</main>
	</div>
</div>
