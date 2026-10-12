<script lang="ts">
	import AlertDialog from '$components/ui/AlertDialog.svelte';
	import { confirmState, type ConfirmResult } from '$lib/stores/confirm';

	let password = '';
	let value = '';

	$: state = $confirmState;
	$: requirePassword = state?.requirePassword ?? false;
	$: promptLabel = state?.promptLabel ?? null;

	// Seed (and clear) the field on open. Only `state` is read here, so typing
	// never re-runs this and overwrites what the user entered.
	$: if (state) {
		value = state.promptDefault ?? '';
		password = '';
	}

	$: canConfirm =
		(!requirePassword || password.length > 0) && (promptLabel === null || value.trim().length > 0);

	function settle(confirmed: boolean) {
		const current = $confirmState;
		const result: ConfirmResult = {
			confirmed,
			password: confirmed && current?.requirePassword ? password : null,
			value: confirmed && current?.promptLabel ? value : null
		};
		password = '';
		value = '';
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
	{:else if promptLabel !== null}
		<label class="block">
			<span class="mb-1 block text-sm font-medium text-foreground">{promptLabel}</span>
			<input
				type="text"
				bind:value
				class="input-base"
				placeholder={$confirmState?.promptPlaceholder ?? ''}
			/>
		</label>
	{/if}
</AlertDialog>
