<script lang="ts">
	import { page } from '$app/stores';
	import { auth } from '$lib/stores/auth';
	import { theme } from '$lib/stores/theme';
	import { AvatarDropdown } from '$components/ui/AvatarDropdown.svelte';
	import { Button } from '$components/ui/Button.svelte';
	import { Link } from '$app/stores';

	let mobileMenuOpen = false;
</script>

<nav class="fixed top-0 left-0 right-0 z-50 border-b border-border bg-background/95 backdrop-blur-sm">
	<div class="container flex h-16 items-center justify-between">
		<!-- Logo -->
		<a href="/" class="flex items-center gap-2 font-playfair font-medium text-xl text-foreground hover:opacity-80 transition-opacity" aria-label="Recetas App - Inicio">
			<span class="text-2xl">🍳</span>
			<span class="hidden sm:block font-playfair font-medium text-title-color">Recetas App</span>
		</a>

		<!-- Desktop Navigation -->
		<div class="hidden md:flex items-center gap-4">
			{#if $auth.isAuthenticated}
				<a href="/mis-recetas" class="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">Mis Recetas</a>
				<a href="/mis-favoritos" class="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">Mis Favoritos</a>
				<AvatarDropdown />
			{:else}
				<a href="/login" class="btn btn-ghost btn-sm">Iniciar sesión</a>
				<a href="/register" class="btn btn-primary btn-sm">Registrarse</a>
			{/if}
		</div>

		<!-- Mobile Menu Button -->
		<button
			class="md:hidden p-2 rounded-md text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
			on:click={() => mobileMenuOpen = !mobileMenuOpen}
			aria-label="Abrir menú"
			aria-expanded={mobileMenuOpen}
		>
			{#if mobileMenuOpen}
				<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
			{:else}
				<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" /></svg>
			{/if}
		</button>
	</div>

	<!-- Mobile Menu -->
	{#if mobileMenuOpen}
	<div class="md:hidden border-t border-border bg-background px-4 py-4 space-y-3 animate-slide-up">
		{#if $auth.isAuthenticated}
			<a href="/mis-recetas" class="block text-sm font-medium text-muted-foreground hover:text-foreground" on:click={() => mobileMenuOpen = false}>Mis Recetas</a>
			<a href="/mis-favoritos" class="block text-sm font-medium text-muted-foreground hover:text-foreground" on:click={() => mobileMenuOpen = false}>Mis Favoritos</a>
			<hr class="border-border" />
			<button class="w-full text-left text-sm font-medium text-destructive hover:bg-destructive/10 px-3 py-2 rounded-md" on:click={() => { $auth.logout(); mobileMenuOpen = false; }}>Cerrar sesión</button>
		{:else}
			<a href="/login" class="block text-sm font-medium text-muted-foreground hover:text-foreground" on:click={() => mobileMenuOpen = false}>Iniciar sesión</a>
			<a href="/register" class="block text-sm font-medium text-primary" on:click={() => mobileMenuOpen = false}>Registrarse</a>
		{/if}
	</div>
{/if}
</nav>