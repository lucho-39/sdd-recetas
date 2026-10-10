import { auth } from '$lib/stores/auth';

const TOKEN_KEY = 'access_token';

export function getAccessToken(): string | null {
	if (typeof window === 'undefined') return null;
	return localStorage.getItem(TOKEN_KEY);
}

let refreshing: Promise<string | null> | null = null;
let signingOut = false;

/**
 * Exchange the HttpOnly refresh cookie for a fresh access token.
 * Single-flight: concurrent 401s share one network round trip.
 */
export function refreshAccessToken(): Promise<string | null> {
	if (!refreshing) {
		refreshing = (async () => {
			try {
				const res = await fetch('/api/v1/auth/refresh', {
					method: 'POST',
					credentials: 'include',
				});
				if (!res.ok) return null;
				const data = await res.json();
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

async function endSession(): Promise<void> {
	if (signingOut) return;
	signingOut = true;
	try {
		await auth.logout();
	} finally {
		signingOut = false;
	}
}

/**
 * fetch with the stored access token attached and automatic refresh on 401.
 *
 * Pass an `Authorization` header explicitly to opt out (e.g. login), which
 * also disables the refresh-retry loop for that call.
 */
export async function apiFetch(path: string, init: RequestInit = {}): Promise<Response> {
	const headers = new Headers(init.headers);
	const managed = !headers.has('Authorization');

	if (managed) {
		const token = getAccessToken();
		if (token) headers.set('Authorization', `Bearer ${token}`);
	}

	let res = await fetch(path, { ...init, headers });

	if (res.status === 401 && managed) {
		const fresh = await refreshAccessToken();
		if (fresh) {
			headers.set('Authorization', `Bearer ${fresh}`);
			res = await fetch(path, { ...init, headers });
		} else {
			await endSession();
		}
	}

	return res;
}
