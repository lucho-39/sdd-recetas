<script lang="ts">
	import { onMount } from 'svelte';
	import {
		IconUsers as Users,
		IconBookFilled as Recipes,
		IconListFilled as Ingredients,
		IconTagFilled as Tag,
		IconBookmarkFilled as Tags,
		IconStarFilled as Rating,
		IconEyeFilled as Visits
	} from '@tabler/icons-svelte';
	import { auth } from '$lib/stores/auth';

	let stats: Record<string, number> | null = null;
	let error = '';
	let loading = true;

	onMount(async () => {
		try {
			const res = await fetch('/api/admin/metrics/dashboard', {
				headers: { Authorization: `Bearer ${$auth.accessToken}` }
			});
			if (!res.ok) throw new Error(`API ${res.status}`);
			stats = await res.json();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Error al cargar métricas';
		} finally {
			loading = false;
		}
	});

	const cards = [
		{ key: 'users_total', label: 'Usuarios', icon: Users },
		{ key: 'users_active', label: 'Usuarios activos', icon: Users },
		{ key: 'recipes_total', label: 'Recetas', icon: Recipes },
		{ key: 'recipes_public', label: 'Recetas públicas', icon: Recipes },
		{ key: 'ingredients_total', label: 'Ingredientes', icon: Ingredients },
		{ key: 'ingredients_pending', label: 'Ingredientes pendientes', icon: Ingredients },
		{ key: 'categories_total', label: 'Categorías', icon: Tag },
		{ key: 'tags_total', label: 'Tags', icon: Tags },
		{ key: 'ratings_total', label: 'Calificaciones', icon: Rating },
		{ key: 'visits_total', label: 'Visitas', icon: Visits }
	];
</script>

<svelte:head>
	<title>Dashboard — Recetario Admin</title>
</svelte:head>

<div class="space-y-6">
	<div>
		<h1 class="font-playfair text-2xl font-medium text-foreground md:text-3xl">Dashboard</h1>
		<p class="mt-1 text-muted-foreground">Estadísticas generales de la aplicación</p>
	</div>

	{#if error}
		<div class="rounded-md border border-destructive/30 bg-destructive/10 p-3 text-sm text-destructive" role="alert">{error}</div>
	{/if}

	<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
		{#each cards as card (card.key)}
			<div class="card p-5">
				<div class="flex items-center justify-between">
					<p class="text-sm text-muted-foreground">{card.label}</p>
					<card.icon class="h-5 w-5 text-muted-foreground" aria-hidden="true" />
				</div>
				<p class="mt-2 text-3xl font-semibold text-foreground">
					{loading ? '…' : (stats?.[card.key] ?? 0)}
				</p>
			</div>
		{/each}
	</div>
</div>
