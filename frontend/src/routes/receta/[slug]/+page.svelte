<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import {
		IconClockFilled as Clock,
		IconUsers as Users,
		IconFlame,
		IconShare,
		IconPlayerPlayFilled as Play,
		IconEyeFilled as Eye,
		IconHeartFilled as HeartFilled,
		IconHeart as Heart
	} from '@tabler/icons-svelte';
	import CategoryBadge from '$components/recipe/CategoryBadge.svelte';
	import RatingStars from '$components/recipe/RatingStars.svelte';
	import AuthorAvatar from '$components/common/AuthorAvatar.svelte';
	import ReviewList from '$components/recipe/ReviewList.svelte';
	import { auth } from '$lib/stores/auth';

	export let data;
	const recipe = data.recipe;

	let isFavorited = false;
	let favBusy = false;
	let avgRating = recipe.avg_rating ?? 0;
	let ratingCount = recipe.rating_count ?? 0;
	let rateBusy = false;

	const starPath =
		'M12 2.5l2.95 5.98 6.6.96-4.78 4.66 1.13 6.57L12 17.77l-5.9 3.9 1.13-6.57L2.45 9.44l6.6-.96L12 2.5z';

	function formatMinutes(min?: number | null): string {
		if (!min) return '—';
		if (min < 60) return `${min} min`;
		const h = Math.floor(min / 60);
		const m = min % 60;
		return m ? `${h} h ${m} min` : `${h} h`;
	}

	async function ensureAuth(): Promise<boolean> {
		if (!$auth.isAuthenticated && !$auth.loading) await auth.init();
		if (!$auth.isAuthenticated) {
			await goto(`/login?returnTo=/receta/${recipe.slug}`);
			return false;
		}
		return true;
	}

	async function share() {
		const url = typeof window !== 'undefined' ? window.location.href : '';
		if (typeof navigator !== 'undefined' && navigator.share) {
			await navigator.share({ title: recipe.title, url }).catch(() => {});
		} else if (typeof navigator !== 'undefined' && navigator.clipboard) {
			await navigator.clipboard.writeText(url).catch(() => {});
		}
	}

	async function toggleFavorite() {
		if (!(await ensureAuth())) return;
		favBusy = true;
		const method = isFavorited ? 'DELETE' : 'POST';
		const res = await fetch(`/api/v1/favorites/${recipe.id}`, {
			method,
			headers: { Authorization: `Bearer ${$auth.accessToken}` }
		});
		if (res.ok) isFavorited = !isFavorited;
		favBusy = false;
	}

	async function rate(score: number) {
		if (!(await ensureAuth())) return;
		rateBusy = true;
		const res = await fetch(`/api/v1/ratings/${recipe.id}?score=${score}`, {
			method: 'POST',
			headers: { Authorization: `Bearer ${$auth.accessToken}` }
		});
		if (res.ok) {
			const body = await res.json();
			avgRating = body.avg_rating;
			ratingCount = body.rating_count;
		}
		rateBusy = false;
	}

	onMount(async () => {
		if (!$auth.isAuthenticated && !$auth.loading) await auth.init();
		if ($auth.isAuthenticated) {
			const res = await fetch('/api/v1/favorites', {
				headers: { Authorization: `Bearer ${$auth.accessToken}` }
			});
			if (res.ok) {
				const favs = await res.json();
				isFavorited = favs.some((f: { recipe_id: string }) => f.recipe_id === recipe.id);
			}
		}
	});
</script>

<svelte:head>
	<title>{recipe.title} — Recetario IA</title>
	<meta name="description" content={recipe.description ?? recipe.title} />
</svelte:head>

