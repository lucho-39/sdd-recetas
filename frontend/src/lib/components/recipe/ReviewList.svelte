<script lang="ts">
	import { onMount } from 'svelte';
	import RatingStars from '$components/recipe/RatingStars.svelte';
	import AuthorAvatar from '$components/common/AuthorAvatar.svelte';
	import { formatDate } from '$lib/utils';

	export let recipeId: string;

	type Review = {
		id: string;
		score: number;
		review_text?: string | null;
		created_at: string;
		user: { display_name: string; avatar_url?: string | null };
	};

	let reviews: Review[] = [];
	let page = 1;
	let total = 0;
	let loading = true;
	let loadingMore = false;

	$: hasMore = reviews.length < total;

	async function fetchPage(target: number, append: boolean) {
		if (append) loadingMore = true;
		else loading = true;
		try {
			const res = await fetch(`/api/v1/ratings/${recipeId}?page=${target}&limit=10`);
			if (res.ok) {
				const data = await res.json();
				reviews = append ? [...reviews, ...data.ratings] : data.ratings;
				total = data.total;
				page = target;
			}
		} finally {
			loading = false;
			loadingMore = false;
		}
	}

	onMount(() => fetchPage(1, false));
</script>

<section class="mt-10" aria-labelledby="reviews-heading">
	<h2 id="reviews-heading" class="mb-4 text-xl font-medium text-foreground">
		Reseñas <span class="text-muted-foreground">({total})</span>
	</h2>

	{#if loading}
		<p class="text-sm text-muted-foreground">Cargando reseñas…</p>
	{:else if reviews.length === 0}
		<p class="text-sm text-muted-foreground">Todavía no hay reseñas. ¡Sé el primero en calificar!</p>
	{:else}
		<ul class="space-y-4">
			{#each reviews as review (review.id)}
				<li class="rounded-lg border border-border p-4">
					<div class="mb-2 flex items-center gap-3">
						<AuthorAvatar
							author={{ id: review.id, display_name: review.user.display_name, avatar_url: review.user.avatar_url }}
							size="sm"
						/>
						<div class="min-w-0 flex-1">
							<p class="truncate text-sm font-medium text-foreground">{review.user.display_name}</p>
							<p class="text-xs text-muted-foreground">{formatDate(review.created_at)}</p>
						</div>
						<RatingStars value={review.score} size="xs" />
					</div>
					{#if review.review_text}
						<p class="text-sm text-foreground">{review.review_text}</p>
					{/if}
				</li>
			{/each}
		</ul>

		{#if hasMore}
			<div class="mt-4 flex justify-center">
				<button type="button" class="btn btn-outline btn-sm" on:click={() => fetchPage(page + 1, true)} disabled={loadingMore}>
					{loadingMore ? 'Cargando…' : 'Cargar más reseñas'}
				</button>
			</div>
		{/if}
	{/if}
</section>
