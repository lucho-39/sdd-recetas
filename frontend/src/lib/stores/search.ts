import { writable, derived, get } from 'svelte/store';
import type { RecipeFilters } from '$lib/types';

interface SearchState {
	filters: RecipeFilters;
}

function createSearchStore() {
	const store = writable<SearchState>({ filters: {} });

	return {
		subscribe: store.subscribe,
		setFilters: (filters: Partial<RecipeFilters>) =>
			store.update((s) => ({ filters: { ...s.filters, ...filters } })),
		updateFilters: (filters: Partial<RecipeFilters>) =>
			store.update((s) => ({ filters: { ...s.filters, ...filters } })),
		clearFilters: () => store.set({ filters: {} }),
		addTag: (tag: string) =>
			store.update((s) => ({
				filters: { ...s.filters, tags: [...(s.filters.tags ?? []), tag] }
			})),
		removeTag: (tag: string) =>
			store.update((s) => ({
				filters: { ...s.filters, tags: (s.filters.tags ?? []).filter((t) => t !== tag) }
			})),
		addIngredient: (name: string) =>
			store.update((s) => ({
				filters: { ...s.filters, ingredients: [...(s.filters.ingredients ?? []), name] }
			})),
		removeIngredient: (name: string) =>
			store.update((s) => ({
				filters: {
					...s.filters,
					ingredients: (s.filters.ingredients ?? []).filter((i) => i !== name)
				}
			})),
		getFilters: () => get(store).filters
	};
}

export const searchStore = createSearchStore();

export const searchFilters = derived(searchStore, ($store) => $store.filters);

export const hasAnyFilters = derived(searchStore, ($store) => {
	const f = $store.filters;
	return !!(
		f.query ||
		f.category ||
		(f.tags && f.tags.length > 0) ||
		(f.ingredients && f.ingredients.length > 0)
	);
});
