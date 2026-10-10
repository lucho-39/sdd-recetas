import { writable } from 'svelte/store';

export type ConfirmRequest = {
	title: string;
	description?: string;
	confirmLabel?: string;
	cancelLabel?: string;
	destructive?: boolean;
};

export type ConfirmState = ConfirmRequest & { resolve: (confirmed: boolean) => void };

export const confirmState = writable<ConfirmState | null>(null);

/**
 * Promise-based replacement for the native `confirm()`. Awaiting it keeps the
 * call sites linear (`if (!(await confirmDialog(...))) return;`) while the
 * dialog itself stays declarative and lives in one place.
 */
export function confirmDialog(request: ConfirmRequest): Promise<boolean> {
	return new Promise((resolve) => {
		confirmState.set({ ...request, resolve });
	});
}
