import type { PageServerLoad } from './$types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://backend:8000';

export const load: PageServerLoad = async ({ fetch, url }) => {
	const query = url.searchParams.get('query') ?? '';
	const category = url.searchParams.get('category') ?? '';

	const params = new URLSearchParams({ limit: '12', sort: 'recent' });
	if (query) params.set('query', query);
	if (category) params.set('category', category);

	const endpoint = `${API_BASE}/api/v1/recipes?${params.toString()}`;

	try {
		const response = await fetch(endpoint);
		if (!response.ok) {
			console.error(`[home] recipes request failed: ${response.status} ${endpoint}`);
			return { recipes: [], total: 0, query, category };
		}
		const data = await response.json();
		return {
			recipes: data.recipes ?? [],
			total: data.total ?? 0,
			query,
			category
		};
	} catch (error) {
		console.error(`[home] recipes request error: ${endpoint}`, error);
		return { recipes: [], total: 0, query, category };
	}
};
