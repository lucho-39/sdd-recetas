import { writable } from 'svelte/store';

export type ConfirmRequest = {
	title: string;
	description?: string;
	confirmLabel?: string;
	cancelLabel?: string;
	destructive?: boolean;
	/**
	 * Present ⇒ the dialog collects text. That is what makes `promptDialog`
	 * differ from `confirmDialog` — not a second host component.
	 */
	promptLabel?: string;
	promptDefault?: string;
	promptPlaceholder?: string;
};

export type ConfirmResult = {
	confirmed: boolean;
	password: string | null;
	/** Text entered by `promptDialog`; null when cancelled. */
	value: string | null;
};

export type ConfirmState = ConfirmRequest & {
	requirePassword: boolean;
	resolve: (result: ConfirmResult) => void;
};

export const confirmState = writable<ConfirmState | null>(null);

/**
 * Promise-based replacement for the native `confirm()`. Awaiting it keeps the
 * call sites linear (`if (!(await confirmDialog(...))) return;`) while the
 * dialog itself stays declarative and lives in one place.
 */
export function confirmDialog(request: ConfirmRequest): Promise<boolean> {
	return new Promise((resolve) => {
		confirmState.set({
			...request,
			requirePassword: false,
			resolve: ({ confirmed }) => resolve(confirmed)
		});
	});
}

/**
 * Same dialog, but demands a fresh password before confirming. Destructive
 * account operations use it: a valid session alone must not be enough.
 */
export function confirmPasswordDialog(request: ConfirmRequest): Promise<ConfirmResult> {
	return new Promise((resolve) => {
		confirmState.set({ ...request, requirePassword: true, resolve });
	});
}

/**
 * Promise-based replacement for the native `prompt()`. Resolves with the
 * entered text, or null if the dialog was cancelled — the same two outcomes
 * `prompt()` produces, so call sites read the same way.
 */
export function promptDialog(request: ConfirmRequest): Promise<string | null> {
	return new Promise((resolve) => {
		confirmState.set({
			...request,
			requirePassword: false,
			resolve: ({ confirmed, value }) => resolve(confirmed ? value : null)
		});
	});
}
