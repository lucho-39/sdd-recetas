<script lang="ts">
	import AlertDialog from '$components/ui/AlertDialog.svelte';
	import { confirmState, type ConfirmResult } from '$lib/stores/confirm';

	let password = '';

	$: requirePassword = $confirmState?.requirePassword ?? false;
	$: canConfirm = !requirePassword || password.length > 0;

	function settle(confirmed: boolean) {
		const current = $confirmState;
		const result: ConfirmResult = {
			confirmed,
			password: confirmed && current?.requirePassword ? password : null
		};
		password = '';
		confirmState.set(null);
		current?.resolve(result);
	}
</script>

<AlertDialog
	open={$confirmState !== null}
	title={$confirmState?.title ?? ''}
	description={$confirmState?.description ?? null}
	confirmLabel={$confirmState?.confirmLabel ?? 'Confirmar'}
	cancelLabel={$confirmState?.cancelLabel ?? 'Cancelar'}
	destructive={$confirmState?.destructive ?? false}
	confirmDisabled={!canConfirm}
	onConfirm={() => settle(true)}
	onClose={() => settle(false)}
>
	{#if requirePassword}
		<label class="block">
			<span class="mb-1 block text-sm font-medium text-foreground">Contraseña actual</span>
			<input
				type="password"
				bind:value={password}
				class="input-base"
				autocomplete="current-password"
			/>
		</label>
	{/if}
</AlertDialog>
