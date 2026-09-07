<script lang="ts">
	import { onMount } from 'svelte';

	export let selected: string[] = [];
	export let onChange: (ingredients: string[]) => void;
	export let placeholder = 'Buscar ingredientes...';

	let query = '';
	let showSuggestions = false;
	let suggestions: { id: string; name: string; category: string; default_unit: string }[] = [];
	let debounceTimer: ReturnType<typeof setTimeout>;

	async function fetchSuggestions() {
		if (query.length < 2) {
			suggestions = [];
			showSuggestions = false;
			return;
		}
		try {
			const response = await fetch(`/api/ingredients/autocomplete?q=${encodeURIComponent(query)}`);
			if (response.ok) {
				const data = await response.json();
				suggestions = data.ingredients || [];
				showSuggestions = suggestions.length > 0;
			}
		} catch (error) {
			console.error('Error fetching ingredient suggestions:', error);
			suggestions = [];
			showSuggestions = false;
		}
	}

	function handleInput() {
		showSuggestions = true;
		if (debounceTimer) clearTimeout(debounceTimer);
		debounceTimer = setTimeout(fetchSuggestions, 200);
	}

	function selectIngredient(ing: { id: string; name: string; category: string; default_unit: string }) {
		if (!selected.includes(ing.id)) {
			selected = [...selected, ing.id];
			onChange(selected);
		}
		query = '';
		suggestions = [];
		showSuggestions = false;
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter') {
			e.preventDefault();
		} else if (e.key === 'Escape') {
			showSuggestions = false;
		}
	}
</script>

<div class="relative">
	<div class="flex flex-wrap gap-1.5 mb-2" role="group" aria-label="Ingredientes seleccionados">
		{#each selected as ingId}
			<span class="badge bg-muted text-muted-foreground flex items-center gap-1" role="option" aria-selected="true">
				{ingId}
				<button
					type="button"
					class="ml-1 p-0.5 hover:bg-muted-foreground/20 rounded"
					on:click={() => { selected = selected.filter(s => s !== ingId); onChange(selected); }}
					aria-label="Quitar ingrediente {ingId}"
				>
					<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
				</button>
			</span>
		{/each}
	</div>

	<div class="relative">
		<input
			type="text"
			bind:value={query}
			placeholder="Buscar ingredientes..."
			class="input-base pr-8"
			on:input={handleInput}
			on:keydown={handleKeydown}
			on:focus={() => showSuggestions = true}
			on:blur={() => setTimeout(() => showSuggestions = false, 200)}
			aria-autocomplete="list"
			aria-controls="ingredient-suggestions"
			aria-expanded={showSuggestions}
			aria-owns="ingredient-suggestions"
		/>
		{#if showSuggestions && suggestions.length > 0}
			<ul
				id="ingredient-suggestions"
				class="absolute z-50 w-full mt-1 bg-popover border border-border rounded-lg shadow-lg max-h-60 overflow-y-auto"
				role="listbox"
				aria-label="Sugerencias de ingredientes"
			>
				{#each suggestions as ing}
					<button
						type="button"
						role="option"
						class="w-full px-3 py-2 text-left text-sm hover:bg-accent flex flex-col gap-1"
						on:click={() => selectIngredient(ing)}
					>
						<span class="font-medium">{ing.name}</span>
						<span class="text-xs text-muted-foreground flex items-center gap-1">
							<span class="px-1.5 py-0.5 text-xs bg-muted rounded">{ing.category}</span>
							<span class="text-muted-foreground">({ing.default_unit})</span>
						</span>
					</button>
				{/each}
			</ul>
		{/if}
	</div>