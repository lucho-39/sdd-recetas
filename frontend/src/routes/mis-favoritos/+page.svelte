<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import {
		IconTrashFilled as RemoveFav,
		IconFolderFilled as Folder,
		IconEdit as Edit
	} from '@tabler/icons-svelte';
	import { auth } from '$lib/stores/auth';
	import RecipeCard from '$components/recipe/RecipeCard.svelte';

	type Favorite = {
		recipe_id: string;
		collection_name?: string | null;
		recipe: any | null;
	};
	type Collection = { name: string | null; count: number };

	let favorites: Favorite[] = [];
	let collections: Collection[] = [];
	let selected: string | null = null;
	let loading = true;
	let error = '';

	$: namedCollections = collections.filter(
		(c): c is { name: string; count: number } => c.name !== null
	);
	$: visible = selected === null ? favorites : favorites.filter((f) => f.collection_name === selected);
	$: totalCount = collections.find((c) => c.name === null)?.count ?? favorites.length;

	async function load() {
		loading = true;
		error = '';
		try {
			const [favRes, colRes] = await Promise.all([
				fetch('/api/v1/favorites', {
					headers: { Authorization: `Bearer ${$auth.accessToken}` }
				}),
				fetch('/api/v1/favorites/collections', {
					headers: { Authorization: `Bearer ${$auth.accessToken}` }
				})
			]);
			if (!favRes.ok) throw new Error(`API ${favRes.status}`);
			favorites = (await favRes.json()).filter((f: Favorite) => f.recipe);
			collections = colRes.ok ? await colRes.json() : [];
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

	async function patchFavorite(recipeId: string, collectionName: string | null) {
		await fetch(`/api/v1/favorites/${recipeId}`, {
			method: 'PATCH',
			headers: {
				'Content-Type': 'application/json',
				Authorization: `Bearer ${$auth.accessToken}`
			},
			body: JSON.stringify({ collection_name: collectionName })
		});
		await load();
	}

	function onMove(fav: Favorite, value: string) {
		if (value === '__new__') {
			const name = prompt('Nombre de la nueva colección:');
			if (!name) return;
			patchFavorite(fav.recipe_id, name.trim());
			return;
		}
		patchFavorite(fav.recipe_id, value || null);
	}

	async function renameCollection() {
		if (selected === null) return;
		const name = prompt('Nuevo nombre de la colección:', selected);
		if (!name || name === selected) return;
		const res = await fetch(`/api/v1/favorites/collections/${encodeURIComponent(selected)}`, {
			method: 'PATCH',
			headers: {
				'Content-Type': 'application/json',
				Authorization: `Bearer ${$auth.accessToken}`
			},
			body: JSON.stringify({ new_name: name.trim() })
		});
		if (res.ok) selected = name.trim();
		await load();
	}

	async function deleteCollection() {
		if (selected === null) return;
		if (!confirm(`¿Borrar la colección "${selected}"? Las recetas vuelven a la lista general.`)) return;
		await fetch(`/api/v1/favorites/collections/${encodeURIComponent(selected)}`, {
			method: 'DELETE',
			headers: { Authorization: `Bearer ${$auth.accessToken}` }
		});
		selected = null;
		await load();
	}

	onMount(async () => {
		if (!$auth.isAuthenticated && !$auth.loading) await auth.init();
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
	{:else}
		<div class="grid gap-8 lg:grid-cols-[220px_1fr]">
			<!-- Collections sidebar -->
			<aside aria-label="Colecciones">
				<ul class="space-y-1">
					<li>
						<button
							type="button"
							class="flex w-full items-center justify-between rounded-md px-3 py-2 text-sm {selected === null ? 'bg-primary/10 font-medium text-primary' : 'text-foreground hover:bg-muted'}"
							on:click={() => (selected = null)}
						>
							<span class="inline-flex items-center gap-2"><Folder class="h-4 w-4" aria-hidden="true" /> Todas</span>
							<span class="text-xs text-muted-foreground">{totalCount}</span>
						</button>
					</li>
					{#each namedCollections as col}
						<li>
							<button
								type="button"
								class="flex w-full items-center justify-between rounded-md px-3 py-2 text-sm {selected === col.name ? 'bg-primary/10 font-medium text-primary' : 'text-foreground hover:bg-muted'}"
								on:click={() => (selected = col.name)}
							>
								<span class="truncate">{col.name}</span>
								<span class="text-xs text-muted-foreground">{col.count}</span>
							</button>
						</li>
					{/each}
				</ul>

				{#if selected !== null}
					<div class="mt-3 flex gap-1 border-t border-border pt-3">
						<button type="button" class="btn btn-ghost btn-sm" on:click={renameCollection}>
							<Edit class="h-4 w-4" aria-hidden="true" /> Renombrar
						</button>
						<button type="button" class="btn btn-ghost btn-sm text-destructive" on:click={deleteCollection}>
							Borrar
						</button>
					</div>
				{/if}
			</aside>

			<!-- Favorites -->
			<main>
				{#if visible.length === 0}
					<div class="py-12 text-center">
						<p class="text-muted-foreground">
							{selected === null ? 'Todavía no guardaste recetas.' : 'Esta colección está vacía.'}
						</p>
						<a href="/buscar" class="btn btn-primary btn-sm mt-4">Explorar recetas</a>
					</div>
				{:else}
					<div class="grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-3">
						{#each visible as fav (fav.recipe_id)}
							<div class="flex flex-col gap-2">
								<RecipeCard recipe={fav.recipe} />
								<div class="flex items-center gap-2">
									<select
										class="input-base py-1.5 text-xs"
										value={fav.collection_name ?? ''}
										on:change={(e) => onMove(fav, e.currentTarget.value)}
										aria-label="Mover a colección"
									>
										<option value="">Sin colección</option>
										{#each namedCollections as col}
											<option value={col.name}>{col.name}</option>
										{/each}
										<option value="__new__">＋ Nueva colección…</option>
									</select>
									<button
										type="button"
										class="btn btn-ghost btn-sm text-destructive"
										on:click={() => remove(fav)}
										title="Quitar de favoritos"
									>
										<RemoveFav class="h-4 w-4" aria-hidden="true" />
									</button>
								</div>
							</div>
						{/each}
					</div>
				{/if}
			</main>
		</div>
	{/if}
</div>
