<script lang="ts">
	import Button from '$components/ui/Button.svelte';
	import Dialog from '$components/ui/Dialog.svelte';

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
		<Button variant="outline" disabled={loading} on:click={onClose}>
			{cancelLabel}
		</Button>
		<Button
			variant={destructive ? 'destructive' : 'primary'}
			{loading}
			disabled={confirmDisabled}
			on:click={onConfirm}
		>
			{confirmLabel}
		</Button>
	</svelte:fragment>
</Dialog>
