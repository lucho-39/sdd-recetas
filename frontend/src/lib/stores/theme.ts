import { derived, get, writable } from 'svelte/store';

export type Theme = 'light' | 'dark' | 'system';

const STORAGE_KEY = 'theme';
const themeState = writable<Theme>('system');

function applyTheme(value: Theme): void {
	if (typeof document === 'undefined') return;
	const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
	const isDark = value === 'dark' || (value === 'system' && prefersDark);
	document.documentElement.classList.toggle('dark', isDark);
}

function persist(value: Theme): void {
	if (typeof localStorage !== 'undefined') localStorage.setItem(STORAGE_KEY, value);
}

export const theme = {
	subscribe: themeState.subscribe,
	init: () => {
		if (typeof localStorage !== 'undefined') {
			const stored = localStorage.getItem(STORAGE_KEY) as Theme | null;
			if (stored === 'light' || stored === 'dark' || stored === 'system') {
				themeState.set(stored);
			}
		}
		applyTheme(get(themeState));
	},
	setTheme: (value: Theme) => {
		themeState.set(value);
		persist(value);
		applyTheme(value);
	},
	toggle: () => {
		const current = get(themeState);
		const next: Theme = current === 'light' ? 'dark' : current === 'dark' ? 'system' : 'light';
		themeState.set(next);
		persist(next);
		applyTheme(next);
		return next;
	}
};

export const isDark = derived(theme, ($theme) => {
	if (typeof window === 'undefined') return false;
	if ($theme === 'dark') return true;
	if ($theme === 'light') return false;
	return window.matchMedia('(prefers-color-scheme: dark)').matches;
});
