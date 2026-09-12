<script lang="ts">
	import { goto } from '$app/navigation';
	import Hero from '$components/home/Hero.svelte';
	import SearchBar from '$components/home/SearchBar.svelte';
	import RecipeGrid from '$components/recipe/RecipeGrid.svelte';

	export let data;

	function handleSearch(filters: { query?: string; category?: string }) {
		const params = new URLSearchParams();
		if (filters.query) params.set('query', filters.query);
		if (filters.category) params.set('category', filters.category);
		const qs = params.toString();
		goto(qs ? `/?${qs}` : '/', { keepFocus: true, noScroll: true });
	}
</script>

<svelte:head>
	<title>Recetario IA — Recetas para todos los días</title>
	<meta
		name="description"
		content="Descubrí, creá y compartí recetas. Buscá por ingredientes, categorías o preferencias."
	/>
</svelte:head>

<Hero />

<SearchBar query={data.query} category={data.category} onSearch={handleSearch} />

<section class="section" aria-labelledby="recipes-heading">
	<div class="container">
		<div class="mb-6 flex items-baseline justify-between gap-4">
			<h2 id="recipes-heading" class="font-playfair text-2xl font-medium text-foreground md:text-3xl">
				{data.query || data.category ? 'Resultados' : 'Recetas destacadas'}
			</h2>
			<span class="shrink-0 text-sm text-muted-foreground">{data.total} recetas</span>
		</div>

		<RecipeGrid
			recipes={data.recipes}
			loading={false}
			loadingMore={false}
			hasMore={false}
			emptyVariant={data.query || data.category ? 'search' : 'recipes'}
			onLoadMore={() => {}}
		/>
	</div>
</section>
