<script lang="ts">
	import { IconClockFilled as Clock, IconUsers as Users, IconFlame, IconShare, IconPlayerPlayFilled as Play, IconEyeFilled as Eye } from '@tabler/icons-svelte';
	import CategoryBadge from '$components/recipe/CategoryBadge.svelte';
	import RatingStars from '$components/recipe/RatingStars.svelte';
	import AuthorAvatar from '$components/common/AuthorAvatar.svelte';

	export let data;
	const recipe = data.recipe;

	function formatMinutes(min?: number | null): string {
		if (!min) return '—';
		if (min < 60) return `${min} min`;
		const h = Math.floor(min / 60);
		const m = min % 60;
		return m ? `${h} h ${m} min` : `${h} h`;
	}

	async function share() {
		const url = typeof window !== 'undefined' ? window.location.href : '';
		if (typeof navigator !== 'undefined' && navigator.share) {
			await navigator.share({ title: recipe.title, url }).catch(() => {});
		} else if (typeof navigator !== 'undefined' && navigator.clipboard) {
			await navigator.clipboard.writeText(url).catch(() => {});
		}
	}
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
			<a href="/?category={recipe.category.slug}" class="hover:text-foreground">{recipe.category.name}</a>
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
			<RatingStars value={recipe.avg_rating} count={recipe.rating_count} size="sm" showCount />
		</div>

		<div class="grid gap-8 md:grid-cols-2">
			<!-- Ingredients -->
			<section aria-labelledby="ingredients-heading">
				<h2 id="ingredients-heading" class="mb-3 text-xl font-medium text-foreground">Ingredientes</h2>
				{#if recipe.ingredients && recipe.ingredients.length > 0}
					<ul class="space-y-2">
						{#each recipe.ingredients as ing}
							<li class="flex items-start gap-2 border-b border-border pb-2 text-sm">
								<span aria-hidden="true">•</span>
								<span class="font-medium text-foreground">{ing.amount} {ing.unit}</span>
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
	</article>
</div>
