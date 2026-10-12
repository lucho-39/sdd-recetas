<script lang="ts">
	import { onMount } from 'svelte';
	import {
		IconTrashFilled as Erase,
		IconUserCheck as Activate,
		IconUserOff as Deactivate
	} from '@tabler/icons-svelte';
	import { adminFetch, formatDate } from '$lib/api';

	type UserRow = {
		id: string;
		email: string;
		display_name: string;
		role: string;
		is_active: boolean;
		is_verified: boolean;
		provider: string;
		created_at: string;
		last_login_at?: string | null;
		deactivated_at?: string | null;
		deleted_at?: string | null;
		recipes_count: number;
		favorites_count: number;
		ratings_count: number;
	};

	// UC-ADMIN-005 AC1: 20 per page.
	let items: UserRow[] = [];
	let total = 0;
	let page = 1;
	const limit = 20;

	let search = '';
	let accountStatus = '';
	let provider = '';
	let roleFilter = '';
	let createdFrom = '';
	let createdTo = '';
	let sort = 'created_at';

	let loading = true;
	let error = '';

	$: pages = Math.max(1, Math.ceil(total / limit));

	function buildQuery(): string {
		const params = new URLSearchParams({ page: String(page), limit: String(limit), sort });
		if (search) params.set('search', search);
		if (accountStatus) params.set('status', accountStatus);
		if (provider) params.set('provider', provider);
		if (roleFilter) params.set('role', roleFilter);
		if (createdFrom) params.set('created_from', createdFrom);
		if (createdTo) params.set('created_to', createdTo);
		return params.toString();
	}

	async function load() {
		loading = true;
		error = '';
		try {
			const data = await adminFetch<{ items: UserRow[]; total: number }>(
				`/users?${buildQuery()}`
			);
			items = data.items;
			total = data.total;
		} catch (err) {
			error = err instanceof Error ? err.message : 'No se pudieron cargar los usuarios';
		} finally {
			loading = false;
		}
	}

	function apply() {
		page = 1;
		load();
	}

	function go(delta: number) {
		const next = page + delta;
		if (next < 1 || next > pages) return;
		page = next;
		load();
	}

	// UC-ADMIN-005 AC3: live search, one request 300ms after the last keystroke.
	let searchTimer: ReturnType<typeof setTimeout> | undefined;
	function onSearchInput() {
		clearTimeout(searchTimer);
		searchTimer = setTimeout(() => {
			page = 1;
			load();
		}, 300);
	}

	// UC-ADMIN-005 AC4: four keys, fixed direction each — a click switches the
	// sort rather than toggling it, because the API has no order parameter.
	function setSort(key: string) {
		if (sort === key) return;
		sort = key;
		apply();
	}

	async function toggleActive(row: UserRow) {
		await adminFetch(`/users/${row.id}/${row.is_active ? 'deactivate' : 'activate'}`, {
			method: 'POST'
		});
		await load();
	}

	async function changeRole(row: UserRow, next: string) {
		try {
			await adminFetch(`/users/${row.id}/role`, {
				method: 'PATCH',
				body: JSON.stringify({ role: next })
			});
		} catch (err) {
			error = err instanceof Error ? err.message : 'No se pudo cambiar el rol';
		}
		await load();
	}

	async function gdprErase(row: UserRow) {
		if (
			!confirm(
				`¿Anonimizar los datos de "${row.display_name}"? Estaacción no se puede deshacer.`
			)
		)
			return;
		const deleteRecipes = confirm('¿Eliminar también sus recetas? (Cancelar = conservarlas)');
		await adminFetch(`/users/${row.id}/gdpr-erase`, {
			method: 'POST',
			body: JSON.stringify({ delete_recipes: deleteRecipes })
		});
		await load();
	}

	function badge(row: UserRow) {
		if (row.deleted_at) return { label: 'Eliminado', cls: 'bg-destructive/10 text-destructive' };
		if (!row.is_active) return { label: 'Inactivo', cls: 'bg-warning/10 text-warning' };
		return { label: 'Activo', cls: 'bg-success/10 text-success' };
	}

	onMount(load);
</script>

<svelte:head><title>Usuarios — Recetario Admin</title></svelte:head>

