import { writable, derived } from 'svelte/store';
import type { Recipe, RecipeFilters } from '$lib/types';

interface RecipesState {
	recipes: Recipe[];
	loading: boolean;
	loadingMore: boolean;
	hasMore: boolean;
	page: number;
	total: number;
	filters: RecipeFilters;
	error: string | null;
}

const isServer = typeof window === 'undefined';
const API_BASE = isServer
	? `${import.meta.env.VITE_API_URL ?? 'http://backend:8000'}/api/v1`
	: '/api/v1';

function buildQuery(filters: RecipeFilters, page: number, limit: number): string {
	const params = new URLSearchParams();
	params.set('page', String(page));
	params.set('limit', String(limit));
	if (filters.query) params.set('query', filters.query);
	if (filters.category) params.set('category', filters.category);
	if (filters.sort) params.set('sort', filters.sort);
	if (filters.tags && filters.tags.length) params.set('tags', filters.tags.join(','));
	if (filters.ingredients && filters.ingredients.length)
		params.set('ingredients', filters.ingredients.join(','));
	return params.toString();
}

function createRecipesStore() {
	const { subscribe, set, update } = writable<RecipesState>({
		recipes: [],
		loading: true,
		loadingMore: false,
		hasMore: true,
		page: 1,
		total: 0,
		filters: {},
		error: null
	});

	const PAGE_SIZE = 12;

	async function fetchPage(page: number, replace: boolean) {
		if (replace) update((s) => ({ ...s, loading: true, error: null }));
		else update((s) => ({ ...s, loadingMore: true }));

		try {
			const state = getState();
			const query = buildQuery(state.filters, page, PAGE_SIZE);
			const response = await fetch(`${API_BASE}/recipes?${query}`);
			if (!response.ok) {
				throw new Error(`API ${response.status}`);
			}
			const data = await response.json();
			const items: Recipe[] = data.recipes ?? [];
			update((s) => ({
				...s,
				recipes: replace ? items : [...s.recipes, ...items],
				page,
				total: data.total ?? items.length,
				hasMore: Boolean(data.has_more),
				loading: false,
				loadingMore: false,
				error: null
			}));
		} catch (error) {
			update((s) => ({
				...s,
				loading: false,
				loadingMore: false,
				hasMore: false,
				error: error instanceof Error ? error.message : 'Error al cargar recetas'
			}));
		}
	}

	let current: RecipesState;
	subscribe((s) => (current = s));
	const getState = () => current;

	return {
		subscribe,
		setFilters: (filters: Partial<RecipeFilters>) =>
			update((s) => ({ ...s, filters: { ...s.filters, ...filters } })),
		clearFilters: () => update((s) => ({ ...s, filters: {} })),
		fetchRecipes: async () => {
			update((s) => ({ ...s, recipes: [] }));
			await fetchPage(1, true);
		},
		fetchMore: async () => {
			if (getState().loadingMore || !getState().hasMore) return;
			await fetchPage(getState().page + 1, false);
		},
		reset: () =>
			set({
				recipes: [],
				loading: false,
				loadingMore: false,
				hasMore: true,
				page: 1,
				total: 0,
				filters: {},
				error: null
			})
	};
}

export const recipesStore = createRecipesStore();

export const recipes = derived(recipesStore, ($store) => $store.recipes);
export const loading = derived(recipesStore, ($store) => $store.loading);
export const loadingMore = derived(recipesStore, ($store) => $store.loadingMore);
export const hasMore = derived(recipesStore, ($store) => $store.hasMore);
export const filters = derived(recipesStore, ($store) => $store.filters);
export const recipesError = derived(recipesStore, ($store) => $store.error);
