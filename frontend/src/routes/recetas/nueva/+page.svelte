<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { auth } from '$lib/stores/auth';
	import RecipeForm from '$components/recipe/RecipeForm.svelte';

	let ready = false;

	onMount(async () => {
		if (!$auth.isAuthenticated && !$auth.loading) await auth.init();
		if (!$auth.isAuthenticated) {
			await goto('/login?returnTo=/recetas/nueva');
			return;
		}
		ready = true;
	});
</script>

<svelte:head><title>Nueva receta — Recetario IA</title></svelte:head>

<div class="container py-8">
	<h1 class="mb-6 font-playfair text-2xl font-medium text-foreground md:text-3xl">Nueva receta</h1>
	{#if ready}<RecipeForm />{/if}
</div>
