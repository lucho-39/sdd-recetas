import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://backend:8000';

export const load: PageServerLoad = async ({ params, fetch }) => {
	const response = await fetch(`${API_BASE}/api/v1/recipes/${params.slug}`);

	if (response.status === 404) {
		throw error(404, 'Receta no encontrada');
	}
	if (!response.ok) {
		throw error(502, 'No se pudo cargar la receta');
	}

	const recipe = await response.json();
	const steps = String(recipe.instructions ?? '')
		.split('\n')
		.map((step: string) => step.trim())
		.filter(Boolean);

	return { recipe, steps };
};
