import { writable, derived } from 'svelte/store';
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
      if (typeof window !== 'undefined') {
        const token = localStorage.getItem('admin_access_token');
        if (token) {
          try {
            const response = await fetch('/api/admin/auth/me', {
              headers: { Authorization: `Bearer ${token}` },
            });
            if (response.ok) {
              const user = await response.json();
              update(state => ({ ...state, user, accessToken: token, isAuthenticated: true }));
            } else {
              localStorage.removeItem('admin_access_token');
            }
          } catch (error) {
            localStorage.removeItem('admin_access_token');
          }
        }
        update(state => ({ ...state, loading: false }));
      },
    login: async (email: string, password: string) => {
      const response = await fetch('/api/admin/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Credenciales inválidas');
      }

      const data = await response.json();
      localStorage.setItem('admin_access_token', data.access_token);

      const userResponse = await fetch('/api/admin/auth/me', {
        headers: { Authorization: `Bearer ${data.access_token}` },
      });
      const user = await userResponse.json();

      update(state => ({
        ...state,
        user,
        accessToken: data.access_token,
        isAuthenticated: true,
      });

      return data;
    },
    logout: async () => {
      try {
        await fetch('/api/admin/auth/logout', { method: 'POST' });
      } catch (error) {
        console.error('Logout error:', error);
      }
      localStorage.removeItem('admin_access_token');
      set({ user: null, accessToken: null, isAuthenticated: false, loading: false });
    },
    setUser: (user: User | null) => update(state => ({ ...state, user, isAuthenticated: !!user })),
    setTokens: (accessToken: string | null) => update(state => ({
      ...state,
      accessToken,
      isAuthenticated: !!accessToken,
    })),
  };

export const auth = createAuthStore();

export const isAuthenticated = derived(auth, $auth => $auth.isAuthenticated);
export const currentUser = derived(auth, $auth => $auth.user);
export const accessToken = derived(auth, $auth => $auth.accessToken);
export const authLoading = derived(auth, $auth => $auth.loading);