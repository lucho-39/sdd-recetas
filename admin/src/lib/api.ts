import { get } from 'svelte/store';
import { auth } from '$lib/stores/auth';

const TOKEN_KEY = 'admin_access_token';

let refreshing: Promise<string | null> | null = null;

/** Exchange the HttpOnly refresh cookie for a new access token (single-flight). */
function refreshAccessToken(): Promise<string | null> {
	if (!refreshing) {
		refreshing = (async () => {
			try {
				const res = await fetch('/api/v1/auth/refresh', {
					method: 'POST',
					credentials: 'include'
				});
				if (!res.ok) return null;
				const data = (await res.json()) as { access_token: string };
				localStorage.setItem(TOKEN_KEY, data.access_token);
				auth.setTokens(data.access_token);
				return data.access_token;
			} catch {
				return null;
			} finally {
				refreshing = null;
			}
		})();
	}
	return refreshing;
}

async function call(path: string, options: RequestInit): Promise<Response> {
	const { accessToken } = get(auth);
	return fetch(`/api/admin${path}`, {
		...options,
		headers: {
			'Content-Type': 'application/json',
			...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
			...(options.headers ?? {})
		}
	});
}

/** Authenticated fetch against the admin API (/api/admin). */
export async function adminFetch<T = unknown>(
	path: string,
	options: RequestInit = {}
): Promise<T> {
	let response = await call(path, options);

	if (response.status === 401) {
		const fresh = await refreshAccessToken();
		if (fresh) {
			response = await call(path, options);
		} else {
			await auth.logout();
		}
	}

	if (!response.ok) {
		const body = await response.json().catch(() => ({}));
		throw new Error((body as { detail?: string }).detail ?? `API ${response.status}`);
	}

	if (response.status === 204) return null as T;
	return (await response.json()) as T;
}

export { refreshAccessToken };

export function formatDate(value?: string | null): string {
	if (!value) return '—';
	return new Intl.DateTimeFormat('es-AR', { dateStyle: 'medium' }).format(new Date(value));
}
