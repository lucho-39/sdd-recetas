<script lang="ts">
	import { onMount } from 'svelte';

	export let selected: string[] = [];
	export let onChange: (tags: string[]) => void;
	export let placeholder = 'Buscar etiquetas...';
	export let maxTags = 10;

	let query = '';
	let showSuggestions = false;
	let suggestions: { slug: string; name: string; usage_count: number }[] = [];
	let debounceTimer: ReturnType<typeof setTimeout>;

	async function fetchSuggestions() {
		if (query.length < 2) {
			suggestions = [];
			showSuggestions = false;
			return;
		}
		try {
			const response = await fetch(`/api/v1/tags?query=${encodeURIComponent(query)}&limit=10`);
			if (response.ok) {
				const data = await response.json();
				suggestions = Array.isArray(data) ? data : [];
				showSuggestions = suggestions.length > 0;
			}
		} catch (error) {
			console.error('Error fetching tag suggestions:', error);
			suggestions = [];
			showSuggestions = false;
		}
	}

	function handleInput() {
		showSuggestions = true;
		if (debounceTimer) clearTimeout(debounceTimer);
		debounceTimer = setTimeout(fetchSuggestions, 200);
	}

	function selectTag(tag: { slug: string; name: string }) {
		if (!selected.includes(tag.slug)) {
			selected = [...selected, tag.slug];
			onChange(selected);
		}
		query = '';
		suggestions = [];
		showSuggestions = false;
	}

	function createTag() {
		if (!query.trim()) return;
		const slug = query.trim().toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
		if (!selected.includes(slug)) {
			selected = [...selected, slug];
			onChange(selected);
		}
		query = '';
		suggestions = [];
		showSuggestions = false;
	}

	function removeTag(slug: string) {
		selected = selected.filter(s => s !== slug);
		onChange(selected);
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter') {
			e.preventDefault();
			if (query.trim()) {
				createTag();
			}
		} else if (e.key === 'Escape') {
			showSuggestions = false;
		}
	}

	function handleBlur() {
		setTimeout(() => { showSuggestions = false; }, 200);
	}
</script>

<div class="relative">
	<div class="flex flex-wrap gap-1.5 mb-2" role="group" aria-label="Etiquetas seleccionadas">
		{#each selected as tagSlug}
			<span class="badge bg-muted text-muted-foreground flex items-center gap-1">
				{tagSlug}
				<button
					type="button"
					class="ml-1 p-0.5 hover:bg-muted-foreground/20 rounded"
					on:click={() => { selected = selected.filter(s => s !== tagSlug); onChange(selected); }}
					aria-label="Quitar etiqueta {tagSlug}"
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
			placeholder={placeholder}
			class="input-base pr-8"
			on:input={handleInput}
			on:keydown={handleKeydown}
			on:focus={() => showSuggestions = true}
			on:blur={() => setTimeout(() => showSuggestions = false, 200)}
			aria-autocomplete="list"
			aria-controls="tag-suggestions"
		/>
		{#if showSuggestions && suggestions.length > 0}
			<ul
				id="tag-suggestions"
				class="absolute z-50 w-full mt-1 bg-popover border border-border rounded-lg shadow-lg max-h-60 overflow-y-auto"
				role="listbox"
				aria-label="Sugerencias de etiquetas"
			>
				{#each suggestions as suggestion}
					<button
						type="button"
						role="option"
						aria-selected="false"
						class="w-full px-3 py-2 text-left text-sm hover:bg-accent flex items-center gap-2"
						on:click={() => selectTag(suggestion)}
					>
						<span class="font-medium">{suggestion.name}</span>
						<span class="text-xs text-muted-foreground">{suggestion.usage_count} usos</span>
					</button>
				{/each}
				{#if query && suggestions.length === 0}
					<button
						type="button"
						class="w-full px-3 py-2 text-left text-sm text-primary hover:bg-accent"
						on:click={() => { selectTag({ slug: query.trim().toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, ''), name: query.trim() }); }}
					>
						Crear "{query.trim()}"
					</button>
				{/if}
			</ul>
		{/if}
	</div>
</div>

<style>
	:global(.tag-autocomplete) {
		@apply relative;
	}
</style>