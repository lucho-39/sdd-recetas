import { writable, derived } from 'svelte/store';
import type { Recipe, RecipeFilters } from '$lib/types';

interface RecipesState {
  recipes: Recipe[];
  loading: boolean;
  loadingMore: boolean;
  hasMore: boolean;
  page: number;
  filters: RecipeFilters;
}

function createRecipesStore() {
  const { subscribe, set, update } = writable<RecipesState>({
    recipes: [],
    loading: false,
    loadingMore: false,
    hasMore: true,
    page: 1,
    filters: {},
  });

  return {
    subscribe,
    setFilters: (filters: Partial<RecipeFilters>) => update(state => ({
      ...state,
      filters: { ...state.filters, ...filters },
      recipes: [],
      page: 1,
      hasMore: true,
    })),
    clearFilters: () => update(state => ({
      ...state,
      filters: {},
      recipes: [],
      page: 1,
      hasMore: true,
    })),
    fetchRecipes: async () => {
      update(state => ({ ...state, loading: true }));
      try {
        const params = new URLSearchParams();
        // TODO: Add filters to params
        const response = await fetch(`/api/recipes?${params.toString()}`);
        const data = await response.json();
        set({
          recipes: data.recipes || [],
          loading: false,
          loadingMore: false,
          hasMore: data.hasMore || false,
          page: 1,
          filters: {},
        });
      } catch (error) {
        update(state => ({ ...state, loading: false }));
        console.error('Error fetching recipes:', error);
      }
    },
    fetchMore: async () => {
      update(state => {
        if (state.loadingMore || !state.hasMore) return state;
        return { ...state, loadingMore: true };
      });

      try {
        const nextPage = 1; // TODO: implement pagination
        const response = await fetch(`/api/recipes?page=${nextPage}`);
        const data = await response.json();
        update(state => ({
          ...state,
          recipes: [...state.recipes, ...(data.recipes || [])],
          loadingMore: false,
          hasMore: data.hasMore || false,
          page: state.page + 1,
        }));
      } catch (error) {
        update(state => ({ ...state, loadingMore: false }));
        console.error('Error fetching more recipes:', error);
      }
    },
    clearError: () => update(state => ({ ...state, error: undefined })),
  };

export const recipesStore = createRecipesStore();

// Derived stores
export const recipes = derived(recipesStore, $store => $store.recipes);
export const loading = derived(recipesStore, $store => $store.loading);
export const loadingMore = derived(recipesStore, $store => $store.loadingMore);
export const hasMore = derived(recipesStore, $store => $store.hasMore);
export const filters = derived(recipesStore, $store => $store.filters);