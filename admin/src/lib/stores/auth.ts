import { writable, derived } from 'svelte/store';
import type { User } from '$lib/types';

interface AuthState {
	user: User | null;
	accessToken: string | null;
	isAuthenticated: boolean;
	loading: boolean;
}

const TOKEN_KEY = 'admin_access_token';

function createAuthStore() {
	const { subscribe, set, update } = writable<AuthState>({
		user: null,
		accessToken: null,
		isAuthenticated: false,
		loading: true
	});

	async function fetchMe(token: string): Promise<User | null> {
		const response = await fetch('/api/v1/auth/me', {
			headers: { Authorization: `Bearer ${token}` }
		});
		if (!response.ok) return null;
		return (await response.json()) as User;
	}

	return {
		subscribe,
		init: async () => {
			if (typeof window === 'undefined') return;
			const token = localStorage.getItem(TOKEN_KEY);
			if (token) {
				const user = await fetchMe(token).catch(() => null);
				if (user && user.role === 'admin') {
					update((state) => ({ ...state, user, accessToken: token, isAuthenticated: true }));
				} else {
					localStorage.removeItem(TOKEN_KEY);
				}
			}
			update((state) => ({ ...state, loading: false }));
		},
		login: async (email: string, password: string) => {
			const response = await fetch('/api/v1/auth/login', {
				method: 'POST',
				headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
				body: new URLSearchParams({ username: email, password })
			});

			if (!response.ok) {
				const error = await response.json().catch(() => ({}));
				throw new Error(error.detail || 'Credenciales inválidas');
			}

			const data = await response.json();
			const user = await fetchMe(data.access_token);
			if (!user || user.role !== 'admin') {
				throw new Error('La cuenta no tiene permisos de administrador');
			}

			localStorage.setItem(TOKEN_KEY, data.access_token);
			update((state) => ({
				...state,
				user,
				accessToken: data.access_token,
				isAuthenticated: true
			}));
			return data;
		},
		logout: async () => {
			try {
				await fetch('/api/v1/auth/logout', { method: 'POST' });
			} catch (error) {
				console.error('Logout error:', error);
			}
			localStorage.removeItem(TOKEN_KEY);
			set({ user: null, accessToken: null, isAuthenticated: false, loading: false });
		}
	};
}

export const auth = createAuthStore();

export const isAuthenticated = derived(auth, ($auth) => $auth.isAuthenticated);
export const currentUser = derived(auth, ($auth) => $auth.user);
export const accessToken = derived(auth, ($auth) => $auth.accessToken);
export const authLoading = derived(auth, ($auth) => $auth.loading);
