<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import {
		IconLayoutDashboardFilled as Dashboard,
		IconTagFilled as Tag,
		IconBookmarkFilled as Tags,
		IconUsers as Users,
		IconBookFilled as Recipes,
		IconListFilled as Ingredients,
		IconMenu2 as Menu,
		IconLogout as Logout,
		IconChevronLeft as Collapse
	} from '@tabler/icons-svelte';
	import { auth } from '$lib/stores/auth';

	let collapsed = false;
	let mobileOpen = false;

	const nav = [
		{ href: '/', label: 'Dashboard', icon: Dashboard },
		{ href: '/usuarios', label: 'Usuarios', icon: Users },
		{ href: '/recetas', label: 'Recetas', icon: Recipes },
		{ href: '/ingredientes', label: 'Ingredientes', icon: Ingredients },
		{ href: '/categorias', label: 'Categorías', icon: Tag },
		{ href: '/tags', label: 'Tags', icon: Tags }
	];

	const isLoginPage = $derived($page.url.pathname.startsWith('/admin/login'));

	onMount(() => {
		auth.init();
		const saved = localStorage.getItem('admin_sidebar_collapsed');
		if (saved === '1') collapsed = true;
	});

	function toggleCollapsed() {
		collapsed = !collapsed;
		if (typeof localStorage !== 'undefined') {
			localStorage.setItem('admin_sidebar_collapsed', collapsed ? '1' : '0');
		}
	}

	async function handleLogout() {
		await auth.logout();
		await goto('/admin/login');
	}

	$effect(() => {
		if (!$auth.loading && !$auth.isAuthenticated && !isLoginPage) {
			goto('/admin/login');
		}
	});
</script>

{#if isLoginPage || !$auth.isAuthenticated}
	<slot />
{:else}
	<div class="flex min-h-screen bg-background text-foreground">
		<!-- Sidebar -->
		<aside
			class="fixed inset-y-0 left-0 z-40 flex flex-col border-r border-border bg-surface transition-all duration-200 {collapsed
				? 'w-16'
				: 'w-64'} {mobileOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0"
			aria-label="Navegación del panel"
		>
			<div class="flex h-16 items-center justify-between border-b border-border px-4">
				{#if !collapsed}
					<span class="font-playfair text-lg font-medium text-title-color">Recetario Admin</span>
				{:else}
					<span class="text-lg" aria-hidden="true">🍳</span>
				{/if}
			</div>

			<nav class="flex-1 space-y-1 p-2">
				{#each nav as item (item.href)}
					{@const active = $page.url.pathname === item.href}
					<a
						href={item.href}
						title={collapsed ? item.label : undefined}
						class="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors {active
							? 'bg-primary text-primary-foreground'
							: 'text-muted-foreground hover:bg-accent hover:text-foreground'} {collapsed ? 'justify-center' : ''}"
						on:click={() => (mobileOpen = false)}
					>
						<item.icon class="h-5 w-5 shrink-0" aria-hidden="true" />
						{#if !collapsed}<span>{item.label}</span>{/if}
					</a>
				{/each}
			</nav>

			<button
				type="button"
				class="m-2 hidden items-center gap-2 rounded-md px-3 py-2 text-sm text-muted-foreground hover:bg-accent hover:text-foreground lg:flex {collapsed
					? 'justify-center'
					: ''}"
				on:click={toggleCollapsed}
				aria-label={collapsed ? 'Expandir menú' : 'Colapsar menú'}
			>
				<Collapse class="h-5 w-5 transition-transform {collapsed ? 'rotate-180' : ''}" aria-hidden="true" />
				{#if !collapsed}<span>Colapsar</span>{/if}
			</button>
		</aside>

		{#if mobileOpen}
			<div class="fixed inset-0 z-40 bg-black/40 lg:hidden" on:click={() => (mobileOpen = false)} aria-hidden="true"></div>
		{/if}

		<!-- Main -->
		<div class="flex flex-1 flex-col transition-all duration-200 {collapsed ? 'lg:ml-16' : 'lg:ml-64'}">
			<header class="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-border bg-background/95 px-4 backdrop-blur-sm md:px-6">
				<button type="button" class="rounded-md p-2 hover:bg-accent lg:hidden" on:click={() => (mobileOpen = true)} aria-label="Abrir menú">
					<Menu class="h-6 w-6" aria-hidden="true" />
				</button>
				<span class="ml-auto truncate text-sm text-muted-foreground">
					{$auth.user?.display_name ?? 'Administrador'}
				</span>
				<button type="button" class="ml-3 inline-flex items-center gap-2 rounded-md px-3 py-2 text-sm text-muted-foreground hover:bg-accent hover:text-foreground" on:click={handleLogout}>
					<Logout class="h-4 w-4" aria-hidden="true" />
					<span class="hidden sm:inline">Cerrar sesión</span>
				</button>
			</header>

			<main id="main-content" class="flex-1 p-4 md:p-6 lg:p-8">
				<slot />
			</main>
		</div>
	</div>
{/if}
