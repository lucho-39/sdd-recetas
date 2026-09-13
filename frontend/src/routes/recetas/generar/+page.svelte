<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { IconSparklesFilled as Sparkles } from '@tabler/icons-svelte';
	import { auth } from '$lib/stores/auth';
	import RecipeForm from '$lib/components/recipe/RecipeForm.svelte';

	let ingredients = '';
	let preferences = '';
	let servings: number | '' = '';
	let loading = false;
	let error = '';
	let draft: Record<string, unknown> | null = null;
	let ready = false;

	onMount(async () => {
		if (!$auth.isAuthenticated && !$auth.loading) await auth.init();
		if (!$auth.isAuthenticated) {
			await goto('/login?returnTo=/recetas/generar');
			return;
		}
		ready = true;
	});

	function toRecipe(data: Record<string, unknown>) {
		const list = (data.ingredients as Record<string, unknown>[]) ?? [];
		const tags = (data.tags as unknown[]) ?? [];
		return {
			title: (data.title as string) ?? '',
			description: (data.description as string) ?? '',
			category_id: '',
			instructions: (data.instructions as string) ?? '',
			difficulty: (data.difficulty as string) ?? '',
			prep_time_minutes: data.prep_time_minutes ?? null,
			cook_time_minutes: data.cook_time_minutes ?? null,
			servings: data.servings ?? null,
			is_public: true,
			image_url: null,
			ingredients: list.map((item) => ({
				ingredient_id: '',
				name: (item.name as string) ?? '',
				amount: item.amount ?? '',
				unit: (item.unit as string) ?? '',
				notes: ''
			})),
			tags: tags.map((tag) => {
				const name = String(tag);
				return { id: '', slug: name.toLowerCase().replace(/\s+/g, '-'), name };
			})
		};
	}

	async function generate() {
		error = '';
		draft = null;
		loading = true;
		try {
			const response = await fetch('/api/v1/ai/generate', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					Authorization: `Bearer ${$auth.accessToken}`
				},
				body: JSON.stringify({
					ingredients,
					preferences: preferences || null,
					servings: servings === '' ? null : Number(servings)
				})
			});
			if (!response.ok) {
				const body = await response.json().catch(() => ({}));
				throw new Error(body.detail || 'No se pudo generar la receta');
			}
			draft = (await response.json()).draft;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Error';
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head><title>Generar receta con IA — Recetario IA</title></svelte:head>

<div class="container py-8">
	<h1 class="mb-6 font-playfair text-2xl font-medium text-foreground md:text-3xl">Generar receta con IA</h1>

	{#if !ready}
		<p class="text-muted-foreground">Cargando…</p>
	{:else if draft}
		<p class="mb-4 text-sm text-muted-foreground">
			Revisá y ajustá el borrador antes de guardarlo.
		</p>
		<RecipeForm initial={toRecipe(draft)} />
	{:else}
		<form class="mx-auto max-w-2xl space-y-4" on:submit|preventDefault={generate}>
			{#if error}
				<p class="rounded-md border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive" role="alert">{error}</p>
			{/if}
			<div>
				<label for="ingredients" class="mb-1 block text-sm font-medium text-foreground">Ingredientes disponibles *</label>
				<textarea id="ingredients" bind:value={ingredients} rows="3" class="input-base" placeholder="Ej: pollo, tomate, cebolla, arroz" required></textarea>
			</div>
			<div>
				<label for="preferences" class="mb-1 block text-sm font-medium text-foreground">Preferencias</label>
				<input id="preferences" bind:value={preferences} class="input-base" placeholder="Ej: sin gluten, vegano, rápido" />
			</div>
			<div>
				<label for="servings" class="mb-1 block text-sm font-medium text-foreground">Porciones</label>
				<input id="servings" type="number" min="1" max="20" bind:value={servings} class="input-base w-32" />
			</div>
			<button type="submit" class="btn btn-primary" disabled={loading || ingredients.trim().length < 3}>
				<Sparkles class="h-4 w-4" aria-hidden="true" />
				{loading ? 'Generando…' : 'Generar con IA'}
			</button>
		</form>
	{/if}
</div>
