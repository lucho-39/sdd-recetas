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
	<span class="mb-2 block text-sm font-medium text-foreground">Categoría</span>
	<div class="flex flex-wrap gap-2" role="radiogroup" aria-label="Seleccionar categoría">
		<button
			type="button"
			role="radio"
			aria-checked={!selected}
			class="badge px-3 py-1.5 transition-all {!selected ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground hover:bg-muted/80'}"
			on:click={() => onChange(undefined)}
		>
			Todas
		</button>
		{#each categories as cat}
			<button
				type="button"
				role="radio"
				aria-checked={selected === cat.slug}
				class="badge flex items-center gap-1 px-3 py-1.5 transition-all {selected === cat.slug ? 'text-white' : 'bg-muted text-muted-foreground hover:bg-muted/80'}"
				style={selected === cat.slug ? `background-color: ${cat.color};` : ''}
				on:click={() => onChange(cat.slug)}
			>
				{#if cat.icon}<span aria-hidden="true">{cat.icon}</span>{/if}
				{cat.name}
			</button>
		{/each}
	</div>
</div>
