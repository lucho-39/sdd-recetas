<script lang="ts">
	import { Card } from '$components/ui/Card.svelte';
	import { Button } from '$components/ui/Button.svelte';
	import { Users, BookOpen, List, BarChart, TrendingUp, AlertCircle } from 'lucide-svelte';
</script>

<div class="space-y-6">
	<!-- Header -->
	<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
		<div>
			<h1 class="text-3xl font-playfair font-medium text-foreground">Dashboard</h1>
			<p class="text-muted-foreground mt-1">Bienvenido al panel de administración</p>
		</div>
		<div class="flex gap-2">
			<Button variant="outline">Exportar CSV</Button>
			<Button>Actualizar</Button>
		</div>
	</div>

	<!-- Stats Cards -->
	<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
		<StatCard title="Usuarios activos (30d)" value="1,234" change="+12%" trend="up" icon={Users} />
		<StatCard title="Recetas publicadas" value="5,678" change="+8%" trend="up" icon={BookOpen} />
		<StatCard title="Ingredientes pendientes" value="42" change="-3" trend="down" icon={AlertCircle} variant="destructive" />
		<StatCard title="Rating promedio" value="4.7" change="+0.2" trend="up" icon={TrendingUp} />
	</div>

	<!-- Charts placeholder -->
	<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
		<Card class="p-6">
			<h3 class="text-lg font-semibold mb-4">Usuarios nuevos por semana</h3>
			<div class="h-64 flex items-center justify-center text-muted-foreground">
				[Gráfico de líneas - Usuarios nuevos/semana]
			</div>
		</Card>
		<Card class="p-6">
			<h3 class="text-lg font-semibold mb-4">Recetas publicadas por categoría</h3>
			<div class="h-64 flex items-center justify-center text-muted-foreground">
				[Gráfico de barras - Recetas por categoría]
			</div>
		</Card>
	</div>

	<!-- Recent activity -->
	<Card class="p-6">
		<h3 class="text-lg font-semibold mb-4">Actividad reciente</h3>
		<div class="space-y-3">
			<ActivityItem user="María García" action="publicó" target="Tortilla de Patatas" time="hace 10 min" />
			<ActivityItem user="Carlos López" action="calificó" target="Gazpacho Andaluz" rating={5} time="hace 25 min" />
			<ActivityItem user="Ana Martín" action="guardó" target="Bizcocho de Yogur" time="hace 1 hora" />
			<ActivityItem user="Pedro Ruiz" action="creó" target="Ensalada César" time="hace 3 horas" />
		</div>
	</Card>
</div>

<script lang="ts">
	interface StatCardProps {
		title: string;
		value: string;
		change: string;
		trend: 'up' | 'down';
		icon: any;
		variant?: 'default' | 'destructive';
	}
</script>

{#render statCard()}
{#snippet statCard({title, value, change, trend, icon: Icon, variant = 'default'})}
	<div class="card p-6 {variant === 'destructive' ? 'border-destructive/20' : ''}">
		<div class="flex items-center justify-between">
			<div>
				<p class="text-sm text-muted-foreground">{title}</p>
				<p class="text-3xl font-bold text-foreground mt-1">{value}</p>
			</div>
			<div class="flex items-center gap-1 text-sm {trend === 'up' ? 'text-success' : 'text-destructive'}">
				<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					{#if trend === 'up'}
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7 7v10" />
					{:else}
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 14l7 7m0 0l7-7m-7-7v-10" />
					{/if}
				</svg>
				{change}
			</div>
		</div>
	</div>
{/snippet}

<script>
	interface ActivityItemProps {
		user: string;
		action: string;
		target: string;
		rating?: number;
		time: string;
	}
</script>

{#render activityItem()}
{#snippet activityItem({user, action, target, rating, time})}
	<div class="flex items-center justify-between py-3 border-b border-border last:border-0">
		<div class="flex items-center gap-3">
			<div class="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary text-sm font-medium">
				{user.charAt(0)}
			</div>
			<div>
				<p class="text-sm font-medium">{user}</p>
				<p class="text-xs text-muted-foreground">{action} <span class="font-medium">{target}</span> {rating ? `· ⭐ ${rating}/5` : ''}</p>
			</div>
		</div>
		<time class="text-xs text-muted-foreground whitespace-nowrap">{time}</time>
	</div>
{/snippet}