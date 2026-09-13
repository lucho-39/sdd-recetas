import { writable, get } from 'svelte/store';
import { browser } from '$app/environment';
import { io, type Socket } from 'socket.io-client';
import { auth } from '$lib/stores/auth';
import type { AppNotification } from '$lib/types';

interface NotificationsState {
	items: AppNotification[];
	unreadCount: number;
	loading: boolean;
	connected: boolean;
}

const MAX_ITEMS = 50;

function createNotificationsStore() {
	const { subscribe, set, update } = writable<NotificationsState>({
		items: [],
		unreadCount: 0,
		loading: false,
		connected: false
	});

	let socket: Socket | null = null;
	let boundToken: string | null = null;
	let started = false;

	function token(): string | null {
		return get(auth).accessToken;
	}

	function connect(accessToken: string) {
		if (!browser || socket) return;
		socket = io({
			auth: { token: accessToken },
			transports: ['websocket', 'polling']
		});
		socket.on('connect', () => update((s) => ({ ...s, connected: true })));
		socket.on('disconnect', () => update((s) => ({ ...s, connected: false })));
		socket.on('notification', (notification: AppNotification) => {
			update((s) => ({
				...s,
				items: [notification, ...s.items].slice(0, MAX_ITEMS),
				unreadCount: s.unreadCount + (notification.is_read ? 0 : 1)
			}));
		});
	}

	function disconnect() {
		socket?.disconnect();
		socket = null;
		update((s) => ({ ...s, connected: false }));
	}

	async function load() {
		const accessToken = token();
		if (!accessToken) return;
		update((s) => ({ ...s, loading: true }));
		try {
			const res = await fetch('/api/v1/notifications?limit=20', {
				headers: { Authorization: `Bearer ${accessToken}` }
			});
			if (res.ok) {
				const body = await res.json();
				update((s) => ({
					...s,
					items: body.items ?? [],
					unreadCount: body.unread_count ?? 0,
					loading: false
				}));
			} else {
				update((s) => ({ ...s, loading: false }));
			}
		} catch {
			update((s) => ({ ...s, loading: false }));
		}
	}

	async function markRead(id: string) {
		const accessToken = token();
		if (!accessToken) return;
		update((s) => {
			const target = s.items.find((n) => n.id === id);
			return {
				...s,
				items: s.items.map((n) => (n.id === id ? { ...n, is_read: true } : n)),
				unreadCount: target && !target.is_read ? Math.max(0, s.unreadCount - 1) : s.unreadCount
			};
		});
		await fetch(`/api/v1/notifications/${id}/read`, {
			method: 'POST',
			headers: { Authorization: `Bearer ${accessToken}` }
		}).catch(() => {});
	}

	async function markAllRead() {
		const accessToken = token();
		if (!accessToken) return;
		update((s) => ({ ...s, items: s.items.map((n) => ({ ...n, is_read: true })), unreadCount: 0 }));
		await fetch('/api/v1/notifications/read-all', {
			method: 'POST',
			headers: { Authorization: `Bearer ${accessToken}` }
		}).catch(() => {});
	}

	async function remove(id: string) {
		const accessToken = token();
		if (!accessToken) return;
		update((s) => {
			const target = s.items.find((n) => n.id === id);
			return {
				...s,
				items: s.items.filter((n) => n.id !== id),
				unreadCount: target && !target.is_read ? Math.max(0, s.unreadCount - 1) : s.unreadCount
			};
		});
		await fetch(`/api/v1/notifications/${id}`, {
			method: 'DELETE',
			headers: { Authorization: `Bearer ${accessToken}` }
		}).catch(() => {});
	}

	async function removeAll() {
		const accessToken = token();
		if (!accessToken) return;
		update((s) => ({ ...s, items: [], unreadCount: 0 }));
		await fetch('/api/v1/notifications', {
			method: 'DELETE',
			headers: { Authorization: `Bearer ${accessToken}` }
		}).catch(() => {});
	}

	function start() {
		if (!browser || started) return;
		started = true;
		auth.subscribe((state) => {
			if (state.isAuthenticated && state.accessToken) {
				if (state.accessToken !== boundToken) {
					boundToken = state.accessToken;
					disconnect();
					connect(state.accessToken);
					load();
				}
			} else if (boundToken) {
				boundToken = null;
				disconnect();
				set({ items: [], unreadCount: 0, loading: false, connected: false });
			}
		});
	}

	return { subscribe, start, load, markRead, markAllRead, remove, removeAll };
}

export const notifications = createNotificationsStore();
