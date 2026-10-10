<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { IconX as X } from '@tabler/icons-svelte';

	export let open = false;
	export let title = '';

	const dispatch = createEventDispatcher();
	const titleId = `modal-title-${Math.random().toString(36).slice(2, 9)}`;

	let panel: HTMLDivElement | null = null;
	let previouslyFocused: HTMLElement | null = null;

	function close() {
		dispatch('close');
	}

	function onKeydown(event: KeyboardEvent) {
		if (event.key === 'Escape' && open) {
			event.preventDefault();
			close();
		}
	}

	$: if (open && panel) {
		previouslyFocused = document.activeElement as HTMLElement | null;
		panel.focus();
	} else if (!open && previouslyFocused) {
		previouslyFocused.focus();
		previouslyFocused = null;
	}
</script>

<svelte:window on:keydown={onKeydown} />

{#if open}
	<div class="fixed inset-0 z-50 flex items-center justify-center p-4">
		<button
			type="button"
			class="absolute inset-0 cursor-default bg-black/50"
			aria-label="Cerrar"
			on:click={close}
		></button>
		<div
			bind:this={panel}
			class="relative w-full max-w-lg animate-fade-in rounded-lg border border-border bg-background p-5 shadow-lg"
			role="dialog"
			aria-modal="true"
			aria-labelledby={titleId}
			tabindex="-1"
		>
			<div class="mb-4 flex items-start justify-between gap-4">
				<h2 id={titleId} class="text-lg font-playfair font-medium text-foreground">{title}</h2>
				<button
					type="button"
					class="rounded p-1 text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
					aria-label="Cerrar"
					on:click={close}
				>
					<X class="h-4 w-4" aria-hidden="true" />
				</button>
			</div>

			<slot />

			{#if $$slots.footer}
				<div class="mt-5 flex justify-end gap-2">
					<slot name="footer" />
				</div>
			{/if}
		</div>
	</div>
{/if}
