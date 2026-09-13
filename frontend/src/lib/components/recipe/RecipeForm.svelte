<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { IconTrashFilled as Trash, IconPlus } from '@tabler/icons-svelte';
	import { auth } from '$lib/stores/auth';
	import { categoriesStore } from '$lib/stores/categories';
	import type { Recipe } from '$lib/types';

	export let initial: Recipe | null = null;
	export let slug: string | null = null;

	const DIFFICULTIES = [
		{ v: '', l: 'Sin especificar' },
		{ v: 'easy', l: 'Fácil' },
		{ v: 'medium', l: 'Media' },
		{ v: 'hard', l: 'Difícil' }
	];

	type IngredientRow = {
		ingredient_id: string;
		name: string;
		amount: string | number;
		unit: string;
		notes: string;
	};

	let title = initial?.title ?? '';
	let description = initial?.description ?? '';
	let categoryId = initial?.category_id ?? initial?.category?.id ?? '';
	let imageUrl = initial?.image_url ?? '';
	let prepTime: number | '' = initial?.prep_time_minutes ?? '';
	let cookTime: number | '' = initial?.cook_time_minutes ?? '';
	let servings: number | '' = initial?.servings ?? '';
	let difficulty = initial?.difficulty ?? '';
	let isPublic = initial?.is_public ?? true;
	let instructions = initial?.instructions ?? '';
	let rows: IngredientRow[] =
		initial?.ingredients?.map((i) => ({
			ingredient_id: i.ingredient_id,
			name: i.name ?? '',
			amount: i.amount ?? '',
			unit: i.unit ?? '',
			notes: i.notes ?? ''
		})) ?? [];

	let ingQuery = '';
	let ingSuggestions: { id: string; name: string; default_unit: string }[] = [];
	let ingTimer: ReturnType<typeof setTimeout>;
	let saving = false;
	let error = '';

	$: categories = $categoriesStore.categories;

	function searchIngredients() {
		if (ingTimer) clearTimeout(ingTimer);
		ingTimer = setTimeout(async () => {
			if (ingQuery.trim().length < 2) {
				ingSuggestions = [];
				return;
			}
			const res = await fetch(`/api/v1/ingredients?query=${encodeURIComponent(ingQuery)}&limit=8`);
			ingSuggestions = res.ok ? await res.json() : [];
		}, 200);
	}

	function addIngredient(ing: { id: string; name: string; default_unit: string }) {
		rows = [...rows, { ingredient_id: ing.id, name: ing.name, amount: '', unit: ing.default_unit, notes: '' }];
		ingQuery = '';
		ingSuggestions = [];
	}

	function addManual() {
		if (!ingQuery.trim()) return;
		rows = [...rows, { ingredient_id: '', name: ingQuery.trim(), amount: '', unit: '', notes: '' }];
		ingQuery = '';
		ingSuggestions = [];
	}

	function removeRow(index: number) {
		rows = rows.filter((_, i) => i !== index);
	}

	async function submit() {
		error = '';
		if (title.trim().length < 3) {
			error = 'El título debe tener al menos 3 caracteres.';
			return;
		}
		if (!categoryId) {
			error = 'Elegí una categoría.';
			return;
		}
		if (instructions.trim().length < 10) {
			error = 'La preparación debe tener al menos 10 caracteres.';
			return;
		}

		const payload = {
			title: title.trim(),
			description: description.trim() || null,
			category_id: categoryId,
			image_url: imageUrl.trim() || null,
			prep_time_minutes: prepTime === '' ? null : Number(prepTime),
			cook_time_minutes: cookTime === '' ? null : Number(cookTime),
			servings: servings === '' ? null : Number(servings),
			difficulty: difficulty || null,
			instructions: instructions.trim(),
			is_public: isPublic,
			ingredients: rows.map((r) => ({
				ingredient_id: r.ingredient_id || r.name.toLowerCase().replace(/\s+/g, '-'),
				name: r.name,
				amount: r.amount === '' ? null : Number(r.amount),
				unit: r.unit,
				notes: r.notes || null
			}))
		};

		saving = true;
		const res = await fetch(slug ? `/api/v1/recipes/${slug}` : '/api/v1/recipes', {
			method: slug ? 'PATCH' : 'POST',
			headers: {
				'Content-Type': 'application/json',
				Authorization: `Bearer ${$auth.accessToken}`
			},
			body: JSON.stringify(payload)
		});
		saving = false;

		if (!res.ok) {
			const body = await res.json().catch(() => ({}));
			error = body.detail ? String(body.detail) : `No se pudo guardar (${res.status}).`;
			return;
		}
		const saved = await res.json();
		await goto(`/receta/${saved.slug}`);
	}

	onMount(() => {
		categoriesStore.fetchCategories();
	});
</script>

