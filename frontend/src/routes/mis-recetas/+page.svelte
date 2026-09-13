<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { IconEyeFilled as Public, IconEyeOff as Private, IconTrashFilled as Trash, IconEdit as Edit, IconRestore as Restore } from '@tabler/icons-svelte';
	import { auth } from '$lib/stores/auth';
	import { formatNumber } from '$lib/utils';
	import RecipeCard from '$components/recipe/RecipeCard.svelte';

	type RecipeItem = {
		id: string;
		slug: string;
		title: string;
		is_public: boolean;
		deleted_at?: string | null;
		visit_count: number;
		avg_rating: number;
		rating_count: number;
		category?: { name: string; icon?: string; color: string; slug: string; id: string };
		author?: any;
		tags?: any[];
		[key: string]: any;
	};

	let items: RecipeItem[] = [];
	let tab: 'public' | 'private' | 'deleted' = 'public';
	let loading = true;
	let error = '';

	$: visible = items.filter((r) => {
		if (tab === 'deleted') return !!r.deleted_at;
		if (r.deleted_at) return false;
		return tab === 'public' ? r.is_public : !r.is_public;
	});

	async function load() {
		loading = true;
		error = '';
		try {
			const res = await fetch('/api/v1/users/me/recipes?limit=100&include_deleted=true', {
				headers: { Authorization: `Bearer ${$auth.accessToken}` }
			});
			if (!res.ok) throw new Error(`API ${res.status}`);
			items = (await res.json()).recipes ?? [];
		} catch (err) {
			error = err instanceof Error ? err.message : 'Error';
		} finally {
			loading = false;
		}
	}

	async function toggleVisibility(r: RecipeItem) {
		await fetch(`/api/v1/recipes/${r.slug}`, {
			method: 'PATCH',
			headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${$auth.accessToken}` },
			body: JSON.stringify({ is_public: !r.is_public })
		});
		await load();
	}

	async function remove(r: RecipeItem) {
		if (!confirm(`¿Eliminar la receta "${r.title}"?`)) return;
		await fetch(`/api/v1/recipes/${r.slug}`, {
			method: 'DELETE',
			headers: { Authorization: `Bearer ${$auth.accessToken}` }
		});
		await load();
	}

	async function restore(r: RecipeItem) {
		await fetch(`/api/v1/recipes/${r.slug}/restore`, {
			method: 'POST',
			headers: { Authorization: `Bearer ${$auth.accessToken}` }
		});
		await load();
	}

	onMount(async () => {
		if (!$auth.isAuthenticated) await auth.init();
		if (!$auth.isAuthenticated) {
			await goto('/login?returnTo=/mis-recetas');
			return;
		}
		await load();
	});
</script>

<svelte:head><title>Mis recetas — Recetario IA</title></svelte:head>

<div class="container py-8">
	<h1 class="mb-6 font-playfair text-2xl font-medium text-foreground md:text-3xl">Mis recetas</h1>

	<div class="mb-6 flex gap-2">
		{#each [{ k: 'public', l: 'Publicadas' }, { k: 'private', l: 'Privadas' }, { k: 'deleted', l: 'Borradas' }] as t}
			<button type="button" class="btn {tab === t.k ? 'btn-primary' : 'btn-outline'} btn-sm" on:click={() => (tab = t.k as typeof tab)}>
				{t.l}
			</button>
		{/each}
	</div>

	{#if error}<p class="mb-4 text-sm text-destructive" role="alert">{error}</p>{/if}

	{#if loading}
		<p class="text-muted-foreground">Cargando…</p>
	{:else if visible.length === 0}
		<p class="text-muted-foreground">No hay recetas en esta sección.</p>
	{:else}
		<div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
			{#each visible as r (r.id)}
				<div class="flex flex-col gap-2">
					<RecipeCard recipe={r as any} />
					<div class="flex items-center justify-between gap-2 px-1">
						<span class="inline-flex items-center gap-1 text-xs text-muted-foreground">
							{#if r.deleted_at}Borrada{:else if r.is_public}<Public class="h-3.5 w-3.5" aria-hidden="true" /> Pública{:else}<Private class="h-3.5 w-3.5" aria-hidden="true" /> Privada{/if}
							· {formatNumber(r.avg_rating)}★ · {r.visit_count} visitas
						</span>
						<div class="flex gap-1">
							{#if r.deleted_at}
								<button type="button" class="btn btn-ghost btn-sm" on:click={() => restore(r)} title="Restaurar">
									<Restore class="h-4 w-4" aria-hidden="true" />
								</button>
							{:else}
								<a href={`/recetas/${r.slug}/editar`} class="btn btn-ghost btn-sm" title="Editar">
									<Edit class="h-4 w-4" aria-hidden="true" />
								</a>
								<button type="button" class="btn btn-ghost btn-sm" on:click={() => toggleVisibility(r)} title={r.is_public ? 'Hacer privada' : 'Publicar'}>
									{#if r.is_public}<Private class="h-4 w-4" aria-hidden="true" />{:else}<Public class="h-4 w-4" aria-hidden="true" />{/if}
								</button>
								<button type="button" class="btn btn-ghost btn-sm text-destructive" on:click={() => remove(r)} title="Eliminar">
									<Trash class="h-4 w-4" aria-hidden="true" />
								</button>
							{/if}
						</div>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>
