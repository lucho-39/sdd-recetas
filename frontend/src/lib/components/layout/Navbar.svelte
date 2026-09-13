<script lang="ts">
	import { IconMenu2 as Menu, IconX as X, IconMoonFilled as Moon } from '@tabler/icons-svelte';
	import { auth } from '$lib/stores/auth';
	import { theme } from '$lib/stores/theme';
	import AvatarDropdown from '$components/ui/AvatarDropdown.svelte';
	import NotificationBell from '$components/ui/NotificationBell.svelte';

	let mobileMenuOpen = false;

	function toggleTheme() {
		theme.toggle();
	}
</script>

<header class="sticky top-0 z-50 border-b border-border bg-background/95 backdrop-blur-sm">
	<nav class="container flex h-16 items-center justify-between" aria-label="Navegación principal">
		<!-- Logo -->
		<a
			href="/"
			class="flex items-center gap-2 font-playfair text-xl font-medium text-title-color transition-opacity hover:opacity-80"
			aria-label="Recetario IA — Inicio"
		>
			<span class="text-2xl" aria-hidden="true">🍳</span>
			<span class="hidden sm:inline">Recetario IA</span>
		</a>

		<!-- Desktop nav -->
		<div class="hidden items-center gap-1 md:flex">
			<a href="/" class="rounded-md px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-foreground">Explorar</a>
			<a href="/buscar" class="rounded-md px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-foreground">Buscar</a>
			{#if $auth.isAuthenticated}
				<a href="/mis-recetas" class="rounded-md px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-foreground">Mis Recetas</a>
				<a href="/mis-favoritos" class="rounded-md px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-foreground">Favoritos</a>
			{/if}
		</div>

		<!-- Actions -->
		<div class="flex items-center gap-2">
			<button
				type="button"
				class="rounded-md p-2 text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
				on:click={toggleTheme}
				aria-label="Cambiar tema"
			>
				<Moon class="h-5 w-5" aria-hidden="true" />
			</button>

			{#if $auth.isAuthenticated}
				<a href="/recetas/nueva" class="btn btn-primary btn-sm hidden sm:inline-flex">Crear receta</a>
				<NotificationBell />
				<AvatarDropdown />
			{:else}
				<a href="/login" class="btn btn-ghost btn-sm hidden sm:inline-flex">Iniciar sesión</a>
				<a href="/register" class="btn btn-primary btn-sm hidden sm:inline-flex">Registrarse</a>
			{/if}

			<button
				type="button"
				class="rounded-md p-2 text-muted-foreground transition-colors hover:bg-accent hover:text-foreground md:hidden"
				on:click={() => (mobileMenuOpen = !mobileMenuOpen)}
				aria-label={mobileMenuOpen ? 'Cerrar menú' : 'Abrir menú'}
				aria-expanded={mobileMenuOpen}
			>
				{#if mobileMenuOpen}
					<X class="h-6 w-6" aria-hidden="true" />
				{:else}
					<Menu class="h-6 w-6" aria-hidden="true" />
				{/if}
			</button>
		</div>
	</nav>

	<!-- Mobile menu -->
	{#if mobileMenuOpen}
		<div class="border-t border-border bg-background px-4 py-4 md:hidden">
			<div class="flex flex-col gap-1">
				<a href="/" class="rounded-md px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-accent hover:text-foreground" on:click={() => (mobileMenuOpen = false)}>Explorar</a>
				<a href="/buscar" class="rounded-md px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-accent hover:text-foreground" on:click={() => (mobileMenuOpen = false)}>Buscar</a>
				{#if $auth.isAuthenticated}
					<a href="/recetas/nueva" class="rounded-md px-3 py-2 text-sm font-medium text-primary hover:bg-accent" on:click={() => (mobileMenuOpen = false)}>Crear receta</a>
					<a href="/mis-recetas" class="rounded-md px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-accent hover:text-foreground" on:click={() => (mobileMenuOpen = false)}>Mis Recetas</a>
					<a href="/mis-favoritos" class="rounded-md px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-accent hover:text-foreground" on:click={() => (mobileMenuOpen = false)}>Favoritos</a>
					<button
						type="button"
						class="rounded-md px-3 py-2 text-left text-sm font-medium text-destructive hover:bg-destructive/10"
						on:click={() => { auth.logout(); mobileMenuOpen = false; }}
					> Cerrar sesión</button>
				{:else}
					<a href="/login" class="rounded-md px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-accent hover:text-foreground" on:click={() => (mobileMenuOpen = false)}>Iniciar sesión</a>
					<a href="/register" class="rounded-md px-3 py-2 text-sm font-medium text-primary hover:bg-accent" on:click={() => (mobileMenuOpen = false)}>Registrarse</a>
				{/if}
			</div>
		</div>
	{/if}
</header>
