<script lang="ts">
	import { onMount } from 'svelte';
	import {
		IconEye as View,
		IconRefresh as Reactivate,
		IconTrashFilled as Erase,
		IconUserCheck as Activate,
		IconUserOff as Deactivate
	} from '@tabler/icons-svelte';
	import { adminFetch, formatDate } from '$lib/api';
	import AlertDialog from '$lib/components/AlertDialog.svelte';

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

	type Dialog =
		| { kind: 'activate' | 'deactivate' | 'reactivate'; row: UserRow }
		| { kind: 'gdpr-warning' | 'gdpr-recipes'; row: UserRow };

	let dialog: Dialog | null = null;
	let deleteRecipes = false;
	let busy = false;

	async function confirm() {
		if (!dialog) return;
		const current = dialog;

		// UC-ADMIN-010 AC2: two gates, not one. The irreversible warning first;
		// only after accepting it does the recipe question appear, so "I accept
		// the risk" and "also delete the recipes" stay separate decisions.
		// Both dialogs abort on cancel or Escape — neither ever proceeds.
		if (current.kind === 'gdpr-warning') {
			dialog = { kind: 'gdpr-recipes', row: current.row };
			return;
		}

		busy = true;
		error = '';
		try {
			if (current.kind === 'gdpr-recipes') {
				await adminFetch(`/users/${current.row.id}/gdpr-erase`, {
					method: 'POST',
					body: JSON.stringify({ delete_recipes: deleteRecipes })
				});
			} else {
				await adminFetch(`/users/${current.row.id}/${current.kind}`, { method: 'POST' });
			}
			dialog = null;
			await load();
		} catch (err) {
			error = err instanceof Error ? err.message : 'La operación falló';
		} finally {
			busy = false;
		}
	}

	async function changeRole(row: UserRow, next: string) {
		error = '';
		try {
			await adminFetch(`/users/${row.id}/role`, {
				method: 'PATCH',
				body: JSON.stringify({ role: next })
			});
		} catch (err) {
			// Demoting yourself is a 403; leave the select showing what the
			// server actually stored instead of what the admin hoped for.
			error = err instanceof Error ? err.message : 'No se pudo cambiar el rol';
		}
		await load();
	}

	function openGdpr(row: UserRow) {
		deleteRecipes = false;
		dialog = { kind: 'gdpr-warning', row };
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
						<td class="p-3 text-right">{row.recipes_count}</td>
						<td class="p-3 text-right">{row.favorites_count}</td>
						<td class="p-3 text-right">{row.ratings_count}</td>
						<td class="p-3 text-right">
							<!-- UC-ADMIN-005 AC5: always offered — an erased account still
							     warrants inspection, even with nothing left to change. -->
							<a
								href="/usuarios/{row.id}"
								class="btn btn-ghost btn-sm"
								title="Ver detalle"
								aria-label="Ver el detalle de {row.display_name}"
							>
								<View class="h-4 w-4" aria-hidden="true" />
							</a>
							{#if row.deleted_at}
								<!-- UC-ADMIN-010 AC1: already erased, so there is nothing left
								     to activate, suspend or erase. The view link is the only
								     action a GDPR-erased row keeps. -->
							{:else if row.is_active}
								<button
									type="button"
									class="btn btn-ghost btn-sm"
									title="Desactivar"
									aria-label="Desactivar a {row.display_name}"
									on:click={() => (dialog = { kind: 'deactivate', row })}
								>
									<Deactivate class="h-4 w-4" aria-hidden="true" />
								</button>
							{:else}
								<button
									type="button"
									class="btn btn-ghost btn-sm"
									title="Activar"
									aria-label="Activar a {row.display_name}"
									on:click={() => (dialog = { kind: 'activate', row })}
								>
									<Activate class="h-4 w-4" aria-hidden="true" />
								</button>
								{#if row.deactivated_at}
									<!-- UC-ADMIN-009 AC1: only a stamped suspension can be force-reactivated. -->
									<button
										type="button"
										class="btn btn-ghost btn-sm"
										title="Forzar reactivación"
										aria-label="Forzar reactivación de {row.display_name}"
										on:click={() => (dialog = { kind: 'reactivate', row })}
									>
										<Reactivate class="h-4 w-4" aria-hidden="true" />
									</button>
								{/if}
								<button
									type="button"
									class="btn btn-ghost btn-sm text-destructive"
									title="Borrar datos (GDPR)"
									aria-label="Borrar los datos de {row.display_name}"
									on:click={() => openGdpr(row)}
								>
									<Erase class="h-4 w-4" aria-hidden="true" />
								</button>
							{/if}
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

{#if dialog?.kind === 'deactivate'}
	<AlertDialog
		open
		destructive
		title="Desactivar cuenta"
		description="Deja de poder iniciar sesión y revoca sus sesiones activas. Puedes volver a activarla cuando quieras."
		confirmLabel="Desactivar"
		loading={busy}
		onConfirm={confirm}
		onClose={() => (dialog = null)}
	>
		<p class="text-sm text-muted-foreground">{dialog.row.display_name} · {dialog.row.email}</p>
	</AlertDialog>
{:else if dialog?.kind === 'activate'}
	<AlertDialog
		open
		title="Activar cuenta"
		description="Restaura el acceso inmediatamente."
		confirmLabel="Activar"
		loading={busy}
		onConfirm={confirm}
		onClose={() => (dialog = null)}
	>
		<p class="text-sm text-muted-foreground">{dialog.row.display_name} · {dialog.row.email}</p>
	</AlertDialog>
{:else if dialog?.kind === 'reactivate'}
	<AlertDialog
		open
		title="Forzar reactivación"
		description="Se le enviará un email para definir nuevo display_name y elegir contraseña."
		confirmLabel="Reactivar"
		loading={busy}
		onConfirm={confirm}
		onClose={() => (dialog = null)}
	>
		<p class="text-sm text-muted-foreground">{dialog.row.display_name} · {dialog.row.email}</p>
	</AlertDialog>
{:else if dialog?.kind === 'gdpr-warning'}
	<AlertDialog
		open
		destructive
		title="ELIMINAR DEFINITIVAMENTE al usuario"
		description="Esta acción es IRREVERSIBLE: la PII queda anonimizada, sus recetas pasan al usuario system y las FK quedan en NULL."
		confirmLabel="Continuar"
		loading={busy}
		onConfirm={confirm}
		onClose={() => (dialog = null)}
	>
		<p class="text-sm text-muted-foreground">{dialog.row.display_name} · {dialog.row.email}</p>
	</AlertDialog>
{:else if dialog?.kind === 'gdpr-recipes'}
	<AlertDialog
		open
		destructive
		title="¿Eliminar también sus recetas?"
		description="Dejarlas marcadas hace soft delete de todo lo que haya creado. Desmarcadas quedan publicadas bajo el usuario system."
		confirmLabel="Eliminar cuenta"
		loading={busy}
		onConfirm={confirm}
		onClose={() => (dialog = null)}
	>
		<p class="mb-3 text-sm text-muted-foreground">
			{dialog.row.display_name} · {dialog.row.email}
		</p>
		<label class="flex items-center gap-2 text-sm text-foreground">
			<input type="checkbox" bind:checked={deleteRecipes} class="h-4 w-4" />
			Eliminar también sus recetas
		</label>
	</AlertDialog>
{/if}
