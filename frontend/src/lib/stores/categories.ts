import { writable, derived } from 'svelte/store';
import type { Category } from '$lib/types';

interface CategoriesState {
	categories: Category[];
	loading: boolean;
}

function createCategoriesStore() {
	const { subscribe, set, update } = writable<CategoriesState>({
		categories: [],
		loading: false
	});

	return {
		subscribe,
		fetchCategories: async () => {
			update((state) => ({ ...state, loading: true }));
			try {
				const response = await fetch('/api/v1/categories');
				if (!response.ok) throw new Error(`API ${response.status}`);
				const data = await response.json();
				set({ categories: Array.isArray(data) ? data : (data.categories ?? []), loading: false });
			} catch (error) {
				console.error('Error fetching categories:', error);
				update((state) => ({ ...state, loading: false }));
			}
		}
	};
}

export const categoriesStore = createCategoriesStore();

export const categories = derived(categoriesStore, ($store) => $store.categories);
export const categoriesLoading = derived(categoriesStore, ($store) => $store.loading);
