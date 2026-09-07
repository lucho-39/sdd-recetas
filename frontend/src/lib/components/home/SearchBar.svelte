<script lang="ts">
	import { searchStore } from '$lib/stores/search';
	import { Search, Filter, X, Loader2 } from 'lucide-svelte';
	import { TagAutocomplete } from '$components/search/TagAutocomplete.svelte';
	import { IngredientAutocomplete } from '$components/search/IngredientAutocomplete.svelte';
	import { CategoryFilter } from '$components/search/CategoryFilter.svelte';
	import { onMount } from 'svelte';
	import { categoriesStore } from '$lib/stores/categories';

	export let initialFilters: any = {};
	export let onSearch: (filters: any) => void = () => {};
	export let onClear: () => void = () => {};
	export let loading = false;

	let showFilters = false;
	let query = '';
	let debounceTimer: ReturnType<typeof setTimeout>;

	function handleSearch() {
		if (debounceTimer) clearTimeout(debounceTimer);
		debounceTimer = setTimeout(() => {
			searchStore.updateFilters({ query: query.trim() || undefined });
			onSearch(searchStore.getFilters());
		}, 300);
	}

	function clearFilters() {
		searchStore.clearFilters();
		query = '';
		onClear();
	}

	function handleKeyDown(e: KeyboardEvent) {
		if (e.key === 'Escape') {
			query = '';
			clearFilters();
		}
	}

	$effect.root(() => {
		$effect(() => {
			if ($searchStore.filters.query) {
				query = $searchStore.filters.query || '';
			}
		});
	});
</script>

<div class="sticky top-16 z-40 bg-background/95 backdrop-blur-sm border-b border-border">
	<!-- Buscador principal -->
	<div class="container px-4 py-4">
		<div class="flex flex-col sm:flex-row gap-3">
			<div class="relative flex-1">
				<Search class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" aria-hidden="true" />
				<input
					type="search"
					bind:value={query}
					on:input={handleSearch}
					on:keydown={handleKeyDown}
					placeholder="Buscar por nombre, ingrediente..."
					class="input-base pl-10 pr-10"
					aria-label="Buscar recetas"
					aria-autocomplete="list"
					aria-expanded={false}
					disabled={loading}
				/>
				{#if query}
					<button
						type="button"
						class="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-muted-foreground hover:text-foreground transition-colors"
						on:click={() => { query = ''; clearFilters(); }}
						aria-label="Limpiar búsqueda"
					>
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
					</button>
				{:else if loading}
					<Loader2 class="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 animate-spin text-muted-foreground" aria-hidden="true" />
				{/if}
			</div>
			<button
				class="btn btn-outline whitespace-nowrap"
				on:click={() => showFilters = !showFilters}
				aria-expanded={showFilters}
				aria-controls="filter-sidebar"
				aria-label={showFilters ? 'Ocultar filtros' : 'Mostrar filtros'}
			>
				<Filter class="w-4 h-4 mr-2" aria-hidden="true" />
				Filtros
			</button>
		</div>

		<!-- Chips activos -->
		{#if $searchStore.hasAnyFilters}
			<div class="flex flex-wrap gap-2 mt-3 animate-fade-in" role="group" aria-label="Filtros activos">
				{#if $searchStore.filters.category}
					<span class="badge bg-[var(--color-{$searchStore.filters.category})] border-[var(--color-{$searchStore.filters.category})] text-white flex items-center gap-1">
						{#each $categoriesStore.categories as cat}
							{#if cat.slug === $searchStore.filters.category}
								{cat.icon} {cat.name}
							{/if}
						{/each}
						<button class="ml-1 p-0.5 hover:bg-white/20 rounded" on:click={() => searchStore.updateFilters({ category: undefined })} aria-label="Quitar filtro categoría">
							<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
						</button>
					</span>
				{/if}
				{#each $searchStore.filters.tags as tag}
					<span class="badge bg-muted text-muted-foreground flex items-center gap-1">
						{tag}
						<button class="ml-1 p-0.5 hover:bg-muted-foreground/20 rounded" on:click={() => searchStore.removeTag(tag)} aria-label="Quitar tag {tag}">
							<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
						</button>
					</span>
				{/each}
				{#each $searchStore.filters.ingredients as ing}
					<span class="badge bg-muted text-muted-foreground flex items-center gap-1">
						{ing}
						<button class="ml-1 p-0.5 hover:bg-muted-foreground/20 rounded" on:click={() => searchStore.removeIngredient(ing)} aria-label="Quitar ingrediente {ing}">
							<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
						</button>
					</span>
				{/each}
				<button class="btn btn-ghost btn-sm" on:click={clearFilters}>
					Limpiar todo
				</button>
			</div>
		{/if}
	</div>

	<!-- Sidebar de filtros (Sheet en móvil) -->
	{#if showFilters}
		<div class="fixed inset-0 z-50 md:hidden" role="dialog" aria-modal="true" aria-labelledby="filter-title">
			<div class="fixed inset-0 bg-black/50 backdrop-blur-sm" on:click={() => showFilters = false} aria-hidden="true" />
			<div class="fixed right-0 top-0 h-full w-96 max-w-[90vw] bg-background border-l border-border shadow-xl animate-slide-up" role="document">
				<div class="flex items-center justify-between p-4 border-b border-border">
					<h2 id="filter-title" class="text-lg font-semibold">Filtros</h2>
					<button class="p-2 rounded-md hover:bg-accent" on:click={() => showFilters = false} aria-label="Cerrar filtros">
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
					</button>
				</div>
				<div class="p-4 space-y-6 overflow-y-auto max-h-[calc(100vh-120px)]">
					<div>
						<h3 class="font-medium mb-3">Categoría</h3>
						<CategoryFilter
							selected={$searchStore.filters.category}
							onChange={(slug) => searchStore.updateFilters({ category: slug })}
							categories={$categoriesStore.categories}
						/>
					</div>
					<div>
						<h3 class="font-medium mb-3">Tags</h3>
						<TagAutocomplete
							selected={$searchStore.filters.tags}
							onChange={(tags) => searchStore.updateFilters({ tags })}
						/>
					</div>
					<div>
						<h3 class="font-medium mb-3">Ingredientes</h3>
						<IngredientAutocomplete
							selected={$searchStore.filters.ingredients}
							onChange={(ingredients) => searchStore.updateFilters({ ingredients })}
						/>
					</div>
					<div class="pt-4 border-t border-border">
						<button class="btn btn-outline w-full" on:click={clearFilters}>Limpiar todo</button>
					</div>
				</div>
			</div>
		</div>
	{/if}