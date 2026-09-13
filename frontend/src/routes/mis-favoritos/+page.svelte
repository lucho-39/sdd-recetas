<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { IconTrashFilled as RemoveFav } from '@tabler/icons-svelte';
	import { auth } from '$lib/stores/auth';
	import RecipeCard from '$components/recipe/RecipeCard.svelte';

	type Favorite = {
		recipe_id: string;
		collection_name?: string | null;
		recipe: any | null;
	};

	let favorites: Favorite[] = [];
	let loading = true;
	let error = '';

	async function load() {
		loading = true;
		error = '';
		try {
			const res = await fetch('/api/v1/favorites', {
				headers: { Authorization: `Bearer ${$auth.accessToken}` }
			});
			if (!res.ok) throw new Error(`API ${res.status}`);
			favorites = (await res.json()).filter((f: Favorite) => f.recipe);
		} catch (err) {
			error = err instanceof Error ? err.message : 'Error';
		} finally {
			loading = false;
		}
	}

	async function remove(fav: Favorite) {
		if (!confirm(`¿Quitar "${fav.recipe?.title}" de favoritos?`)) return;
		await fetch(`/api/v1/favorites/${fav.recipe_id}`, {
			method: 'DELETE',
			headers: { Authorization: `Bearer ${$auth.accessToken}` }
		});
		await load();
	}

	onMount(async () => {
		if (!$auth.isAuthenticated) await auth.init();
		if (!$auth.isAuthenticated) {
			await goto('/login?returnTo=/mis-favoritos');
			return;
		}
		await load();
	});
</script>

<svelte:head><title>Mis favoritos — Recetario IA</title></svelte:head>

<div class="container py-8">
	<h1 class="mb-6 font-playfair text-2xl font-medium text-foreground md:text-3xl">Mis favoritos</h1>

	{#if error}<p class="mb-4 text-sm text-destructive" role="alert">{error}</p>{/if}

	{#if loading}
		<p class="text-muted-foreground">Cargando…</p>
	{:else if favorites.length === 0}
		<div class="py-12 text-center">
			<p class="text-muted-foreground">Todavía no guardaste recetas.</p>
			<a href="/" class="btn btn-primary btn-sm mt-4">Explorar recetas</a>
		</div>
	{:else}
		<div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
			{#each favorites as fav (fav.recipe_id)}
				<div class="flex flex-col gap-2">
					<RecipeCard recipe={fav.recipe} />
					<button type="button" class="btn btn-ghost btn-sm self-start text-destructive" on:click={() => remove(fav)}>
						<RemoveFav class="h-4 w-4" aria-hidden="true" /> Quitar de favoritos
					</button>
				</div>
			{/each}
		</div>
	{/if}
</div>
