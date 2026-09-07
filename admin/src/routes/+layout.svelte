<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { theme } from '$lib/stores/theme';
	import { auth } from '$lib/stores/auth';

	let sidebarOpen = false;
</script>

<div class="min-h-screen flex">
	<!-- Sidebar -->
	<aside class="fixed inset-y-0 left-0 z-40 w-64 bg-surface border-r border-border transform transition-transform duration-300 lg:translate-x-0 -translate-x-full" class:open={sidebarOpen}>
		<div class="flex flex-col h-full">
			<!-- Header -->
			<div class="p-4 border-b border-border flex items-center justify-between">
				<h1 class="font-playfair font-medium text-xl text-foreground">Admin</h1>
				<button class="lg:hidden p-2 rounded-md hover:bg-accent" on:click={() => sidebarOpen = false} aria-label="Cerrar menú">
					<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
				</button>
			</div>

			<!-- Navigation -->
			<nav class="flex-1 p-4 space-y-1 overflow-y-auto" aria-label="Navegación principal">
				<NavLink href="/admin" icon="LayoutDashboard">Dashboard</NavLink>
				<NavLink href="/admin/categorias" icon="Tag">Categorías</NavLink>
				<NavLink href="/admin/usuarios" icon="Users">Usuarios</NavLink>
				<NavLink href="/admin/recetas" icon="BookOpen">Recetas</NavLink>
				<NavLink href="/admin/ingredientes" icon="List">Ingredientes</NavLink>
				<NavLink href="/admin/metricas" icon="BarChart">Métricas</NavLink>
				<NavLink href="/admin/config" icon="Settings">Configuración</NavLink>
			</nav>

			<!-- Footer -->
			<div class="p-4 border-t border-border">
				<p class="text-xs text-muted-foreground text-center">Recetario Admin v0.1.0</p>
			</div>
		</div>
	</aside>

	<!-- Mobile overlay -->
	{#if sidebarOpen}
		<div class="fixed inset-0 z-40 bg-black/50 lg:hidden" on:click={() => sidebarOpen = false} aria-hidden="true" />
	{/if}

	<!-- Main content -->
	<main class="flex-1 lg:ml-64 min-h-screen flex flex-col">
		<!-- Top bar -->
		<header class="fixed top-0 right-0 left-0 lg:left-64 z-30 h-16 border-b border-border bg-background/95 backdrop-blur-sm flex items-center justify-between px-4 md:px-6">
			<button class="lg:hidden p-2 rounded-md hover:bg-accent" on:click={() => sidebarOpen = true} aria-label="Abrir menú">
				<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" /></svg>
			</button>

			<div class="flex-1 flex items-center justify-end gap-4">
				<div class="hidden md:flex items-center gap-4">
					<span class="text-sm text-muted-foreground">Admin</span>
				</div>
				<div class="flex items-center gap-2">
					<button class="p-2 rounded-full hover:bg-accent transition-colors" aria-label="Notificaciones">
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.41-1.41c-0.78-0.78-2.05-0.78-2.83 0L12 19.41 6.41 13.89a2 2 0 00-2.83 0L4 15.41c-0.78 0.78-0.78 2.05 0 2.83l1.41 1.41c0.78 0.78 2.05 0.78 2.83 0L12 20.41l6.41-6.41c0.78-0.78 0.78-2.05 0-2.83L18 5.41c0.78-0.78 2.05-0.78 2.83 0l1.41 1.41c0.78 0.78 0.78 2.05 0 2.83z" /></svg>
					</button>
					<div class="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-medium text-sm">
						A
					</div>
				</div>
			</div>
		</header>

		<!-- Main content -->
		<main class="flex-1 pt-16 lg:pt-20 p-4 md:p-6 lg:p-8" id="main-content">
			<slot />
		</main>
	</main>
</div>

<style>
	:global(*) {
		margin: 0;
		padding: 0;
		box-sizing: border-box;
	}

	:global(html) {
		font-size: 16px;
		scroll-behavior: smooth;
	}

	:global(body) {
		@apply bg-background text-foreground font-sans antialiased;
		font-feature-settings: "cv02", "cv03", "cv04", "cv11";
	}
</style>