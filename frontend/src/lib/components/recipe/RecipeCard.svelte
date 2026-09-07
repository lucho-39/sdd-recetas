<script lang="ts">
	import { Recipe } from '$lib/types';
	import { CategoryBadge } from '$components/recipe/CategoryBadge.svelte';
	import { RatingStars } from '$components/recipe/RatingStars.svelte';
	import { AuthorAvatar } from '$components/common/AuthorAvatar.svelte';
	import { Bookmark, Eye } from 'lucide-svelte';

	export let recipe: Recipe;
	export let variant: 'default' | 'compact' = 'default';
	export let onClick: () => void = () => {};

	function formatNumber(num: number): string {
		if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
		if (num >= 1000) return (num / 1000).toFixed(1) + 'k';
		return num.toString();
	}
</script>

<article
	class="group relative flex flex-col h-full bg-card rounded-xl border border-border shadow-sm overflow-hidden
		transition-shadow hover:shadow-lg hover:scale-[1.02]
		focus-visible:ring-2 focus-visible:ring-primary focus-visible:outline-none
		{cursor: pointer}"
	role="article"
	aria-label="Ver receta: {recipe.title}"
	on:click={onClick}
	on:keydown={(e) => e.key === 'Enter' && onClick()}
	tabindex="0"
>
	<!-- Imagen -->
	<div class="aspect-[4/3] w-full overflow-hidden bg-muted relative">
		<img
			src={recipe.image_url || `https://placehold.co/400x400/${recipe.category?.color?.slice(1) || 'E8E4DF'}/${recipe.category?.color?.slice(1) || '6B6762'}?text={encodeURIComponent(recipe.slug)}`}
			alt="Receta: {recipe.title}"
			class="w-full h-full object-cover transition-transform group-hover:scale-105"
			loading="lazy"
		/>
		<!-- Badge Categoría -->
		{#if recipe.category}
			<CategoryBadge category={recipe.category} class="absolute top-2 left-2 z-10" />
		{/if}
	</div>

	<!-- Contenido -->
	<div class="flex-1 flex flex-col p-4 space-y-3 min-h-0">
		<!-- Tags -->
		{#if recipe.tags && recipe.tags.length > 0}
			<div class="flex flex-wrap gap-1.5" aria-label="Etiquetas">
				{#each recipe.tags.slice(0, 2) as tag}
					<span class="badge bg-muted text-muted-foreground px-2 py-0.5 rounded-full text-xs">{tag.name}</span>
				{/each}
				{#if recipe.tags.length > 2}
					<span class="badge variant="outline" text-muted-foreground px-2 py-0.5 rounded-full text-xs">+{recipe.tags.length - 2}</span>
				{/if}
			</div>
		{/if}

		<!-- Título -->
		<h3 class="font-semibold text-lg line-clamp-2 group-hover:text-primary transition-colors">
			{recipe.title}
		</h3>

		<!-- Meta: Rating + Contadores + Autor -->
		<div class="flex items-center gap-3 text-sm text-muted-foreground flex-wrap">
			<RatingStars value={recipe.avg_rating} count={recipe.rating_count} size="sm" showCount />
			<span class="flex items-center gap-1">
				<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16a2 2 0 01-2 2H4a2 2 0 01-2-2V4a2 2 0 012-2h10a2 2 0 012 2v10.5" /></svg>
				{recipe.save_count.toLocaleString()}
			</span>
			<span class="flex items-center gap-1">
				<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 5.943 5.77 4 7.937 4h8.126c2.16 0 4.198 1.943 3.548 5.098" /></svg>
				{recipe.visit_count.toLocaleString()}
			</span>
			<AuthorAvatar author={{ id: recipe.author_id, display_name: recipe.author?.display_name || 'Autor', avatar_url: recipe.author?.avatar_url }} size="sm" />
		</div>
	</div>
</article>

<style>
	:global(.recipe-card) {
		@apply group relative flex flex-col h-full bg-card rounded-xl border border-border shadow-sm overflow-hidden transition-shadow hover:shadow-lg hover:scale-[1.02] focus-visible:ring-2 focus-visible:ring-primary focus-visible:outline-none;
	}
</style>