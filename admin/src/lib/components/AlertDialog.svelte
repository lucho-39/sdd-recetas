<script lang="ts">
	import Dialog from './Dialog.svelte';

	export let open = false;
	export let title: string;
	export let description: string | null = null;
	export let confirmLabel = 'Confirmar';
	export let cancelLabel = 'Cancelar';
	export let destructive = false;
	export let loading = false;
	export let confirmDisabled = false;
	export let onConfirm: () => void = () => {};
	export let onClose: () => void = () => {};
</script>

<Dialog {open} {title} {description} {onClose}>
	<slot />

	<svelte:fragment slot="footer">
		<button type="button" class="btn btn-outline btn-sm" disabled={loading} on:click={onClose}>
			{cancelLabel}
		</button>
		<button
			type="button"
			class="btn {destructive ? 'btn-destructive' : 'btn-primary'} btn-sm"
			disabled={loading || confirmDisabled}
			on:click={onConfirm}
		>
			{confirmLabel}
		</button>
	</svelte:fragment>
</Dialog>
