<script lang="ts">
	import { onMount } from 'svelte';
	import { adminFetch } from '$lib/api';
	import BarChart from '$lib/components/BarChart.svelte';

	type Series = { label: string; count: number };
	type TopRecipe = {
		slug: string;
		title: string;
		visit_count: number;
		avg_rating: number;
		rating_count: number;
	};
	type Overview = {
		top_recipes: TopRecipe[];
		categories: { name: string; count: number }[];
		ratings_distribution: Record<string, number>;
	};

	let overview: Overview | null = null;
	let usersMonth: Series[] = [];
	let usersWeek: Series[] = [];
	let loading = true;
	let error = '';

	$: categoryData =
		overview?.categories.map((c) => ({ label: c.name, count: c.count })) ?? [];
	$: ratingData = [5, 4, 3, 2, 1].map((score) => ({
		label: `${score}★`,
		count: overview?.ratings_distribution?.[String(score)] ?? 0
	}));

	onMount(async () => {
		try {
			const [overviewData, month, week] = await Promise.all([
				adminFetch<Overview>('/metrics/overview'),
				adminFetch<{ series: Series[] }>('/metrics/users-series?interval=month&periods=12'),
				adminFetch<{ series: Series[] }>('/metrics/users-series?interval=week&periods=8')
			]);
			overview = overviewData;
			usersMonth = month.series;
			usersWeek = week.series;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Error al cargar métricas';
		} finally {
			loading = false;
		}
	});
</script>

<svelte:head><title>Métricas — Recetario Admin</title></svelte:head>

<div class="space-y-6">
	<div>
		<h1 class="font-playfair text-2xl font-medium text-foreground md:text-3xl">Métricas</h1>
		<p class="mt-1 text-muted-foreground">Crecimiento de usuarios, contenido popular y calificaciones</p>
	</div>

	{#if error}
		<div class="rounded-md border border-destructive/30 bg-destructive/10 p-3 text-sm text-destructive" role="alert">{error}</div>
	{/if}

	{#if loading}
		<p class="text-muted-foreground">Cargando métricas…</p>
	{:else}
		<div class="grid grid-cols-1 gap-4 xl:grid-cols-2">
			<BarChart title="Usuarios registrados por mes" data={usersMonth} />
			<BarChart title="Usuarios registrados por semana" data={usersWeek} />
			<BarChart title="Recetas por categoría" data={categoryData} />
			<BarChart title="Distribución de calificaciones" data={ratingData} />
		</div>

		<div class="card p-4">
			<h3 class="mb-4 text-sm font-medium text-foreground">Recetas más visitadas</h3>
			{#if !overview?.top_recipes.length}
				<p class="py-6 text-center text-sm text-muted-foreground">Sin datos</p>
			{:else}
				<table class="w-full text-sm">
					<thead>
						<tr class="border-b border-border text-left text-xs uppercase text-muted-foreground">
							<th class="py-2">Receta</th>
							<th class="py-2 text-right">Visitas</th>
							<th class="py-2 text-right">Calificación</th>
						</tr>
					</thead>
					<tbody>
						{#each overview.top_recipes as item (item.slug)}
							<tr class="border-b border-border/60">
								<td class="py-2">{item.title}</td>
								<td class="py-2 text-right tabular-nums">{item.visit_count}</td>
								<td class="py-2 text-right tabular-nums">
									{item.avg_rating.toFixed(2)} ({item.rating_count})
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			{/if}
		</div>
	{/if}
</div>
