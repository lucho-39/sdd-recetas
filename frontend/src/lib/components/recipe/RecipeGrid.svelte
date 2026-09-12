<script lang="ts">
	import type { Recipe } from '$lib/types';
	import RecipeCard from './RecipeCard.svelte';
	import RecipeCardSkeleton from './RecipeCardSkeleton.svelte';
	import EmptyState from '$components/common/EmptyState.svelte';

	export let recipes: Recipe[] = [];
	export let loading = false;
	export let loadingMore = false;
	export let hasMore = true;
	export let emptyVariant: 'search' | 'favorites' | 'recipes' = 'recipes';
	export let onLoadMore: () => void = () => {};

	let sentinel: HTMLDivElement | null = null;
	let observer: IntersectionObserver | null = null;

	function setSentinel(node: HTMLDivElement) {
		sentinel = node;
		observer?.disconnect();
		observer = new IntersectionObserver(
			(entries) => {
				if (entries[0].isIntersecting && hasMore && !loadingMore && !loading) {
					onLoadMore();
				}
			},
			{ rootMargin: '200px', threshold: 0.1 }
		);
		observer.observe(node);
		return {
			destroy() {
				observer?.disconnect();
			}
		};
	}
</script>

{#if loading && recipes.length === 0}
	<div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4" aria-busy="true" aria-label="Cargando recetas">
		{#each Array(8) as _}
			<RecipeCardSkeleton />
		{/each}
	</div>
{:else if recipes.length === 0}
	<EmptyState variant={emptyVariant} />
{:else}
	<div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4" role="list" aria-label="Lista de recetas">
		{#each recipes as recipe (recipe.id)}
			<RecipeCard {recipe} />
		{/each}
	</div>

	{#if hasMore}
		<div class="mt-8 flex justify-center" bind:this={setSentinel}>
			{#if loadingMore}
				<span class="inline-flex items-center gap-2 text-sm text-muted-foreground">
					<span class="h-5 w-5 animate-spin rounded-full border-2 border-primary border-t-transparent" aria-hidden="true"></span>
					Cargando más…
				</span>
			{:else}
				<button type="button" class="btn btn-outline" on:click={onLoadMore}>Cargar más recetas</button>
			{/if}
		</div>
	{/if}
{/if}
