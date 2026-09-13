<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import {
		IconMenu2 as Menu,
		IconX as X,
		IconLayoutDashboardFilled as LayoutDashboard,
		IconTagFilled as Tag,
		IconUsers as Users,
		IconBookFilled as BookOpen,
		IconListFilled as List,
		IconChartBar as BarChart3,
		IconSettingsFilled as Settings
	} from '@tabler/icons-svelte';
	import { auth } from '$lib/stores/auth';

	let sidebarOpen = false;

	const nav = [
		{ href: '/', label: 'Dashboard', icon: LayoutDashboard },
		{ href: '/admin/categorias', label: 'Categorías', icon: Tag },
		{ href: '/admin/usuarios', label: 'Usuarios', icon: Users },
		{ href: '/admin/recetas', label: 'Recetas', icon: BookOpen },
		{ href: '/admin/ingredientes', label: 'Ingredientes', icon: List },
		{ href: '/admin/metricas', label: 'Métricas', icon: BarChart3 },
		{ href: '/admin/config', label: 'Configuración', icon: Settings }
	];

	onMount(() => {
		auth.init();
	});
</script>

<div class="flex min-h-screen bg-background text-foreground">
	<!-- Sidebar -->
	<aside
		class="fixed inset-y-0 left-0 z-40 w-64 -translate-x-full border-r border-border bg-surface transition-transform duration-300 lg:translate-x-0 {sidebarOpen ? 'translate-x-0' : ''}"
		aria-label="Navegación del panel"
	>
		<div class="flex items-center justify-between border-b border-border p-4">
			<span class="font-playfair text-lg font-medium text-title-color">Recetario Admin</span>
			<button type="button" class="rounded-md p-1 hover:bg-accent lg:hidden" on:click={() => (sidebarOpen = false)} aria-label="Cerrar menú">
				<X class="h-5 w-5" aria-hidden="true" />
			</button>
		</div>
		<nav class="space-y-1 p-3">
			{#each nav as item (item.href)}
				<a href={item.href} class="flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-foreground" on:click={() => (sidebarOpen = false)}>
					<item.icon class="h-4 w-4" aria-hidden="true" />
					{item.label}
				</a>
			{/each}
		</nav>
	</aside>

	{#if sidebarOpen}
		<div class="fixed inset-0 z-40 bg-black/40 lg:hidden" on:click={() => (sidebarOpen = false)} aria-hidden="true"></div>
	{/if}

	<!-- Main -->
	<div class="flex flex-1 flex-col lg:ml-64">
		<header class="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-border bg-background/95 px-4 backdrop-blur-sm md:px-6">
			<button type="button" class="rounded-md p-2 hover:bg-accent lg:hidden" on:click={() => (sidebarOpen = true)} aria-label="Abrir menú">
				<Menu class="h-6 w-6" aria-hidden="true" />
			</button>
			<span class="ml-auto text-sm text-muted-foreground">Administrador</span>
		</header>

		<main id="main-content" class="flex-1 p-4 md:p-6 lg:p-8">
			<slot />
		</main>
	</div>
</div>
