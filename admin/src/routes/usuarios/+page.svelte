<script lang="ts">
	import { onMount } from 'svelte';
	import {
		IconUserCheck as Activate,
		IconUserOff as Deactivate,
		IconTrashFilled as Erase
	} from '@tabler/icons-svelte';
	import { adminFetch, formatDate } from '$lib/api';

	type UserRow = {
		id: string;
		email: string;
		display_name: string;
		role: string;
		is_active: boolean;
		is_verified: boolean;
		created_at: string;
		last_login_at?: string | null;
	};

	let items: UserRow[] = [];
	let search = '';
	let status = '';
	let loading = true;
	let error = '';

	async function load() {
		loading = true;
		error = '';
		try {
			const params = new URLSearchParams({ limit: '100' });
			if (search) params.set('search', search);
			if (status) params.set('is_active', status === 'active' ? 'true' : 'false');
			const data = await adminFetch<{ items: UserRow[] }>(`/users?${params.toString()}`);
			items = data.items;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Error';
		} finally {
			loading = false;
		}
	}

	async function toggleActive(row: UserRow) {
		await adminFetch(`/users/${row.id}/${row.is_active ? 'deactivate' : 'activate'}`, { method: 'POST' });
		await load();
	}

	async function changeRole(row: UserRow, role: string) {
		await adminFetch(`/users/${row.id}/role`, { method: 'PATCH', body: JSON.stringify({ role }) });
		await load();
	}

	async function gdprErase(row: UserRow) {
		if (!confirm(`¿Anonimizar los datos de "${row.display_name}"? Esta acción no se puede deshacer.`)) return;
		const deleteRecipes = confirm('¿Eliminar también sus recetas? (Cancelar = conservarlas)');
		await adminFetch(`/users/${row.id}/gdpr-erase`, {
			method: 'POST',
			body: JSON.stringify({ delete_recipes: deleteRecipes })
		});
		await load();
	}

	onMount(load);
</script>

<svelte:head><title>Usuarios — Recetario Admin</title></svelte:head>

<div class="space-y-6">
	<div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
		<h1 class="font-playfair text-2xl font-medium text-foreground">Usuarios</h1>
		<div class="flex gap-2">
			<select bind:value={status} on:change={load} class="input-base" aria-label="Estado">
				<option value="">Todos</option>
				<option value="active">Activos</option>
				<option value="inactive">Inactivos</option>
			</select>
			<input type="search" bind:value={search} on:input={load} placeholder="Buscar…" class="input-base" />
		</div>
	</div>

	{#if error}<p class="text-sm text-destructive" role="alert">{error}</p>{/if}

	<div class="card overflow-x-auto">
		<table class="w-full text-sm">
			<thead class="border-b border-border text-left text-muted-foreground">
				<tr><th class="p-3">Usuario</th><th class="p-3">Rol</th><th class="p-3">Estado</th><th class="p-3">Alta</th><th class="p-3 text-right">Acciones</th></tr>
			</thead>
			<tbody>
				{#each items as row (row.id)}
					<tr class="border-b border-border last:border-0">
						<td class="p-3">
							<p class="font-medium text-foreground">{row.display_name}</p>
							<p class="text-xs text-muted-foreground">{row.email}</p>
						</td>
						<td class="p-3">
							<select value={row.role} on:change={(e) => changeRole(row, e.currentTarget.value)} class="input-base py-1" aria-label="Rol">
								<option value="user">user</option>
								<option value="admin">admin</option>
							</select>
						</td>
						<td class="p-3">
							<span class="badge {row.is_active ? 'bg-success/10 text-success' : 'bg-destructive/10 text-destructive'}">
								{row.is_active ? 'Activo' : 'Inactivo'}
							</span>
						</td>
						<td class="p-3 text-muted-foreground">{formatDate(row.created_at)}</td>
						<td class="p-3 text-right">
							<button type="button" class="btn btn-ghost btn-sm" on:click={() => toggleActive(row)} title={row.is_active ? 'Desactivar' : 'Activar'}>
								{#if row.is_active}<Deactivate class="h-4 w-4" aria-hidden="true" />{:else}<Activate class="h-4 w-4" aria-hidden="true" />{/if}
							</button>
							<button type="button" class="btn btn-ghost btn-sm text-destructive" on:click={() => gdprErase(row)} title="Borrar datos (GDPR)">
								<Erase class="h-4 w-4" aria-hidden="true" />
							</button>
						</td>
					</tr>
				{/each}
				{#if !loading && items.length === 0}
					<tr><td class="p-6 text-center text-muted-foreground" colspan="5">Sin usuarios</td></tr>
				{/if}
			</tbody>
		</table>
	</div>
</div>
