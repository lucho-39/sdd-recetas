<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	export let variant: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link' = 'default';
	export let size: 'default' | 'sm' | 'lg' | 'icon' = 'default';
	export let disabled = false;
	export let loading = false;
	export let type: 'button' | 'submit' | 'reset' = 'button';
	export let href: string | undefined = undefined;
	export let className: string = '';
	export let fullWidth = false;

	const dispatch = createEventDispatcher();

	function handleClick(event: MouseEvent) {
		if (disabled || loading) {
			event.preventDefault();
			return;
		}
		dispatch('click', event);
	}
</script>

{#if href}
	<a
		href={href}
		class:btn
		class:btn-primary={variant === 'primary'}
		class:btn-secondary={variant === 'secondary'}
		class:btn-destructive={variant === 'destructive'}
		class:btn-outline={variant === 'outline'}
		class:btn-ghost={variant === 'ghost'}
		class:btn-link={variant === 'link'}
		class:btn-sm={size === 'sm'}
		class:btn-lg={size === 'lg'}
		class:w-full={fullWidth}
		class:opacity-50={disabled}
		class:pointer-events-none={disabled}
		aria-disabled={disabled}
		aria-busy={loading}
		on:click={handleClick}
		class={className}
	>
		{#if loading}
			<svg class="mr-2 h-4 w-4 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
				<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
				<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
			</svg>
		{/if}
		<slot />
	</a>
{:else}
	<button
		type={type}
		class:btn
		class:btn-primary={variant === 'primary'}
		class:btn-secondary={variant === 'secondary'}
		class:btn-destructive={variant === 'destructive'}
		class:btn-outline={variant === 'outline'}
		class:btn-ghost={variant === 'ghost'}
		class:btn-link={variant === 'link'}
		class:btn-sm={size === 'sm'}
		class:btn-lg={size === 'lg'}
		class:w-full={fullWidth}
		disabled={disabled || loading}
		aria-disabled={disabled || loading}
		aria-busy={loading}
		on:click={handleClick}
		class={className}
	>
		{#if loading}
			<svg class="mr-2 h-4 w-4 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
				<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
				<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
			</svg>
		{/if}
		<slot />
	</button>
{/if}

<style>
	:global(.btn) {
		@apply inline-flex items-center justify-center gap-2 rounded-md font-medium
			transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary
			disabled:pointer-events-none disabled:opacity-50;
	}

	:global(.btn-primary) {
		@apply bg-primary text-primary-foreground hover:bg-primary/90;
	}

	:global(.btn-secondary) {
		@apply bg-secondary text-secondary-foreground hover:bg-secondary/80;
	}

	:global(.btn-destructive) {
		@apply bg-destructive text-destructive-foreground hover:bg-destructive/90;
	}

	:global(.btn-outline) {
		@apply border border-input bg-background hover:bg-accent hover:text-accent-foreground;
	}

	:global(.btn-ghost) {
		@apply hover:bg-accent hover:text-accent-foreground;
	}

	:global(.btn-sm) {
		@apply h-8 px-3 text-sm;
	}

	:global(.btn-lg) {
		@apply h-12 px-6 text-lg;
	}
</style>