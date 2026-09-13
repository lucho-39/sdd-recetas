<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { auth } from '$lib/stores/auth';
	import RecipeForm from '$components/recipe/RecipeForm.svelte';

	export let data;

	let ready = false;

	onMount(async () => {
		if (!$auth.isAuthenticated && !$auth.loading) await auth.init();
		if (!$auth.isAuthenticated) {
			await goto(`/login?returnTo=/recetas/${data.slug}/editar`);
			return;
		}
		if ($auth.user && data.recipe.author?.id !== $auth.user.id) {
			await goto(`/receta/${data.slug}`);
			return;
		}
		ready = true;
	});
</script>

<svelte:head><title>Editar {data.recipe.title} — Recetario IA</title></svelte:head>

<div class="container py-8">
	<h1 class="mb-6 font-playfair text-2xl font-medium text-foreground md:text-3xl">Editar receta</h1>
	{#if ready}
		<RecipeForm initial={data.recipe} slug={data.slug} />
	{/if}
</div>
