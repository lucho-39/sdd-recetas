<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { X } from 'lucide-svelte';
	import { Button } from '$components/ui/Button.svelte';

	export let variant: 'default' | 'destructive' | 'warning' | 'success' = 'default';
	export let title: string = '';
	export let description: string = '';
	export let action: { label: string; onClick: () => void } | null = null;
	export let dismissible = true;
	export let onDismiss: (() => void) | null = null;

	const dispatch = createEventDispatcher();
</script>

<div
	class="relative w-full rounded-lg border p-4
	bg-background text-foreground
	data-[variant=destructive]:border-destructive/50 data-[variant=destructive]:bg-destructive/10 data-[variant=destructive]:text-destructive
	data-[variant=warning]:border-warning/50 data-[variant=warning]:bg-warning/10 data-[variant=warning]:text-warning
	data-[variant=success]:border-success/50 data-[variant=success]:bg-success/10 data-[variant=success]:text-success
	animate-fade-in"
	role="alert"
	aria-live="polite"
>
	<div class="flex items-start gap-3">
		{#if variant === 'destructive'}
			<svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.283 2.5-2.882l-1.5-6.5c-.2-.6-.75-1.118-1.35-1.118H6.5c-.6 0-1.05-.453-1.1-.995l-.5-1.5c-.1-.6-.25-1.1.15-1.5.4-.4.8-.65 1.15-.75h12.5" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" /></svg>
		{:else if variant === 'warning'}
			<svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.283 2.5-2.882l-1.5-6.5c-.2-.6-.75-1.118-1.35-1.118H6.5c-.6 0-1.05-.453-1.1-.995l-.5-1.5c-.1-.6-.25-1.1.15-1.5.4-.4.8-.65 1.15-.75h12.5" /></svg>
		{:else if variant === 'success'}
			<svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
		{:else}
			<svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" /></svg>
		{/if}
	<div class="flex-1 min-w-0">
		<h4 class="font-medium">{title}</h4>
		<p class="text-sm opacity-90 mt-1">{description}</p>
	</div>
	{#if action}
		<Button variant="outline" size="sm" on:click={action.onClick}>
			{action.label}
		</Button>
	{/if}
	{#if dismissible}
		<button
			class="absolute top-2 right-2 p-1 hover:bg-accent rounded"
			on:click={onDismiss}
			aria-label="Cerrar"
		>
			<X class="w-4 h-4" />
		</button>
	{/if}
</div>