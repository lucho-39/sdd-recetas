import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://backend:8000';

/** RB-17: /u/<display_name_slug> is the short public handle. */
export const load: PageServerLoad = async ({ params, fetch }) => {
	const profileResponse = await fetch(`${API_BASE}/api/v1/users/${params.slug}`);

	if (profileResponse.status === 404) {
		throw error(404, 'Usuario no encontrado');
	}
	if (!profileResponse.ok) {
		throw error(502, 'No se pudo cargar el perfil');
	}

	const profile = await profileResponse.json();

	const recipesResponse = await fetch(`${API_BASE}/api/v1/users/${params.slug}/recipes?limit=24`);
	const recipesData = recipesResponse.ok ? await recipesResponse.json() : { recipes: [], total: 0 };

	return { profile, recipes: recipesData.recipes ?? [], total: recipesData.total ?? 0 };
};
