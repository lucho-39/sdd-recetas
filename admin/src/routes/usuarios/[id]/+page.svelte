<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { IconArrowLeft as Back } from '@tabler/icons-svelte';
	import { adminFetch, formatDate } from '$lib/api';

	// GET /api/admin/users/{id} — UC-ADMIN-006 AC1 (panel) + AC3 (métricas).
	type Detail = {
		id: string;
		email: string;
		display_name: string;
		avatar_url?: string | null;
		role: string;
		is_active: boolean;
		is_verified: boolean;
		provider: string;
		created_at: string;
		last_login_at?: string | null;
		deactivated_at?: string | null;
		deleted_at?: string | null;
		recipes_count: number;
		recipes_public: number;
		recipes_private: number;
		recipes_deleted: number;
		favorites_count: number;
		ratings_count: number;
		ratings_average: number | null;
	};

	let user: Detail | null = null;
	let loading = true;
	let error = '';

	async function load() {
		loading = true;
		error = '';
		try {
			user = await adminFetch<Detail>(`/users/${$page.params.id}`);
		} catch (err) {
			error = err instanceof Error ? err.message : 'No se pudo cargar el usuario';
		} finally {
			loading = false;
		}
	}

	// UC-ADMIN-006 AC4: three states, three colours — and "deleted" is not
	// the same as "inactive" even though both carry is_active=false.
	function accountState(d: Detail) {
		if (d.deleted_at)
			return { label: 'Eliminado (GDPR)', cls: 'bg-destructive/10 text-destructive' };
		if (!d.is_active) return { label: 'Inactivo', cls: 'bg-warning/10 text-warning' };
		return { label: 'Activo', cls: 'bg-success/10 text-success' };
	}

	// UC-ADMIN-006 AC3: the breakdown is its own rows, not a tooltip — an
	// admin auditing an account wants to see public vs private vs deleted
	// at a glance, not derive them from one total.
	function metrics(d: Detail) {
		return [
			{ label: 'Recetas', value: String(d.recipes_count) },
			{ label: 'Públicas', value: String(d.recipes_public) },
			{ label: 'Privadas', value: String(d.recipes_private) },
			{ label: 'Borradas', value: String(d.recipes_deleted) },
			{ label: 'Favoritos', value: String(d.favorites_count) },
			{ label: 'Calificaciones dadas', value: String(d.ratings_count) },
			{
				label: 'Promedio dado',
				value: d.ratings_average === null ? '—' : d.ratings_average.toFixed(1)
			}
		];
	}

	function facts(d: Detail) {
		return [
			{ label: 'Email', value: d.email },
			{ label: 'Proveedor', value: d.provider },
			{ label: 'Rol', value: d.role },
			{ label: 'Verificada', value: d.is_verified ? 'Sí' : 'No' },
			{ label: 'Alta', value: formatDate(d.created_at) },
			{ label: 'Último login', value: d.last_login_at ? formatDate(d.last_login_at) : '—' },
			{ label: 'Desactivada', value: d.deactivated_at ? formatDate(d.deactivated_at) : '—' }
		];
	}

	onMount(load);
</script>

<svelte:head>
	<title>{user?.display_name ?? 'Usuario'} — Recetario Admin</title>
</svelte:head>

<div class="space-y-6">
	<a href="/usuarios" class="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground">
		<Back class="h-4 w-4" aria-hidden="true" />
		Volver a usuarios
	</a>

	{#if error}<p class="text-sm text-destructive" role="alert">{error}</p>{/if}

	{#if loading}
		<p class="text-muted-foreground">Cargando…</p>
	{:else if user}
		<!-- UC-ADMIN-006 AC1: the basic panel, AC4's badge alongside it. -->
		<div class="flex flex-wrap items-center gap-4">
			{#if user.avatar_url}
				<img
					src={user.avatar_url}
					alt=""
					class="h-14 w-14 rounded-full object-cover"
					referrerpolicy="no-referrer"
				/>
			{:else}
				<span
					class="flex h-14 w-14 items-center justify-center rounded-full bg-muted text-lg font-medium text-muted-foreground"
					aria-hidden="true"
				>
					{user.display_name.slice(0, 1).toUpperCase()}
				</span>
			{/if}
			<div class="min-w-0">
				<div class="flex flex-wrap items-center gap-2">
					<h1 class="font-playfair text-2xl font-medium text-foreground">
						{user.display_name}
					</h1>
					<span class="badge {accountState(user).cls}">{accountState(user).label}</span>
					<span class="badge bg-muted text-muted-foreground">{user.role}</span>
				</div>
				<p class="truncate text-muted-foreground">{user.email}</p>
			</div>
		</div>

		<div class="grid gap-4 md:grid-cols-2">
			<section class="card p-4">
				<h2 class="mb-3 text-sm font-medium text-muted-foreground">Cuenta</h2>
				<dl class="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
					{#each facts(user) as fact (fact.label)}
						<dt class="text-muted-foreground">{fact.label}</dt>
						<dd class="text-foreground">{fact.value}</dd>
					{/each}
				</dl>
			</section>

			<section class="card p-4">
				<h2 class="mb-3 text-sm font-medium text-muted-foreground">Actividad</h2>
				<dl class="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
					{#each metrics(user) as metric (metric.label)}
						<dt class="text-muted-foreground">{metric.label}</dt>
						<dd class="text-right font-medium text-foreground">{metric.value}</dd>
					{/each}
				</dl>
			</section>
		</div>
	{/if}
</div>
