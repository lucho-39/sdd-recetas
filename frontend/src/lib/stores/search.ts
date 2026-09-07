import { writable, derived } from 'svelte/store';
import type { RecipeFilters } from '$lib/types';

interface SearchState {
  filters: RecipeFilters;
}

function createSearchStore() {
  const { subscribe, set, update } = writable<SearchState>({
    filters: {},
  });

  return {
    subscribe,
    setFilters: (filters: Partial<RecipeFilters>) => update(state => ({
      ...state,
      filters: { ...state.filters, ...filters },
    })),
    addTag: (tag: string) => update(state => ({
      ...state,
      filters: {
        ...state.filters,
        tags: [...(state.filters.tags || []), tag],
      },
    })),
    removeTag: (tag: string) => update(state => ({
      ...state,
      filters: {
        ...state.filters,
        tags: (state.filters.tags || []).filter(t => t !== tag),
      },
    })),
    addIngredient: (ingredient: string) => update(state => ({
      ...state,
      filters: {
        ...state.filters,
        ingredients: [...(state.filters.ingredients || []), ingredient],
      },
    })),
    removeIngredient: (ingredient: string) => update(state => ({
      ...state,
      filters: {
        ...state.filters,
        ingredients: (state.filters.ingredients || []).filter(i => i !== ingredient),
      },
    })),
    clearFilters: () => set({ filters: {} }),
    hasAnyFilters: derived(({ subscribe }) => {
      let hasAny = false;
      subscribe(state => {
        hasAny = !!(
          state.filters.category ||
          (state.filters.tags && state.filters.tags.length > 0) ||
          (state.filters.ingredients && state.filters.ingredients.length > 0) ||
          state.filters.query
        );
      })();
      return hasAny;
    }),
    getFilters: derived(({ subscribe }) => {
      let filters: RecipeFilters = {};
      subscribe(state => { filters = state.filters; })();
      return filters;
    }),
  };

export const searchStore = createSearchStore();

export const hasAnyFilters = derived(searchStore, $store => 
  !!($store.filters.category ||
    ($store.filters.tags && $store.filters.tags.length > 0) ||
    ($store.filters.ingredients && $store.filters.ingredients.length > 0) ||
    $store.filters.query)
);