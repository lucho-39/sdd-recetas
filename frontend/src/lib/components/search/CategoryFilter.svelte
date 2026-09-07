<script lang="ts">
	import { categoriesStore } from '$lib/stores/categories';

	export let selected: string | undefined;
	export let onChange: (slug: string | undefined) => void;
	export let categories: { slug: string; name: string; icon?: string; color: string }[] = [];

	$: if (categories.length === 0) {
		categories = $categoriesStore.categories;
	}
</script>

<div class="space-y-2">
	<label class="block text-sm font-medium text-foreground mb-2">Categoría</label>
	<div class="flex flex-wrap gap-2" role="radiogroup" aria-label="Seleccionar categoría">
		<button
			type="button"
			role="radio"
			aria-checked={!selected}
			class="badge px-3 py-1.5 transition-all {selected ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground hover:bg-muted/80'}"
			on:click={() => onChange(undefined)}
			aria-checked={!selected}
		>
			Todas
		</button>
		{#each categories as cat}
			<button
				type="button"
				role="radio"
				aria-checked={selected === cat.slug}
				class="badge px-3 py-1.5 transition-all flex items-center gap-1
					{selected === cat.slug ? 'bg-[{cat.color}] text-white' : 'bg-muted text-muted-foreground hover:bg-muted/80'}"
				on:click={() => onChange(cat.slug)}
				aria-checked={selected === cat.slug}
				style="--badge-color: {cat.color};"
			>
				{#if cat.icon}<span aria-hidden="true">{cat.icon}</span>{/if}
				{cat.name}
			</button>
		{/each}
	</div>