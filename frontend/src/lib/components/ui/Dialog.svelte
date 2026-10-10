<script lang="ts">
	import { IconX as X } from '@tabler/icons-svelte';

	export let open = false;
	export let title = '';
	export let description: string | null = null;
	export let closeOnOverlay = true;
	export let onClose: () => void = () => {};

	const titleId = `dialog-title-${Math.random().toString(36).slice(2, 9)}`;
	const descriptionId = `dialog-description-${Math.random().toString(36).slice(2, 9)}`;

	let panel: HTMLDivElement | null = null;
	let previouslyFocused: HTMLElement | null = null;

	function onKeydown(event: KeyboardEvent) {
		if (!open) return;

		if (event.key === 'Escape') {
			event.preventDefault();
			onClose();
			return;
		}

		if (event.key === 'Tab' && panel) {
			const focusables = Array.from(
				panel.querySelectorAll<HTMLElement>(
					'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
				)
			);
			if (focusables.length === 0) {
				event.preventDefault();
				panel.focus();
				return;
			}
			const first = focusables[0];
			const last = focusables[focusables.length - 1];
			if (event.shiftKey && document.activeElement === first) {
				event.preventDefault();
				last.focus();
			} else if (!event.shiftKey && document.activeElement === last) {
				event.preventDefault();
				first.focus();
			}
		}
	}

	$: if (open && panel) {
		previouslyFocused = document.activeElement as HTMLElement | null;
		const content = panel.querySelector<HTMLElement>('.dialog-content');
		const target =
			content?.querySelector<HTMLElement>('button, input, select, textarea, a[href]') ??
			panel.querySelector<HTMLElement>('button, input, select, textarea, a[href]') ??
			panel;
		target.focus();
	} else if (!open && previouslyFocused) {
		previouslyFocused.focus();
		previouslyFocused = null;
	}
</script>

<svelte:window on:keydown={onKeydown} />

{#if open}
	<div class="fixed inset-0 z-50 flex items-center justify-center p-4">
		{#if closeOnOverlay}
			<button
				type="button"
				class="absolute inset-0 cursor-default bg-black/50"
				aria-label="Cerrar"
				on:click={onClose}
			></button>
		{:else}
			<div class="absolute inset-0 bg-black/50"></div>
		{/if}
		<div
			bind:this={panel}
			class="relative w-full max-w-lg animate-fade-in rounded-lg border border-border bg-background p-5 shadow-lg"
			role="dialog"
			aria-modal="true"
			aria-labelledby={titleId}
			aria-describedby={description ? descriptionId : undefined}
			tabindex="-1"
		>
			<div class="mb-4 flex items-start justify-between gap-4">
				<div class="min-w-0">
					<h2 id={titleId} class="text-lg font-playfair font-medium text-foreground">{title}</h2>
					{#if description}
						<p id={descriptionId} class="mt-1 text-sm text-muted-foreground">{description}</p>
					{/if}
				</div>
				<button
					type="button"
					class="shrink-0 rounded p-1 text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
					aria-label="Cerrar"
					on:click={onClose}
				>
					<X class="h-4 w-4" aria-hidden="true" />
				</button>
			</div>

			<!-- Focus starts here, not on the header close button: a form dialog
			     lands on its first field, a confirmation dialog on Cancel. -->
			<div class="dialog-content">
				<slot />

				{#if $$slots.footer}
					<div class="mt-5 flex justify-end gap-2">
						<slot name="footer" />
					</div>
				{/if}
			</div>
		</div>
	</div>
{/if}