<form class="mx-auto max-w-2xl space-y-6" on:submit|preventDefault={submit}>
	{#if error}
		<p class="rounded-md border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive" role="alert">
			{error}
		</p>
	{/if}

	<div>
		<label for="title" class="mb-1 block text-sm font-medium text-foreground">Título *</label>
		<input id="title" bind:value={title} class="input-base" maxlength="200" required />
	</div>

	<div>
		<label for="description" class="mb-1 block text-sm font-medium text-foreground">Descripción</label>
		<textarea id="description" bind:value={description} rows="2" class="input-base"></textarea>
	</div>

	<div class="grid gap-4 sm:grid-cols-2">
		<div>
			<label for="category" class="mb-1 block text-sm font-medium text-foreground">Categoría *</label>
			<select id="category" bind:value={categoryId} class="input-base" required>
				<option value="">Elegí una categoría…</option>
				{#each categories as cat}<option value={cat.id}>{cat.name}</option>{/each}
			</select>
		</div>
		<div>
			<label for="difficulty" class="mb-1 block text-sm font-medium text-foreground">Dificultad</label>
			<select id="difficulty" bind:value={difficulty} class="input-base">
				{#each DIFFICULTIES as d}<option value={d.v}>{d.l}</option>{/each}
			</select>
		</div>
	</div>

	<div>
		<label for="image" class="mb-1 block text-sm font-medium text-foreground">Imagen (URL)</label>
		<input id="image" bind:value={imageUrl} class="input-base" maxlength="500" placeholder="https://…" />
	</div>

	<div class="grid gap-4 sm:grid-cols-3">
		<div>
			<label for="prep" class="mb-1 block text-sm font-medium text-foreground">Preparación (min)</label>
			<input id="prep" type="number" min="0" bind:value={prepTime} class="input-base" />
		</div>
		<div>
			<label for="cook" class="mb-1 block text-sm font-medium text-foreground">Cocción (min)</label>
			<input id="cook" type="number" min="0" bind:value={cookTime} class="input-base" />
		</div>
		<div>
			<label for="servings" class="mb-1 block text-sm font-medium text-foreground">Porciones</label>
			<input id="servings" type="number" min="1" bind:value={servings} class="input-base" />
		</div>
	</div>

	<!-- Ingredients -->
	<fieldset class="rounded-lg border border-border p-4">
		<legend class="px-1 text-sm font-medium text-foreground">Ingredientes</legend>

		{#if rows.length > 0}
			<ul class="mb-4 space-y-2">
				{#each rows as row, i (i)}
					<li class="flex flex-wrap items-center gap-2">
						<span class="min-w-32 flex-1 text-sm text-foreground">{row.name}</span>
						<input type="number" min="0" step="any" bind:value={row.amount} class="input-base w-20 py-1.5" placeholder="Cant." aria-label="Cantidad de {row.name}" />
						<input type="text" bind:value={row.unit} class="input-base w-24 py-1.5" placeholder="Unidad" aria-label="Unidad de {row.name}" />
						<input type="text" bind:value={row.notes} class="input-base w-32 py-1.5" placeholder="Notas" aria-label="Notas de {row.name}" />
						<button type="button" class="btn btn-ghost btn-sm text-destructive" on:click={() => removeRow(i)} aria-label="Quitar {row.name}">
							<Trash class="h-4 w-4" aria-hidden="true" />
						</button>
					</li>
				{/each}
			</ul>
		{/if}

		<div class="relative">
			<div class="flex gap-2">
				<input
					type="text"
					bind:value={ingQuery}
					on:input={searchIngredients}
					class="input-base"
					placeholder="Buscar en el catálogo…"
				/>
				<button type="button" class="btn btn-outline btn-sm" on:click={addManual} disabled={!ingQuery.trim()}>
					<IconPlus class="h-4 w-4" aria-hidden="true" /> Agregar
				</button>
			</div>
			{#if ingSuggestions.length > 0}
				<ul class="absolute z-50 mt-1 max-h-56 w-full overflow-y-auto rounded-lg border border-border bg-popover shadow-lg">
					{#each ingSuggestions as ing}
						<li>
							<button type="button" class="w-full px-3 py-2 text-left text-sm hover:bg-accent" on:click={() => addIngredient(ing)}>
								{ing.name}
							</button>
						</li>
					{/each}
				</ul>
			{/if}
		</div>
	</fieldset>

	<div>
		<label for="instructions" class="mb-1 block text-sm font-medium text-foreground">Preparación *</label>
		<textarea id="instructions" bind:value={instructions} rows="6" class="input-base" placeholder="Un paso por línea…" required></textarea>
	</div>

	<label class="flex items-center gap-2 text-sm text-foreground">
		<input type="checkbox" bind:checked={isPublic} class="h-4 w-4" />
		Publicar receta (visible para todos)
	</label>

	<div class="flex gap-3">
		<button type="submit" class="btn btn-primary" disabled={saving}>
			{saving ? 'Guardando…' : slug ? 'Guardar cambios' : 'Crear receta'}
		</button>
		<a href="/mis-recetas" class="btn btn-outline">Cancelar</a>
	</div>
</form>
