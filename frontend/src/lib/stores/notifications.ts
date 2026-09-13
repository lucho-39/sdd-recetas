import { writable, get } from 'svelte/store';
import { browser } from '$app/environment';
import { io, type Socket } from 'socket.io-client';
import { auth } from '$lib/stores/auth';
import type { AppNotification, NotificationPreferences } from '$lib/types';

interface NotificationsState {
	items: AppNotification[];
	unreadCount: number;
	loading: boolean;
	connected: boolean;
	preferences: NotificationPreferences;
}

const MAX_ITEMS = 50;

const DEFAULT_PREFERENCES: NotificationPreferences = {
	in_app_enabled: true,
	email_enabled: false,
	push_enabled: false,
	favorites_enabled: true,
	ratings_enabled: true
};

function createNotificationsStore() {
	const { subscribe, set, update } = writable<NotificationsState>({
		items: [],
		unreadCount: 0,
		loading: false,
		connected: false,
		preferences: { ...DEFAULT_PREFERENCES }
	});

	let socket: Socket | null = null;
	let boundToken: string | null = null;
	let started = false;

	function token(): string | null {
		return get(auth).accessToken;
	}

	function showBrowserNotification(notification: AppNotification) {
		if (!browser || typeof Notification === 'undefined' || Notification.permission !== 'granted') return;
		const who = notification.actor?.display_name ?? 'Alguien';
		const title =
			notification.type === 'rating'
				? `${who} calificó tu receta`
				: `${who} guardó tu receta`;
		const body = notification.recipe_title ?? '';
		const url = notification.recipe_slug ? `/receta/${notification.recipe_slug}` : '/';

		if ('serviceWorker' in navigator) {
			navigator.serviceWorker.ready
				.then((registration) =>
					registration.showNotification(title, { body, data: { url }, tag: notification.id ?? undefined })
				)
				.catch(() => {});
		} else {
			// eslint-disable-next-line no-new
			new Notification(title, { body });
		}
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
			const eventInApp = notification.in_app !== false;
			update((s) => ({
				...s,
				items: eventInApp ? [notification, ...s.items].slice(0, MAX_ITEMS) : s.items,
				unreadCount:
					eventInApp && !notification.is_read ? s.unreadCount + 1 : s.unreadCount
			}));
			if (get({ subscribe }).preferences.push_enabled) {
				showBrowserNotification(notification);
			}
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

	async function loadPreferences(): Promise<NotificationPreferences> {
		const accessToken = token();
		if (!accessToken) return get({ subscribe }).preferences;
		try {
			const res = await fetch('/api/v1/users/me/notification-preferences', {
				headers: { Authorization: `Bearer ${accessToken}` }
			});
			if (res.ok) {
				const preferences = (await res.json()) as NotificationPreferences;
				update((s) => ({ ...s, preferences }));
				return preferences;
			}
		} catch {
			/* keep defaults */
		}
		return get({ subscribe }).preferences;
	}

	async function savePreferences(
		partial: Partial<NotificationPreferences>
	): Promise<NotificationPreferences> {
		const accessToken = token();
		if (!accessToken) return get({ subscribe }).preferences;
		const res = await fetch('/api/v1/users/me/notification-preferences', {
			method: 'PUT',
			headers: {
				'Content-Type': 'application/json',
				Authorization: `Bearer ${accessToken}`
			},
			body: JSON.stringify(partial)
		});
		if (!res.ok) throw new Error(`API ${res.status}`);
		const preferences = (await res.json()) as NotificationPreferences;
		update((s) => ({ ...s, preferences }));
		return preferences;
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
					loadPreferences();
				}
			} else if (boundToken) {
				boundToken = null;
				disconnect();
				set({
					items: [],
					unreadCount: 0,
					loading: false,
					connected: false,
					preferences: { ...DEFAULT_PREFERENCES }
				});
			}
		});
	}

	return {
		subscribe,
		start,
		load,
		loadPreferences,
		savePreferences,
		markRead,
		markAllRead,
		remove,
		removeAll
	};
}

export const notifications = createNotificationsStore();
