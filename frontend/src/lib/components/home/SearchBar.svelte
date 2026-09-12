<script lang="ts">
	import { Search, SlidersHorizontal, X } from 'lucide-svelte';

	export let query = '';
	export let category = '';
	export let loading = false;
	export let onSearch: (filters: { query?: string; category?: string }) => void = () => {};

	const categories = [
		{ slug: 'postre', name: 'Postre', icon: '🍰' },
		{ slug: 'entrada', name: 'Entrada', icon: '🥗' },
		{ slug: 'snack', name: 'Snack', icon: '🍿' },
		{ slug: 'plato-principal', name: 'Plato principal', icon: '🍽️' },
		{ slug: 'acompañamiento', name: 'Acompañamiento', icon: '🥔' },
		{ slug: 'bebida', name: 'Bebida', icon: '🥤' },
		{ slug: 'desayuno', name: 'Desayuno', icon: '☕' },
		{ slug: 'sopa-crema', name: 'Sopa / Crema', icon: '🍲' },
		{ slug: 'ensalada', name: 'Ensalada', icon: '🥗' },
		{ slug: 'horneados', name: 'Horneados', icon: '🍞' }
	];

	let showFilters = false;
	let debounceTimer: ReturnType<typeof setTimeout>;

	function emitSearch() {
		onSearch({ query: query.trim() || undefined, category: category || undefined });
	}

	function handleInput() {
		clearTimeout(debounceTimer);
		debounceTimer = setTimeout(emitSearch, 300);
	}

	function selectCategory(slug: string) {
		category = category === slug ? '' : slug;
		emitSearch();
	}

	function clearAll() {
		query = '';
		category = '';
		emitSearch();
	}
</script>

<section class="sticky top-16 z-40 border-b border-border bg-background/95 backdrop-blur-sm" aria-label="Buscador de recetas">
	<div class="container py-3 md:py-4">
		<div class="flex flex-col gap-3 sm:flex-row">
			<div class="relative flex-1">
				<Search class="pointer-events-none absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" aria-hidden="true" />
				<input
					type="search"
					bind:value={query}
					on:input={handleInput}
					placeholder="Buscar por nombre o descripción..."
					class="input-base pl-10 pr-10"
					aria-label="Buscar recetas"
					disabled={loading}
				/>
				{#if query}
					<button
						type="button"
						class="absolute right-2 top-1/2 -translate-y-1/2 rounded p-1 text-muted-foreground hover:text-foreground"
						on:click={clearAll}
						aria-label="Limpiar búsqueda"
					>
						<X class="h-4 w-4" aria-hidden="true" />
					</button>
				{/if}
			</div>

			<button
				type="button"
				class="btn btn-outline whitespace-nowrap"
				on:click={() => (showFilters = !showFilters)}
				aria-expanded={showFilters}
				aria-controls="category-filters"
			>
				<SlidersHorizontal class="h-4 w-4" aria-hidden="true" />
				Categorías
			</button>
		</div>

		<!-- Category chips (mobile-first, always visible when open) -->
		{#if showFilters}
			<div id="category-filters" class="mt-3 flex flex-wrap gap-2" role="group" aria-label="Filtrar por categoría">
				{#each categories as cat}
					<button
						type="button"
						class="badge border transition-colors {category === cat.slug ? 'border-primary bg-primary text-primary-foreground' : 'border-border bg-muted text-muted-foreground hover:bg-accent'}"
						on:click={() => selectCategory(cat.slug)}
						aria-pressed={category === cat.slug}
					>
						<span aria-hidden="true">{cat.icon}</span>
						{cat.name}
					</button>
				{/each}
				{#if query || category}
					<button type="button" class="btn btn-ghost btn-sm" on:click={clearAll}>Limpiar</button>
				{/if}
			</div>
		{/if}
	</div>
</section>
