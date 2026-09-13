<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { IconUserFilled as User, IconDeviceFloppy as Save, IconLockFilled as Lock, IconAlertTriangleFilled as AlertTriangle, IconTrashFilled as Trash, IconCircleCheckFilled as Check } from '@tabler/icons-svelte';
	import { auth } from '$lib/stores/auth';
	import { notifications } from '$lib/stores/notifications';
	import AuthorAvatar from '$components/common/AuthorAvatar.svelte';
	import RecipeGrid from '$components/recipe/RecipeGrid.svelte';
	import type { NotificationPreferences } from '$lib/types';

	let displayName = '';
	let avatarUrl = '';
	let savingProfile = false;
	let profileMessage = '';
	let profileError = '';

	let myRecipes: any[] = [];
	let loadingRecipes = true;

	let currentPassword = '';
	let newPassword = '';
	let changingPassword = false;
	let passwordMessage = '';
	let passwordError = '';

	let prefs: NotificationPreferences = {
		in_app_enabled: true,
		email_enabled: false,
		push_enabled: false,
		favorites_enabled: true,
		ratings_enabled: true
	};
	let savingPrefs = false;
	let prefsMessage = '';
	let prefsError = '';
	let pushPermission: NotificationPermission | 'unsupported' = 'default';

	const memberSince = (created?: string) =>
		created
			? new Intl.DateTimeFormat('es-AR', { year: 'numeric', month: 'long' }).format(new Date(created))
			: '—';

	function authHeaders(): HeadersInit {
		return { Authorization: `Bearer ${$auth.accessToken}` };
	}

	async function loadMyRecipes() {
		loadingRecipes = true;
		try {
			const res = await fetch('/api/v1/users/me/recipes?limit=50', { headers: authHeaders() });
			if (res.ok) myRecipes = (await res.json()).recipes ?? [];
		} finally {
			loadingRecipes = false;
		}
	}

	async function saveProfile() {
		savingProfile = true;
		profileMessage = '';
		profileError = '';
		try {
			const res = await fetch('/api/v1/users/me', {
				method: 'PATCH',
				headers: { 'Content-Type': 'application/json', ...authHeaders() },
				body: JSON.stringify({ display_name: displayName, avatar_url: avatarUrl || null })
			});
			if (!res.ok) throw new Error('No se pudo guardar el perfil');
			const updated = await res.json();
			auth.setUser(updated);
			profileMessage = 'Perfil actualizado';
		} catch (err) {
			profileError = err instanceof Error ? err.message : 'Error al guardar';
		} finally {
			savingProfile = false;
		}
	}

	async function changePassword() {
		changingPassword = true;
		passwordMessage = '';
		passwordError = '';
		try {
			const res = await fetch('/api/v1/auth/change-password', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json', ...authHeaders() },
				body: JSON.stringify({ current_password: currentPassword, new_password: newPassword })
			});
			if (!res.ok) {
				const body = await res.json().catch(() => ({}));
				throw new Error(body.detail || 'No se pudo cambiar la contraseña');
			}
			currentPassword = '';
			newPassword = '';
			passwordMessage = 'Contraseña actualizada';
		} catch (err) {
			passwordError = err instanceof Error ? err.message : 'Error al cambiar la contraseña';
		} finally {
			changingPassword = false;
		}
	}

	async function loadPrefs() {
		prefs = await notifications.loadPreferences();
	}

	async function updatePref(key: keyof NotificationPreferences, value: boolean) {
		savingPrefs = true;
		prefsMessage = '';
		prefsError = '';
		try {
			prefs = await notifications.savePreferences({ [key]: value });
			prefsMessage = 'Preferencias guardadas';
		} catch (err) {
			prefsError = err instanceof Error ? err.message : 'No se pudieron guardar las preferencias';
		} finally {
			savingPrefs = false;
		}
	}

	async function enablePush() {
		if (typeof Notification === 'undefined') {
			prefsError = 'Tu navegador no soporta notificaciones.';
			return;
		}
		const permission = await Notification.requestPermission();
		pushPermission = permission;
		if (permission === 'granted') {
			await updatePref('push_enabled', true);
		} else {
			prefsError = 'Permiso de notificaciones denegado.';
		}
	}

	onMount(async () => {
		if (!$auth.isAuthenticated) {
			await auth.init();
		}
		if (!$auth.isAuthenticated) {
			await goto('/login');
			return;
		}
		displayName = $auth.user?.display_name ?? '';
		avatarUrl = $auth.user?.avatar_url ?? '';
		if (typeof Notification !== 'undefined') pushPermission = Notification.permission;
		await Promise.all([loadMyRecipes(), loadPrefs()]);
	});
