<script lang="ts">
	import { RecipeCard } from './RecipeCard.svelte';
	import { RecipeCardSkeleton } from './RecipeCardSkeleton.svelte';
	import { EmptyState } from '$components/common/EmptyState.svelte';

	export let recipes: any[] = [];
	export let loading = false;
	export let loadingMore = false;
	export let hasMore = true;
	export let emptyVariant: 'search' | 'favorites' | 'recipes' = 'search';
	export let onLoadMore: () => void = () => {};

	let sentinel: HTMLDivElement | null = null;

	async function handleIntersection(entries: IntersectionObserverEntry[]) {
		if (entries[0].isIntersecting && hasMore && !loadingMore) {
			dispatch('loadMore');
		}
	}

	let observer: IntersectionObserver | null = null;

	function setSentinel(node: HTMLDivElement) {
		sentinel = node;
		if (observer) observer.disconnect();
		observer = new IntersectionObserver(handleIntersection, {
			rootMargin: '200px',
			threshold: 0.1,
		});
		if (sentinel) observer.observe(sentinel);
	}
</script>

<div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6" role="list" aria-label="Lista de recetas">
	{#if loading && recipes.length === 0}
		{#each Array(8) as _}
			<RecipeCardSkeleton />
		{/each}
	{:else if recipes.length === 0}
		<div class="col-span-full">
			<EmptyState variant={emptyVariant} />
		</div>
	{:else}
		{#each recipes as recipe}
			<RecipeCard {recipe} role="listitem" />
		{/each}
		{#if hasMore}
			<div class="col-span-full" bind:this={setSentinel} aria-hidden="true">
				{#if loadingMore}
					<div class="flex justify-center py-8">
						<div class="animate-spin rounded-full h-8 w-8 border-2 border-primary border-t-transparent" aria-label="Cargando más recetas"></div>
					</div>
				{:else}
					<button
						class="col-span-full btn btn-outline py-3"
						on:click={() => dispatch('loadMore')}
						aria-label="Cargar más recetas"
					>
						Cargar más recetas
					</button>
				{/if}
			</div>
		{/if}
	{/if}
</div>