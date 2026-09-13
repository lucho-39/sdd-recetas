<script lang="ts">
	import RecipeGrid from '$components/recipe/RecipeGrid.svelte';
	import AuthorAvatar from '$components/common/AuthorAvatar.svelte';

	export let data;

	const memberSince = new Intl.DateTimeFormat('es-AR', {
		year: 'numeric',
		month: 'long'
	}).format(new Date(data.profile.created_at));

	const profile = data.profile;
</script>

<svelte:head>
	<title>{profile.display_name} — Recetario IA</title>
</svelte:head>

<div class="container py-8">
	<header class="mb-8 flex flex-col items-center gap-4 text-center sm:flex-row sm:text-left">
		<AuthorAvatar
			author={{ id: profile.id, display_name: profile.display_name, avatar_url: profile.avatar_url }}
			size="lg"
		/>
		<div>
			<h1 class="font-playfair text-2xl font-medium text-foreground md:text-3xl">
				{profile.display_name}
			</h1>
			<p class="mt-1 text-sm text-muted-foreground">
				Miembro desde {memberSince} · {profile.recipe_count}
				{profile.recipe_count === 1 ? 'receta publicada' : 'recetas publicadas'}
			</p>
		</div>
	</header>

	<section aria-labelledby="author-recipes-heading">
		<h2 id="author-recipes-heading" class="mb-6 text-xl font-medium text-foreground">
			Recetas publicadas
		</h2>
		<RecipeGrid
			recipes={data.recipes}
			loading={false}
			loadingMore={false}
			hasMore={false}
			emptyVariant="recipes"
			onLoadMore={() => {}}
		/>
	</section>
</div>