</script>

<svelte:head>
	<title>Mi perfil — Recetario IA</title>
</svelte:head>

<div class="container py-8">
	<h1 class="mb-6 font-playfair text-2xl font-medium text-foreground md:text-3xl">Mi perfil</h1>

	{#if $auth.user}
		<!-- Header -->
		<section class="card mb-8 p-6">
			<div class="flex flex-col gap-6 sm:flex-row sm:items-center">
				<AuthorAvatar
					author={{ id: $auth.user.id, display_name: $auth.user.display_name, avatar_url: $auth.user.avatar_url }}
					size="lg"
				/>
				<div class="flex-1">
					<p class="text-sm text-muted-foreground">Miembro desde {memberSince($auth.user.created_at)}</p>
					<p class="text-xs text-muted-foreground">{$auth.user.email}</p>
				</div>
			</div>

			<div class="mt-6 grid gap-4 sm:grid-cols-2">
				<div>
					<label for="display_name" class="label">Nombre</label>
					<input id="display_name" type="text" bind:value={displayName} class="input-base" maxlength="100" />
				</div>
				<div>
					<label for="avatar_url" class="label">URL de avatar</label>
					<input id="avatar_url" type="url" bind:value={avatarUrl} class="input-base" placeholder="https://…" />
				</div>
			</div>

			<div class="mt-4 flex items-center gap-3">
				<button type="button" class="btn btn-primary btn-sm" on:click={saveProfile} disabled={savingProfile}>
					<Save class="h-4 w-4" aria-hidden="true" /> Guardar cambios
				</button>
				{#if profileMessage}
					<span class="inline-flex items-center gap-1 text-sm text-success"><Check class="h-4 w-4" aria-hidden="true" />{profileMessage}</span>
				{/if}
				{#if profileError}
					<span class="text-sm text-destructive" role="alert">{profileError}</span>
				{/if}
			</div>
		</section>

		<!-- My recipes -->
		<section class="mb-8" aria-labelledby="my-recipes-heading">
			<h2 id="my-recipes-heading" class="mb-4 text-xl font-medium text-foreground">Mis recetas</h2>
			<RecipeGrid
				recipes={myRecipes}
				loading={loadingRecipes}
				loadingMore={false}
				hasMore={false}
				emptyVariant="recipes"
				onLoadMore={() => {}}
			/>
		</section>

		<!-- Notifications -->
		<section class="card mb-8 p-6" aria-labelledby="notifications-heading">
			<h2 id="notifications-heading" class="mb-1 text-xl font-medium text-foreground">Notificaciones</h2>
			<p class="mb-4 text-sm text-muted-foreground">Elegí qué querés recibir y por qué canal.</p>

			{#if prefsError}<p class="mb-3 text-sm text-destructive" role="alert">{prefsError}</p>{/if}
			{#if prefsMessage}<p class="mb-3 text-sm text-success">{prefsMessage}</p>{/if}

			<fieldset class="mb-5">
				<legend class="mb-2 text-sm font-medium text-foreground">Eventos</legend>
				<div class="space-y-2">
					<label class="flex items-center gap-2 text-sm">
						<input type="checkbox" class="h-4 w-4" checked={prefs.favorites_enabled} disabled={savingPrefs} on:change={(e) => updatePref('favorites_enabled', e.currentTarget.checked)} />
						Cuando guardan mis recetas
					</label>
					<label class="flex items-center gap-2 text-sm">
						<input type="checkbox" class="h-4 w-4" checked={prefs.ratings_enabled} disabled={savingPrefs} on:change={(e) => updatePref('ratings_enabled', e.currentTarget.checked)} />
						Cuando califican mis recetas
					</label>
				</div>
			</fieldset>

			<fieldset>
				<legend class="mb-2 text-sm font-medium text-foreground">Canales</legend>
				<div class="space-y-2">
					<label class="flex items-center gap-2 text-sm">
						<input type="checkbox" class="h-4 w-4" checked={prefs.in_app_enabled} disabled={savingPrefs} on:change={(e) => updatePref('in_app_enabled', e.currentTarget.checked)} />
						En la app (campanita)
					</label>
					<label class="flex items-center gap-2 text-sm">
						<input type="checkbox" class="h-4 w-4" checked={prefs.email_enabled} disabled={savingPrefs} on:change={(e) => updatePref('email_enabled', e.currentTarget.checked)} />
						Email
					</label>
					<div class="flex flex-wrap items-center gap-3">
						<label class="flex items-center gap-2 text-sm">
							<input type="checkbox" class="h-4 w-4" checked={prefs.push_enabled} disabled={savingPrefs} on:change={(e) => updatePref('push_enabled', e.currentTarget.checked)} />
							Notificaciones del navegador
						</label>
						{#if pushPermission !== 'granted'}
							<button type="button" class="btn btn-outline btn-sm" on:click={enablePush} disabled={savingPrefs}>Activar</button>
						{:else}
							<span class="text-xs text-muted-foreground">Permiso concedido</span>
						{/if}
					</div>
					{#if pushPermission === 'denied'}
						<p class="text-xs text-destructive">Bloqueaste las notificaciones; habilitalas en la configuración del sitio.</p>
					{/if}
				</div>
			</fieldset>
		</section>

		<!-- Account actions -->
		<section class="card p-6" aria-labelledby="account-heading">
			<h2 id="account-heading" class="mb-4 text-xl font-medium text-foreground">Cuenta</h2>

			<div class="space-y-4">
				<div>
					<h3 class="mb-2 flex items-center gap-2 text-sm font-medium text-foreground"><Lock class="h-4 w-4" aria-hidden="true" /> Cambiar contraseña</h3>
					<div class="grid gap-3 sm:grid-cols-2">
						<input type="password" bind:value={currentPassword} class="input-base" placeholder="Contraseña actual" autocomplete="current-password" />
						<input type="password" bind:value={newPassword} class="input-base" placeholder="Nueva contraseña" autocomplete="new-password" />
					</div>
					<div class="mt-3 flex items-center gap-3">
						<button type="button" class="btn btn-outline btn-sm" on:click={changePassword} disabled={changingPassword || !currentPassword || newPassword.length < 8}>
							Actualizar contraseña
						</button>
						{#if passwordMessage}<span class="text-sm text-success">{passwordMessage}</span>{/if}
						{#if passwordError}<span class="text-sm text-destructive" role="alert">{passwordError}</span>{/if}
					</div>
				</div>

				<hr class="border-border" />

				<div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
					<div class="flex items-start gap-2 text-sm text-muted-foreground">
						<AlertTriangle class="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
						<p>Darte de baja o eliminar la cuenta estará disponible próximamente (<strong>v2</strong>).</p>
					</div>
					<div class="flex gap-2">
						<button type="button" class="btn btn-outline btn-sm" disabled>Darme de baja</button>
						<button type="button" class="btn btn-destructive btn-sm" disabled>
							<Trash class="h-4 w-4" aria-hidden="true" /> Eliminar cuenta
						</button>
					</div>
				</div>
			</div>
		</section>
	{/if}
</div>
