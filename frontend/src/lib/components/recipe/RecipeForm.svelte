<script lang="ts">
	import { apiFetch } from '$lib/api';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { IconTrashFilled as Trash, IconPlus } from '@tabler/icons-svelte';
	import { categoriesStore } from '$lib/stores/categories';
	import TagAutocomplete from '$components/search/TagAutocomplete.svelte';
	import Dialog from '$components/ui/Dialog.svelte';
	import type { Recipe } from '$lib/types';

	export let initial: Partial<Recipe> | null = null;
	export let slug: string | null = null;

	const DIFFICULTIES = [
		{ v: '', l: 'Sin especificar' },
		{ v: 'easy', l: 'Fácil' },
		{ v: 'medium', l: 'Media' },
		{ v: 'hard', l: 'Difícil' }
	];

	// RF-12.2 / RF-12.3: hay que coincidir con VALID_CATEGORIES y VALID_UNITS del backend.
	const INGREDIENT_CATEGORIES = [
		{ v: 'proteina', l: 'Proteína' },
		{ v: 'verdura', l: 'Verdura' },
		{ v: 'fruta', l: 'Fruta' },
		{ v: 'lacteo', l: 'Lácteo' },
		{ v: 'grano', l: 'Grano' },
		{ v: 'condimento', l: 'Condimento' },
		{ v: 'grasa', l: 'Grasa' },
		{ v: 'otro', l: 'Otro' }
	];
	const INGREDIENT_UNITS = [
		'g',
		'kg',
		'ml',
		'l',
		'unidad',
		'cucharada',
		'cucharadita',
		'taza',
		'pizca'
	];

	type IngredientRow = {
		ingredient_id: string;
		name: string;
		amount: string | number;
		unit: string;
		notes: string;
		default_unit: string;
		/** RF-12.8: vacío = sin restricción; con valores = default_unit + alternativas. */
		allowed_units: string[];
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
	let tagSlugs: string[] = initial?.tags?.map((t) => t.slug) ?? [];
	let rows: IngredientRow[] =
		initial?.ingredients?.map((i) => ({
			ingredient_id: i.ingredient_id,
			name: i.name ?? '',
			amount: i.amount ?? '',
			unit: i.unit ?? '',
			notes: i.notes ?? '',
			// RF-12.8: present when the recipe came through
			// resolve_ingredient_catalog(), so an edit opens with the same
			// narrowed unit menu a freshly picked ingredient gets.
			default_unit: i.default_unit ?? '',
			allowed_units: i.allowed_units ?? []
		})) ?? [];

	let ingQuery = '';
	let ingSuggestions: {
		id: string;
		name: string;
		default_unit: string;
		allowed_units: string[];
	}[] = [];
	let ingTimer: ReturnType<typeof setTimeout>;
	let saving = false;
	let error = '';
	let uploading = false;
	let uploadError = '';
	let showNewIngredient = false;
	let creatingIngredient = false;
	let modalError = '';
	let newIngredient = { name: '', category: 'otro', default_unit: 'unidad', aliases: '' };

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

	function addIngredient(ing: {
		id: string;
		name: string;
		default_unit: string;
		allowed_units?: string[];
	}) {
		rows = [
			...rows,
			{
				ingredient_id: ing.id,
				name: ing.name,
				amount: '',
				unit: ing.default_unit,
				notes: '',
				default_unit: ing.default_unit,
				allowed_units: ing.allowed_units ?? []
			}
		];
		ingQuery = '';
		ingSuggestions = [];
	}

	// RF-12.8: a row only offers the units its catalog entry accepts. An empty
	// whitelist (or a row loaded from an existing recipe, which carries no
	// catalog data) falls back to the nine global units.
	function unitsFor(row: IngredientRow): string[] {
		if (row.allowed_units.length === 0) return INGREDIENT_UNITS;
		const list = [row.default_unit, ...row.allowed_units].filter(Boolean);
		return [...new Set(list)];
	}

	// RF-12.5: crear desde el selector abre un modal con categoría y unidad.
	function addManual() {
		const name = ingQuery.trim();
		if (!name) return;
		newIngredient = { name, category: 'otro', default_unit: 'unidad', aliases: '' };
		modalError = '';
		showNewIngredient = true;
	}

	async function saveNewIngredient() {
		const name = newIngredient.name.trim();
		if (name.length < 2) {
			modalError = 'El nombre debe tener al menos 2 caracteres.';
			return;
		}
		modalError = '';
		creatingIngredient = true;
		try {
			const res = await apiFetch('/api/v1/ingredients', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					name,
					category: newIngredient.category,
					default_unit: newIngredient.default_unit,
					aliases: newIngredient.aliases
						.split(',')
						.map((a) => a.trim())
						.filter(Boolean)
				})
			});
			if (!res.ok) {
				const body = await res.json().catch(() => ({}));
				modalError = typeof body.detail === 'string' ? body.detail : `No se pudo crear "${name}".`;
				return;
			}
			const ingredient = await res.json();
			rows = [
				...rows,
				{
					ingredient_id: ingredient.id,
					name: ingredient.name,
					amount: '',
					unit: ingredient.default_unit ?? '',
					notes: '',
					default_unit: ingredient.default_unit ?? '',
					allowed_units: ingredient.allowed_units ?? []
				}
			];
			showNewIngredient = false;
			ingQuery = '';
			ingSuggestions = [];
		} catch {
			modalError = 'No se pudo crear el ingrediente. Revisá tu conexión.';
		} finally {
			creatingIngredient = false;
		}
	}

	function removeRow(index: number) {
		rows = rows.filter((_, i) => i !== index);
	}

	async function uploadImage(event: Event) {
		const input = event.currentTarget as HTMLInputElement;
		const file = input.files?.[0];
		if (!file) return;

		uploading = true;
		uploadError = '';
		try {
			const form = new FormData();
			form.append('file', file);
			const res = await apiFetch('/api/v1/uploads', {
				method: 'POST',
				body: form
			});
			if (res.ok) {
				const body = await res.json();
				imageUrl = body.url;
			} else {
				const body = await res.json().catch(() => ({}));
				uploadError = body.detail ? String(body.detail) : 'No se pudo subir la imagen.';
			}
		} catch {
			uploadError = 'No se pudo subir la imagen.';
		} finally {
			uploading = false;
			input.value = '';
		}
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
			tags: tagSlugs,
			ingredients: rows.map((r) => ({
				ingredient_id: r.ingredient_id,
				name: r.name,
				amount: r.amount === '' ? null : Number(r.amount),
				unit: r.unit,
				notes: r.notes || null
			}))
		};

		saving = true;
		const res = await apiFetch(slug ? `/api/v1/recipes/${slug}` : '/api/v1/recipes', {
			method: slug ? 'PATCH' : 'POST',
			headers: {
				'Content-Type': 'application/json'
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
		<p
			class="rounded-md border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive"
			role="alert"
		>
			{error}
		</p>
	{/if}

	<div>
		<label for="title" class="mb-1 block text-sm font-medium text-foreground">Título *</label>
		<input id="title" bind:value={title} class="input-base" maxlength="200" required />
	</div>

	<div>
		<label for="description" class="mb-1 block text-sm font-medium text-foreground"
			>Descripción</label
		>
		<textarea id="description" bind:value={description} rows="2" class="input-base"></textarea>
	</div>

	<div class="grid gap-4 sm:grid-cols-2">
		<div>
			<label for="category" class="mb-1 block text-sm font-medium text-foreground"
				>Categoría *</label
			>
			<select id="category" bind:value={categoryId} class="input-base" required>
				<option value="">Elegí una categoría…</option>
				{#each categories as cat}<option value={cat.id}>{cat.name}</option>{/each}
			</select>
		</div>
		<div>
			<label for="difficulty" class="mb-1 block text-sm font-medium text-foreground"
				>Dificultad</label
			>
			<select id="difficulty" bind:value={difficulty} class="input-base">
				{#each DIFFICULTIES as d}<option value={d.v}>{d.l}</option>{/each}
			</select>
		</div>
	</div>

	<div>
		<label for="image" class="mb-1 block text-sm font-medium text-foreground">Imagen</label>
		<input
			id="image"
			bind:value={imageUrl}
			class="input-base"
			maxlength="500"
			placeholder="https://… o subí un archivo"
		/>
		<div class="mt-2 flex items-center gap-3">
			<input
				type="file"
				accept="image/png,image/jpeg,image/webp,image/gif"
				on:change={uploadImage}
				class="text-sm text-muted-foreground"
				aria-label="Subir imagen"
			/>
			{#if uploading}<span class="text-sm text-muted-foreground">Subiendo…</span>{/if}
		</div>
		{#if uploadError}<p class="mt-1 text-sm text-destructive" role="alert">{uploadError}</p>{/if}
		{#if imageUrl}
			<img
				src={imageUrl}
				alt="Vista previa"
				class="mt-3 h-40 w-full max-w-xs rounded-lg border border-border object-cover"
			/>
		{/if}
	</div>

	<div class="grid gap-4 sm:grid-cols-3">
		<div>
			<label for="prep" class="mb-1 block text-sm font-medium text-foreground"
				>Preparación (min)</label
			>
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
						<input
							type="number"
							min="0"
							step="any"
							bind:value={row.amount}
							class="input-base w-20 py-1.5"
							placeholder="Cant."
							aria-label="Cantidad de {row.name}"
						/>
						<select
							bind:value={row.unit}
							class="input-base w-24 py-1.5"
							aria-label="Unidad de {row.name}"
						>
							{#if row.unit && !unitsFor(row).includes(row.unit)}
								<option value={row.unit}>{row.unit}</option>
							{/if}
							{#each unitsFor(row) as u}<option value={u}>{u}</option>{/each}
						</select>
						<input
							type="text"
							bind:value={row.notes}
							class="input-base w-32 py-1.5"
							placeholder="Notas"
							aria-label="Notas de {row.name}"
						/>
						<button
							type="button"
							class="btn btn-ghost btn-sm text-destructive"
							on:click={() => removeRow(i)}
							aria-label="Quitar {row.name}"
						>
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
				<button
					type="button"
					class="btn btn-outline btn-sm"
					on:click={addManual}
					disabled={!ingQuery.trim()}
				>
					<IconPlus class="h-4 w-4" aria-hidden="true" /> Agregar
				</button>
			</div>
			{#if ingSuggestions.length > 0}
				<ul
					class="absolute z-50 mt-1 max-h-56 w-full overflow-y-auto rounded-lg border border-border bg-popover shadow-lg"
				>
					{#each ingSuggestions as ing}
						<li>
							<button
								type="button"
								class="w-full px-3 py-2 text-left text-sm hover:bg-accent"
								on:click={() => addIngredient(ing)}
							>
								{ing.name}
							</button>
						</li>
					{/each}
				</ul>
			{/if}
		</div>
	</fieldset>

	<fieldset class="rounded-lg border border-border p-4">
		<legend class="px-1 text-sm font-medium text-foreground">Etiquetas</legend>
		<TagAutocomplete
			selected={tagSlugs}
			onChange={(tags) => (tagSlugs = tags)}
			placeholder="Buscar o crear etiquetas…"
		/>
	</fieldset>

	<div>
		<label for="instructions" class="mb-1 block text-sm font-medium text-foreground"
			>Preparación *</label
		>
		<textarea
			id="instructions"
			bind:value={instructions}
			rows="6"
			class="input-base"
			placeholder="Un paso por línea…"
			required
		></textarea>
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

<Dialog
	open={showNewIngredient}
	title="Nuevo ingrediente"
	onClose={() => (showNewIngredient = false)}
>
	<div class="space-y-4">
		<div>
			<label for="new-ing-name" class="label">Nombre</label>
			<input
				id="new-ing-name"
				type="text"
				bind:value={newIngredient.name}
				class="input-base"
				minlength="2"
				maxlength="100"
				required
			/>
		</div>

		<div class="grid gap-4 sm:grid-cols-2">
			<div>
				<label for="new-ing-category" class="label">Categoría</label>
				<select id="new-ing-category" bind:value={newIngredient.category} class="input-base">
					{#each INGREDIENT_CATEGORIES as c}<option value={c.v}>{c.l}</option>{/each}
				</select>
			</div>
			<div>
				<label for="new-ing-unit" class="label">Unidad por defecto</label>
				<select id="new-ing-unit" bind:value={newIngredient.default_unit} class="input-base">
					{#each INGREDIENT_UNITS as u}<option value={u}>{u}</option>{/each}
				</select>
			</div>
		</div>

		<div>
			<label for="new-ing-aliases" class="label"
				>Aliases <span class="text-muted-foreground">(opcional, separados por coma)</span></label
			>
			<input
				id="new-ing-aliases"
				type="text"
				bind:value={newIngredient.aliases}
				class="input-base"
				placeholder="tomate pera, cherry"
			/>
		</div>

		{#if modalError}<p class="text-sm text-destructive" role="alert">{modalError}</p>{/if}
		<p class="text-xs text-muted-foreground">
			El ingrediente queda pendiente de validación por un administrador.
		</p>
	</div>

	<svelte:fragment slot="footer">
		<button type="button" class="btn btn-outline" on:click={() => (showNewIngredient = false)}>
			Cancelar
		</button>
		<button
			type="button"
			class="btn btn-primary"
			on:click={saveNewIngredient}
			disabled={creatingIngredient}
		>
			{creatingIngredient ? 'Creando…' : 'Crear ingrediente'}
		</button>
	</svelte:fragment>
</Dialog>
