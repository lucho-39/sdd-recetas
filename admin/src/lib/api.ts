import { get } from 'svelte/store';
import { auth } from '$lib/stores/auth';

/** Authenticated fetch against the admin API (/api/admin). */
export async function adminFetch<T = unknown>(
	path: string,
	options: RequestInit = {}
): Promise<T> {
	const { accessToken } = get(auth);
	const response = await fetch(`/api/admin${path}`, {
		...options,
		headers: {
			'Content-Type': 'application/json',
			...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
			...(options.headers ?? {})
		}
	});

	if (!response.ok) {
		const body = await response.json().catch(() => ({}));
		throw new Error((body as { detail?: string }).detail ?? `API ${response.status}`);
	}

	if (response.status === 204) return null as T;
	return (await response.json()) as T;
}

export function formatDate(value?: string | null): string {
	if (!value) return '—';
	return new Intl.DateTimeFormat('es-AR', { dateStyle: 'medium' }).format(new Date(value));
}
