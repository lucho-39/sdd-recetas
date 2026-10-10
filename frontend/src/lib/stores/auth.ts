import { writable, derived } from 'svelte/store';
import { apiFetch } from '$lib/api';
import type { User } from '$lib/types';

interface AuthState {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  loading: boolean;
}

function createAuthStore() {
  const { subscribe, set, update } = writable<AuthState>({
    user: null,
    accessToken: null,
    isAuthenticated: false,
    loading: true,
  });

  return {
    subscribe,
    init: async () => {
      // Check for existing token in localStorage
      if (typeof window !== 'undefined') {
        const token = localStorage.getItem('access_token');
        if (token) {
          let effective = token;
          try {
            let response = await apiFetch('/api/v1/auth/me', {
              });

            if (response.status === 401) {
              // Access token expired (15 min); the refresh cookie may still be valid.
              const { refreshAccessToken } = await import('$lib/api');
              const fresh = await refreshAccessToken();
              if (fresh) {
                effective = fresh;
                response = await apiFetch('/api/v1/auth/me', {
                  });
              }
            }

            if (response.ok) {
              const user = await response.json();
              update(state => ({ ...state, user, accessToken: effective, isAuthenticated: true }));
            } else {
              localStorage.removeItem('access_token');
            }
          } catch {
            localStorage.removeItem('access_token');
          }
        }
        update(state => ({ ...state, loading: false }));
      }
    },
    login: async (email: string, password: string) => {
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ username: email, password }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Credenciales inválidas');
      }

      const data = await response.json();
      localStorage.setItem('access_token', data.access_token);
      // refresh_token is in HttpOnly cookie

      const userResponse = await apiFetch('/api/v1/auth/me', {
        });
      const user = await userResponse.json();

      update(state => ({
        ...state,
        user,
        accessToken: data.access_token,
        isAuthenticated: true,
      }));

      return data;
    },
    logout: async () => {
      try {
        await fetch('/api/v1/auth/logout', { method: 'POST' });
      } catch (error) {
        console.error('Logout error:', error);
      }
      localStorage.removeItem('access_token');
      set({ user: null, accessToken: null, isAuthenticated: false, loading: false });
    },
    setUser: (user: User | null) => update(state => ({ ...state, user, isAuthenticated: !!user })),
    setTokens: (accessToken: string | null) => update(state => ({
      ...state,
      accessToken,
      isAuthenticated: !!accessToken,
    })),
  };
}

export const auth = createAuthStore();

export const isAuthenticated = derived(auth, $auth => $auth.isAuthenticated);
export const currentUser = derived(auth, $auth => $auth.user);
export const accessToken = derived(auth, $auth => $auth.accessToken);
export const authLoading = derived(auth, $auth => $auth.loading);