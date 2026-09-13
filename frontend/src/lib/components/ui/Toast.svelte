<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { IconX as X } from '@tabler/icons-svelte';

	export let variant: 'default' | 'destructive' | 'success' = 'default';
	export let title: string = '';
	export let message: string = '';
	export let className: string = '';

	const dispatch = createEventDispatcher();

	function dismiss() {
		dispatch('dismiss');
	}
</script>

<div
	class="toast"
	class:toast-default={variant === 'default'}
	class:toast-destructive={variant === 'destructive'}
	class:toast-success={variant === 'success'}
	class={className}
	role="alert"
	aria-live="polite"
>
	<div class="toast-content">
		{#if title}
			<h4 class="toast-title">{title}</h4>
		{/if}
		{#if message}
			<p class="toast-message">{message}</p>
		{/if}
	</div>
	<button
		class="toast-close"
		on:click={dismiss}
		aria-label="Dismiss"
	>
		<X class="h-4 w-4" />
	</button>
</div>

<style>
	.toast {
		@apply flex items-start gap-3 p-4 rounded-lg border shadow-lg min-w-[300px] max-w-md animate-in slide-in-from-top-2 duration-300;
	}

	.toast-default {
		@apply bg-background border-border text-foreground;
	}

	.toast-destructive {
		@apply bg-destructive/10 border-destructive/30 text-destructive;
	}

	.toast-success {
		@apply bg-green-50 border-green-200 text-green-900 dark:bg-green-900/20 dark:border-green-800 dark:text-green-100;
	}

	.toast-content {
		@apply flex-1;
	}

	.toast-title {
		@apply font-semibold text-sm mb-1;
	}

	.toast-message {
		@apply text-sm opacity-90;
	}

	.toast-close {
		@apply p-1 rounded hover:bg-accent transition-colors text-foreground/50 hover:text-foreground;
		flex-shrink: 0;
	}
</style>