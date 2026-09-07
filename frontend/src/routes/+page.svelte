<script lang="ts">
	import { Hero } from '$components/home/Hero.svelte';
	import { SearchBar } from '$components/home/SearchBar.svelte';
	import { RecipeGrid } from '$components/recipe/RecipeGrid.svelte';
	import { onMount } from 'svelte';
	import { recipesStore } from '$lib/stores/recipes';

	let loading = true;
	let recipes = $derived($recipesStore.recipes);
	let hasMore = $derived($recipesStore.hasMore);
	let loadingMore = $derived($recipesStore.loadingMore);

	async function loadRecipes() {
		await recipesStore.fetchRecipes();
		loading = false;
	}

	async function loadMore() {
		await recipesStore.fetchMore();
	}

	onMount(async () => {
		await loadRecipes();
	});
</script>

<div class="min-h-screen flex flex-col">
	<Hero />
	<SearchBar />
	<section class="container section" aria-labelledby="recipes-heading">
		<div class="flex items-center justify-between mb-6">
			<h2 id="recipes-heading" class="text-2xl md:text-3xl font-playfair font-medium text-foreground">
				Recetas destacadas
			</h2>
		</div>

		{#if loading}
			{@const skeletonCount = 8}
			<div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
				{#each Array(skeletonCount) as _}
					<RecipeCardSkeleton />
				{/each}
			</div>
		{:else if recipes.length === 0}
			<EmptyState variant="recipes" />
		{:else}
			<RecipeGrid {recipes} {loadingMore} {hasMore} on:loadMore />
		{/if}
	</section>