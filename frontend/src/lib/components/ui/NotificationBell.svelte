<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { IconBellFilled as Bell, IconTrashFilled as Trash } from '@tabler/icons-svelte';
	import { notifications } from '$lib/stores/notifications';
	import AuthorAvatar from '$components/common/AuthorAvatar.svelte';
	import type { AppNotification } from '$lib/types';

	let open = false;

	$: unread = $notifications.unreadCount;
	$: badge = unread > 99 ? '99+' : String(unread);

	onMount(() => notifications.load());

	function describe(notification: AppNotification): string {
		const who = notification.actor?.display_name ?? 'Alguien';
		if (notification.type === 'favorite') return `${who} guardó tu receta`;
		if (notification.type === 'rating') {
			const score = notification.detail?.score;
			return score ? `${who} calificó tu receta con ${score}★` : `${who} calificó tu receta`;
		}
		return `${who} interactuó con tu receta`;
	}

	function timeAgo(value: string): string {
		const diff = Date.now() - new Date(value).getTime();
		const minutes = Math.floor(diff / 60000);
		if (minutes < 1) return 'ahora';
		if (minutes < 60) return `hace ${minutes} min`;
		const hours = Math.floor(minutes / 60);
		if (hours < 24) return `hace ${hours} h`;
		return `hace ${Math.floor(hours / 24)} d`;
	}

	async function openNotification(notification: AppNotification) {
		open = false;
		await notifications.markRead(notification.id);
		if (notification.recipe_slug) await goto(`/receta/${notification.recipe_slug}`);
	}
</script>

<svelte:window on:click={() => (open = false)} />

<div class="relative">
	<button
		type="button"
		class="relative rounded-md p-2 text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
		on:click|stopPropagation={() => (open = !open)}
		aria-expanded={open}
		aria-haspopup="menu"
		aria-label={unread ? `Notificaciones, ${unread} sin leer` : 'Notificaciones'}
	>
		<Bell class="h-5 w-5" aria-hidden="true" />
		{#if unread > 0}
			<span class="absolute -right-0.5 -top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-destructive px-1 text-[10px] font-medium text-white">
				{badge}
			</span>
		{/if}
	</button>

	{#if open}
		<div
			class="animate-fade-in absolute right-0 top-full z-50 mt-2 w-80 rounded-lg border border-border bg-popover shadow-lg"
			role="menu"
			on:click|stopPropagation
		>
			<div class="flex items-center justify-between border-b border-border px-3 py-2">
				<span class="text-sm font-medium text-foreground">Notificaciones</span>
				{#if $notifications.items.length > 0}
					<div class="flex gap-2 text-xs">
						{#if unread > 0}
							<button type="button" class="text-primary hover:underline" on:click={() => notifications.markAllRead()}>
								Marcar leídas
							</button>
						{/if}
						<button type="button" class="text-destructive hover:underline" on:click={() => notifications.removeAll()}>
							Borrar todas
						</button>
					</div>
				{/if}
			</div>

			{#if $notifications.loading && $notifications.items.length === 0}
				<p class="px-3 py-6 text-center text-sm text-muted-foreground">Cargando…</p>
			{:else if $notifications.items.length === 0}
				<p class="px-3 py-6 text-center text-sm text-muted-foreground">No tenés notificaciones.</p>
			{:else}
				<ul class="max-h-96 overflow-y-auto">
					{#each $notifications.items as notification (notification.id)}
						<li class="group flex items-start gap-3 border-b border-border/60 px-3 py-3 hover:bg-accent/50">
							<button
								type="button"
								class="flex flex-1 items-start gap-3 text-left"
								on:click={() => openNotification(notification)}
							>
								{#if notification.actor}
									<AuthorAvatar author={notification.actor} size="xs" />
								{:else}
									<span class="flex h-6 w-6 items-center justify-center rounded-full bg-muted text-xs" aria-hidden="true">🍳</span>
								{/if}
								<span class="min-w-0 flex-1">
									<span class="block text-sm text-foreground">{describe(notification)}</span>
									{#if notification.recipe_title}
										<span class="block truncate text-xs text-muted-foreground">{notification.recipe_title}</span>
									{/if}
									<span class="block text-xs text-muted-foreground">{timeAgo(notification.created_at)}</span>
								</span>
								{#if !notification.is_read}
									<span class="mt-1 h-2 w-2 shrink-0 rounded-full bg-primary" title="Sin leer"></span>
								{/if}
							</button>
							<button
								type="button"
								class="rounded p-1 text-muted-foreground opacity-0 transition-opacity hover:text-destructive group-hover:opacity-100"
								on:click={() => notifications.remove(notification.id)}
								aria-label="Eliminar notificación"
							>
								<Trash class="h-4 w-4" aria-hidden="true" />
							</button>
						</li>
					{/each}
				</ul>
			{/if}
		</div>
	{/if}
</div>
