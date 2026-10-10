<script lang="ts">
	import AlertDialog from '$components/ui/AlertDialog.svelte';
	import { confirmState } from '$lib/stores/confirm';

	function settle(confirmed: boolean) {
		const current = $confirmState;
		confirmState.set(null);
		current?.resolve(confirmed);
	}
</script>

<AlertDialog
	open={$confirmState !== null}
	title={$confirmState?.title ?? ''}
	description={$confirmState?.description ?? null}
	confirmLabel={$confirmState?.confirmLabel ?? 'Confirmar'}
	cancelLabel={$confirmState?.cancelLabel ?? 'Cancelar'}
	destructive={$confirmState?.destructive ?? false}
	onConfirm={() => settle(true)}
	onClose={() => settle(false)}
/>
