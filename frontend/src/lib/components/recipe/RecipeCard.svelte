<script lang="ts">
	import type { Recipe } from '$lib/types';
	import { Clock, Flame, Eye, Bookmark } from 'lucide-svelte';
	import CategoryBadge from '$components/recipe/CategoryBadge.svelte';
	import RatingStars from '$components/recipe/RatingStars.svelte';
	import AuthorAvatar from '$components/common/AuthorAvatar.svelte';

	export let recipe: Recipe;

	function formatNumber(num: number): string {
		if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
		if (num >= 1000) return (num / 1000).toFixed(1) + 'k';
		return String(num ?? 0);
	}
</script>

<article class="group">
	<a
		href={`/receta/${recipe.slug}`}
		class="card flex h-full flex-col overflow-hidden"
		aria-label={`Ver receta: ${recipe.title}`}
	>
		<!-- Image / placeholder -->
		<div class="relative aspect-[4/3] w-full overflow-hidden bg-muted">
			{#if recipe.image_url}
				<img
					src={recipe.image_url}
					alt={recipe.title}
					class="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
					loading="lazy"
				/>
			{:else}
				<div
					class="flex h-full w-full items-center justify-center text-4xl"
					style="background-color: {recipe.category?.color ?? '#F0EDE8'}22;"
					aria-hidden="true"
				>
					{recipe.category?.icon ?? '🍽️'}
				</div>
			{/if}
			{#if recipe.category}
				<CategoryBadge category={recipe.category} className="absolute left-2 top-2 z-10" />
			{/if}
		</div>

		<!-- Body -->
		<div class="flex flex-1 flex-col gap-3 p-4">
			<h3 class="line-clamp-2 text-base font-medium text-foreground transition-colors group-hover:text-primary md:text-lg">
				{recipe.title}
			</h3>

			{#if recipe.description}
				<p class="line-clamp-2 text-sm text-muted-foreground">{recipe.description}</p>
			{/if}

			<div class="mt-auto flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-muted-foreground">
				<RatingStars value={recipe.avg_rating} count={recipe.rating_count} size="sm" showCount />
				{#if recipe.prep_time_minutes}
					<span class="inline-flex items-center gap-1">
						<Clock class="h-4 w-4" aria-hidden="true" />{recipe.prep_time_minutes} min
					</span>
				{/if}
				<span class="inline-flex items-center gap-1">
					<Bookmark class="h-4 w-4" aria-hidden="true" />{formatNumber(recipe.save_count)}
				</span>
				<span class="inline-flex items-center gap-1">
					<Eye class="h-4 w-4" aria-hidden="true" />{formatNumber(recipe.visit_count)}
				</span>
			</div>

			{#if recipe.author}
				<div class="flex items-center gap-2 border-t border-border pt-3">
					<AuthorAvatar author={recipe.author} size="sm" />
					<span class="truncate text-xs text-muted-foreground">{recipe.author.display_name}</span>
				</div>
			{/if}
		</div>
	</a>
</article>
