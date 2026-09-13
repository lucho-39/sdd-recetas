<script lang="ts">
	import {
		IconUsers as Users,
		IconBookFilled as BookOpen,
		IconListFilled as List,
		IconStarFilled as Star,
		IconTrendingUp as TrendingUp
	} from '@tabler/icons-svelte';

	const stats = [
		{ label: 'Usuarios activos (30d)', value: '—', icon: Users },
		{ label: 'Recetas publicadas', value: '—', icon: BookOpen },
		{ label: 'Ingredientes pendientes', value: '—', icon: List },
		{ label: 'Rating promedio', value: '—', icon: Star }
	];

	const activity = [
		{ user: 'María García', action: 'publicó', target: 'Torta de chocolate', time: 'hace 10 min' },
		{ user: 'Carlos López', action: 'calificó', target: 'Gazpacho andaluz', time: 'hace 25 min' },
		{ user: 'Ana Martín', action: 'guardó', target: 'Bizcocho de yogur', time: 'hace 1 hora' }
	];
</script>

<svelte:head>
	<title>Dashboard — Recetario Admin</title>
</svelte:head>

<div class="space-y-6">
	<div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
		<div>
			<h1 class="font-playfair text-2xl font-medium text-foreground md:text-3xl">Dashboard</h1>
			<p class="mt-1 text-muted-foreground">Resumen del panel de administración</p>
		</div>
		<button type="button" class="btn btn-outline btn-sm self-start">Actualizar</button>
	</div>

	<div
		class="flex items-start gap-2 rounded-md border border-warning/30 bg-warning/10 p-3 text-sm text-foreground"
		role="status"
	>
		<TrendingUp class="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
		<p>Los endpoints de administración (<code>/api/admin/*</code>) están pendientes; estas métricas son de ejemplo.</p>
	</div>

	<!-- Stat cards -->
	<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
		{#each stats as stat (stat.label)}
			<div class="card p-5">
				<div class="flex items-center justify-between">
					<p class="text-sm text-muted-foreground">{stat.label}</p>
					<stat.icon class="h-5 w-5 text-muted-foreground" aria-hidden="true" />
				</div>
				<p class="mt-2 text-3xl font-semibold text-foreground">{stat.value}</p>
			</div>
		{/each}
	</div>

	<!-- Recent activity -->
	<div class="card p-6">
		<h2 class="mb-4 text-lg font-medium text-foreground">Actividad reciente</h2>
		<ul class="divide-y divide-border">
			{#each activity as item (item.user + item.target)}
				<li class="flex items-center justify-between gap-4 py-3">
					<div class="flex items-center gap-3">
						<span class="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-sm font-medium text-primary">
							{item.user.charAt(0)}
						</span>
						<div>
							<p class="text-sm font-medium text-foreground">{item.user}</p>
							<p class="text-xs text-muted-foreground">{item.action} {item.target}</p>
						</div>
					</div>
					<time class="whitespace-nowrap text-xs text-muted-foreground">{item.time}</time>
				</li>
			{/each}
		</ul>
	</div>
</div>
