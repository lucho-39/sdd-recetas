<script lang="ts">
	import {
		IconUserFilled as User,
		IconLogout as LogOut,
		IconSettingsFilled as Settings,
		IconChevronDown as ChevronDown,
		IconBookFilled as BookOpen,
		IconHeartFilled as Heart
	} from '@tabler/icons-svelte';
	import { auth } from '$lib/stores/auth';

	let open = false;

	$: user = $auth.user;

	async function handleLogout() {
		open = false;
		await auth.logout();
	}

	function close() {
		open = false;
	}
</script>

<svelte:window on:click={() => (open = false)} />

<div class="relative">
	<button
		type="button"
		class="flex items-center gap-1.5 rounded-full p-1 transition-colors hover:bg-accent"
		on:click|stopPropagation={() => (open = !open)}
		aria-expanded={open}
		aria-haspopup="menu"
		aria-label="Menú de usuario"
	>
		{#if user?.avatar_url}
			<img src={user.avatar_url} alt="" class="h-8 w-8 rounded-full object-cover" />
		{:else}
			<span class="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-sm font-medium text-primary-foreground">
				{user?.display_name?.charAt(0).toUpperCase() ?? 'U'}
			</span>
		{/if}
		<ChevronDown class="h-4 w-4 text-muted-foreground" aria-hidden="true" />
	</button>

	{#if open}
		<div
			class="animate-fade-in absolute right-0 top-full z-50 mt-2 w-56 rounded-lg border border-border bg-popover py-1 shadow-lg"
			role="menu"
			on:click|stopPropagation
		>
			<div class="border-b border-border px-3 py-2">
				<p class="truncate text-sm font-medium">{user?.display_name}</p>
				<p class="truncate text-xs text-muted-foreground">{user?.email}</p>
			</div>
			<a href="/perfil" class="flex items-center gap-2 px-3 py-2 text-sm hover:bg-accent" role="menuitem" on:click={close}>
				<User class="h-4 w-4" aria-hidden="true" /> Perfil
			</a>
			<a href="/mis-recetas" class="flex items-center gap-2 px-3 py-2 text-sm hover:bg-accent" role="menuitem" on:click={close}>
				<BookOpen class="h-4 w-4" aria-hidden="true" /> Mis Recetas
			</a>
			<a href="/mis-favoritos" class="flex items-center gap-2 px-3 py-2 text-sm hover:bg-accent" role="menuitem" on:click={close}>
				<Heart class="h-4 w-4" aria-hidden="true" /> Favoritos
			</a>
			<a href="/perfil" class="flex items-center gap-2 px-3 py-2 text-sm hover:bg-accent" role="menuitem" on:click={close}>
				<Settings class="h-4 w-4" aria-hidden="true" /> Configuración
			</a>
			<hr class="my-1 border-border" />
			<button
				type="button"
				class="flex w-full items-center gap-2 px-3 py-2 text-sm text-destructive hover:bg-destructive/10"
				role="menuitem"
				on:click={handleLogout}
			>
				<LogOut class="h-4 w-4" aria-hidden="true" /> Cerrar sesión
			</button>
		</div>
	{/if}
</div>