<div class="container py-6 md:py-8">
	<!-- Breadcrumb -->
	<nav class="mb-4 text-sm text-muted-foreground" aria-label="Ruta de navegación">
		<a href="/" class="hover:text-foreground">Inicio</a>
		{#if recipe.category}
			<span aria-hidden="true"> / </span>
			<a href="/buscar?category={recipe.category.slug}" class="hover:text-foreground">{recipe.category.name}</a>
		{/if}
		<span aria-hidden="true"> / </span>
		<span class="text-foreground">{recipe.title}</span>
	</nav>

	<article class="mx-auto max-w-4xl">
		<!-- Hero image -->
		<div class="relative mb-6 aspect-[16/9] w-full overflow-hidden rounded-lg bg-muted">
			{#if recipe.image_url}
				<img src={recipe.image_url} alt={recipe.title} class="h-full w-full object-cover" />
			{:else}
				<div class="flex h-full w-full items-center justify-center text-6xl" style="background-color: {recipe.category?.color ?? '#F0EDE8'}22;" aria-hidden="true">
					{recipe.category?.icon ?? '🍽️'}
				</div>
			{/if}
			{#if recipe.category}
				<div class="absolute left-3 top-3">
					<CategoryBadge category={recipe.category} />
				</div>
			{/if}
		</div>

		<!-- Title + actions -->
		<div class="mb-4 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
			<h1 class="font-playfair text-3xl font-medium text-foreground md:text-4xl">{recipe.title}</h1>
			<div class="flex shrink-0 gap-2">
				<button
					type="button"
					class="btn btn-outline btn-sm"
					on:click={toggleFavorite}
					disabled={favBusy}
					aria-pressed={isFavorited}
					title={isFavorited ? 'Quitar de favoritos' : 'Guardar en favoritos'}
				>
					{#if isFavorited}<HeartFilled class="h-4 w-4 text-primary" aria-hidden="true" />{:else}<Heart class="h-4 w-4" aria-hidden="true" />{/if}
					{isFavorited ? 'Guardada' : 'Guardar'}
				</button>
				<button type="button" class="btn btn-outline btn-sm" on:click={share}>
					<IconShare class="h-4 w-4" aria-hidden="true" /> Compartir
				</button>
				<a href="/cooking/{recipe.slug}" class="btn btn-primary btn-sm">
					<Play class="h-4 w-4" aria-hidden="true" /> Cocinar
				</a>
			</div>
		</div>

		{#if recipe.description}
			<p class="mb-4 text-muted-foreground">{recipe.description}</p>
		{/if}

		<!-- Meta -->
		<div class="mb-6 flex flex-wrap items-center gap-x-5 gap-y-2 text-sm text-muted-foreground">
			<a href={`/usuario/${recipe.author?.id}`} class="inline-flex items-center gap-2 font-medium text-foreground hover:text-primary">
				<AuthorAvatar author={{ id: recipe.author?.id, display_name: recipe.author?.display_name ?? 'Autor', avatar_url: recipe.author?.avatar_url }} size="xs" />
				{recipe.author?.display_name ?? 'Autor'}
			</a>
			<span class="inline-flex items-center gap-1"><Clock class="h-4 w-4" aria-hidden="true" />{formatMinutes(recipe.prep_time_minutes)}</span>
			{#if recipe.servings}
				<span class="inline-flex items-center gap-1"><Users class="h-4 w-4" aria-hidden="true" />{recipe.servings} porciones</span>
			{/if}
			{#if recipe.difficulty}
				<span class="inline-flex items-center gap-1"><IconFlame class="h-4 w-4" aria-hidden="true" />{recipe.difficulty}</span>
			{/if}
			<span class="inline-flex items-center gap-1"><Eye class="h-4 w-4" aria-hidden="true" />{recipe.visit_count}</span>
			<RatingStars value={avgRating} count={ratingCount} size="sm" showCount />
		</div>

		<!-- Rating -->
		<section class="mb-6 rounded-lg border border-border p-4" aria-labelledby="rating-heading">
			<h2 id="rating-heading" class="mb-3 text-sm font-medium text-foreground">Calificá esta receta</h2>
			<div class="flex items-center gap-1" role="radiogroup" aria-label="Puntaje de 1 a 5 estrellas">
				{#each [1, 2, 3, 4, 5] as score}
					<button
						type="button"
						class="p-1 text-rating transition-transform hover:scale-110 disabled:opacity-50"
						on:click={() => rate(score)}
						disabled={rateBusy}
						aria-label={`${score} estrella${score === 1 ? '' : 's'}`}
					>
						<svg class="h-7 w-7" viewBox="0 0 24 24" fill={score <= Math.round(avgRating) ? 'currentColor' : 'none'} stroke="currentColor" stroke-width="1.5" aria-hidden="true">
							<path d={starPath} />
						</svg>
					</button>
				{/each}
				<span class="ml-2 text-sm text-muted-foreground">
					{avgRating.toFixed(1)} / 5 ({ratingCount} reseña{ratingCount === 1 ? '' : 's'})
				</span>
			</div>
		</section>

		{#if recipe.tags && recipe.tags.length > 0}
			<div class="mb-6 flex flex-wrap gap-2" aria-label="Etiquetas">
				{#each recipe.tags as tag}
					<a href="/buscar?tag={tag.slug}" class="badge bg-muted text-muted-foreground hover:bg-accent">#{tag.name}</a>
				{/each}
			</div>
		{/if}

		<div class="grid gap-8 md:grid-cols-2">
			<!-- Ingredients -->
			<section aria-labelledby="ingredients-heading">
				<h2 id="ingredients-heading" class="mb-3 text-xl font-medium text-foreground">Ingredientes</h2>
				{#if recipe.ingredients && recipe.ingredients.length > 0}
					<ul class="space-y-2">
						{#each recipe.ingredients as ing}
							<li class="flex items-start gap-2 border-b border-border pb-2 text-sm">
								<span aria-hidden="true">•</span>
								<span class="text-foreground">
									{#if ing.amount}<span class="font-medium">{ing.amount} {ing.unit}</span>{/if}
									<span class="ml-1">{ing.name ?? 'Ingrediente'}</span>
								</span>
								{#if ing.notes}<span class="text-muted-foreground">— {ing.notes}</span>{/if}
							</li>
						{/each}
					</ul>
				{:else}
					<p class="text-sm text-muted-foreground">Esta receta todavía no tiene ingredientes cargados.</p>
				{/if}
			</section>

			<!-- Instructions -->
			<section aria-labelledby="instructions-heading">
				<h2 id="instructions-heading" class="mb-3 text-xl font-medium text-foreground">Preparación</h2>
				<div class="space-y-3 text-sm leading-relaxed text-foreground">
					{#each recipe.instructions.split('\n').filter((p: string) => p.trim()) as paragraph, i}
						<div class="flex gap-3">
							<span class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary/10 text-xs font-medium text-primary">{i + 1}</span>
							<p>{paragraph}</p>
						</div>
					{/each}
				</div>
			</section>
		</div>

		<ReviewList recipeId={recipe.id} />
	</article>
</div>