<div class="space-y-6">
	<div>
		<h1 class="font-playfair text-2xl font-medium text-foreground">Usuarios</h1>
		<p class="mt-1 text-muted-foreground">{total} cuentas registradas</p>
	</div>

	<!-- UC-ADMIN-005 AC2: every filter the spec names, reset to page 1 on change. -->
	<div class="flex flex-wrap items-end gap-3">
		<label class="block grow">
			<span class="mb-1 block text-xs text-muted-foreground">Buscar</span>
			<input
				type="search"
				class="input-base"
				placeholder="Email o nombre…"
				bind:value={search}
				on:input={onSearchInput}
			/>
		</label>
		<label class="block">
			<span class="mb-1 block text-xs text-muted-foreground">Estado</span>
			<select class="input-base" bind:value={accountStatus} on:change={apply}>
				<option value="">Todos</option>
				<option value="active">Activos</option>
				<option value="inactive">Inactivos</option>
				<option value="deleted">Eliminados</option>
			</select>
		</label>
		<label class="block">
			<span class="mb-1 block text-xs text-muted-foreground">Proveedor</span>
			<select class="input-base" bind:value={provider} on:change={apply}>
				<option value="">Todos</option>
				<option value="email">Email</option>
				<option value="google">Google</option>
				<option value="github">GitHub</option>
			</select>
		</label>
		<label class="block">
			<span class="mb-1 block text-xs text-muted-foreground">Rol</span>
			<select class="input-base" bind:value={roleFilter} on:change={apply}>
				<option value="">Todos</option>
				<option value="user">user</option>
				<option value="admin">admin</option>
			</select>
		</label>
		<label class="block">
			<span class="mb-1 block text-xs text-muted-foreground">Alta desde</span>
			<input type="date" class="input-base" bind:value={createdFrom} on:change={apply} />
		</label>
		<label class="block">
			<span class="mb-1 block text-xs text-muted-foreground">Alta hasta</span>
			<input type="date" class="input-base" bind:value={createdTo} on:change={apply} />
		</label>
	</div>

	{#if error}<p class="text-sm text-destructive" role="alert">{error}</p>{/if}

	<div class="card overflow-x-auto">
		<table class="w-full text-sm">
			<thead class="border-b border-border text-left text-muted-foreground">
				<tr>
					<th class="p-3">
						<button type="button" class="btn btn-ghost btn-sm -mx-2 px-2" on:click={() => setSort('email')}>
							Email{#if sort === 'email'}<span aria-hidden="true"> ↓</span>{/if}
						</button>
					</th>
					<th class="p-3">Nombre</th>
					<th class="p-3">Proveedor</th>
					<th class="p-3">Estado</th>
					<th class="p-3">Rol</th>
					<th class="p-3">
						<button
							type="button"
							class="btn btn-ghost btn-sm -mx-2 px-2"
							on:click={() => setSort('created_at')}
						>
							Alta{#if sort === 'created_at'}<span aria-hidden="true"> ↓</span>{/if}
						</button>
					</th>
					<th class="p-3">
						<button
							type="button"
							class="btn btn-ghost btn-sm -mx-2 px-2"
							on:click={() => setSort('last_login_at')}
						>
							Último login{#if sort === 'last_login_at'}<span aria-hidden="true"> ↓</span>{/if}
						</button>
					</th>
					<th class="p-3 text-right">
						<button
							type="button"
							class="btn btn-ghost btn-sm -mx-2 px-2"
							on:click={() => setSort('recipes_count')}
						>
							Recetas{#if sort === 'recipes_count'}<span aria-hidden="true"> ↓</span>{/if}
						</button>
					</th>
					<th class="p-3 text-right">Favoritos</th>
					<th class="p-3 text-right">Calificaciones</th>
					<th class="p-3 text-right">Acciones</th>
				</tr>
			</thead>
			<tbody>
				{#each items as row (row.id)}
					<tr class="border-b border-border last:border-0">
						<td class="p-3">{row.email}</td>
						<td class="p-3 font-medium text-foreground">{row.display_name}</td>
						<td class="p-3">
							<span class="badge bg-muted text-muted-foreground">{row.provider}</span>
						</td>
						<td class="p-3">
							<span class="badge {badge(row).cls}">{badge(row).label}</span>
						</td>
						<td class="p-3">
							<select
								value={row.role}
								on:change={(e) => changeRole(row, e.currentTarget.value)}
								class="input-base py-1"
								aria-label="Rol de {row.display_name}"
							>
								<option value="user">user</option>
								<option value="admin">admin</option>
							</select>
						</td>
						<td class="p-3 whitespace-nowrap text-muted-foreground">{formatDate(row.created_at)}</td>
						<td class="p-3 whitespace-nowrap text-muted-foreground">
							{row.last_login_at ? formatDate(row.last_login_at) : '—'}
						</td>
						<td class="p-3 text-right">
							<button
								type="button"
								class="btn btn-ghost btn-sm"
								title={row.is_active ? 'Desactivar' : 'Activar'}
								aria-label="{row.is_active ? 'Desactivar' : 'Activar'} a {row.display_name}"
								on:click={() => toggleActive(row)}
							>
								{#if row.is_active}
									<Deactivate class="h-4 w-4" aria-hidden="true" />
								{:else}
									<Activate class="h-4 w-4" aria-hidden="true" />
								{/if}
							</button>
							<button
								type="button"
								class="btn btn-ghost btn-sm text-destructive"
								title="Borrar datos (GDPR)"
								aria-label="Borrar los datos de {row.display_name}"
								on:click={() => gdprErase(row)}
							>
								<Erase class="h-4 w-4" aria-hidden="true" />
							</button>
						</td>
					</tr>
				{/each}
				{#if !loading && items.length === 0}
					<tr><td class="p-6 text-center text-muted-foreground" colspan="11">Sin resultados</td></tr>
				{/if}
			</tbody>
		</table>
	</div>

	<div class="flex items-center justify-between">
		<span class="text-sm text-muted-foreground">{total} usuarios</span>
		<div class="flex items-center gap-2">
			<button type="button" class="btn btn-outline btn-sm" on:click={() => go(-1)} disabled={page <= 1}>
				Anterior
			</button>
			<span class="text-sm text-muted-foreground">{page} / {pages}</span>
			<button
				type="button"
				class="btn btn-outline btn-sm"
				on:click={() => go(1)}
				disabled={page >= pages}
			>
				Siguiente
			</button>
		</div>
	</div>
</div>
