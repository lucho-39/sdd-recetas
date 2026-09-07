<script lang="ts">
	import { auth } from '$lib/stores/auth';
	import { Button } from '$components/ui/Button.svelte';
	import { User, LogOut, Settings, ChevronDown } from 'lucide-svelte';

	export let user: import('$lib/types').User | null = $derived($auth.currentUser);
</script>

<div class="relative">
	<button
		class="flex items-center gap-2 p-1.5 rounded-full hover:bg-accent transition-colors"
		on:click={() => open = !open}
		aria-expanded={open}
		aria-haspopup="true"
		aria-label="Menú de usuario"
	>
		{#if user?.avatar_url}
			<img src={user.avatar_url} alt="" class="w-8 h-8 rounded-full" />
		{:else}
			<div class="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-medium text-sm">
				{user?.display_name?.charAt(0).toUpperCase() || 'U'}
			</div>
		{/if}
		<ChevronDown class="w-4 h-4 text-muted-foreground" />
	</button>

	{#if open}
	<div class="absolute right-0 top-full mt-2 w-48 bg-popover border border-border rounded-lg shadow-lg py-1 z-50 animate-fade-in">
		<div class="px-3 py-2 border-b border-border">
			<p class="text-sm font-medium truncate">{user?.display_name}</p>
			<p class="text-xs text-muted-foreground truncate">{user?.email}</p>
		</div>
		<a href="/perfil" class="flex items-center gap-2 px-3 py-2 text-sm text-foreground hover:bg-accent" on:click={() => open = false}>
			<User class="w-4 h-4" />
			Perfil
		</a>
		<a href="/mis-recetas" class="flex items-center gap-2 px-3 py-2 text-sm text-foreground hover:bg-accent" on:click={() => open = false}>
			<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2h14a2 2 0 012 2z" /></svg>
			Mis Recetas
		</a>
		<a href="/mis-favoritos" class="flex items-center gap-2 px-3 py-2 text-sm text-foreground hover:bg-accent" on:click={() => open = false}>
			<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" /></svg>
			Favoritos
		</a>
		<hr class="border-border my-1" />
		<button class="w-full flex items-center gap-2 px-3 py-2 text-sm text-foreground hover:bg-accent" on:click={() => { /* open settings */ }}>
			<Settings class="w-4 h-4" />
			Configuración
		</button>
		<hr class="border-border my-1" />
		<button class="w-full flex items-center gap-2 px-3 py-2 text-sm text-destructive hover:bg-destructive/10" on:click={() => { logout(); }}>
			<LogOut class="w-4 h-4" />
			Cerrar sesión
		</button>
	</div>
{/if}

<script lang="ts">
	let open = false;
	import { ChevronDown } from 'lucide-svelte';

	function logout() {
		// TODO: Implement logout
	}
</script>