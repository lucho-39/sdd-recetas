import { writable, derived } from 'svelte/store';
import { persisted } from 'svelte-local-storage-store';

export type Theme = 'light' | 'dark' | 'system';

function createThemeStore() {
  const { subscribe, set, update } = persisted<Theme>('theme', 'system');

  return {
    subscribe,
    init: () => {
      if (typeof window !== 'undefined') {
        const stored = subscribe.get();
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const isDark = stored === 'dark' || (stored === 'system' && prefersDark);
        document.documentElement.classList.toggle('dark', isDark);
      }
    },
    setTheme: (theme: Theme) => {
      set(theme);
      if (typeof window !== 'undefined') {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const isDark = theme === 'dark' || (theme === 'system' && prefersDark);
        document.documentElement.classList.toggle('dark', isDark);
      }
    },
    toggle: () => {
      update(current => {
        const next = current === 'light' ? 'dark' : current === 'dark' ? 'system' : 'light';
        if (typeof window !== 'undefined') {
          const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
          const isDark = next === 'dark' || (next === 'system' && prefersDark);
          document.documentElement.classList.toggle('dark', isDark);
        }
        return next;
      });
    },
  };

export const theme = createThemeStore();

export const isDark = derived(theme, $theme => {
  if (typeof window === 'undefined') return false;
  if ($theme === 'dark') return true;
  if ($theme === 'light') return false;
  return window.matchMedia('(prefers-color-scheme: dark)').matches;
});