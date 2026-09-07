<script lang="ts">
	export let value: number = 0;
	export let count: number = 0;
	export let size: 'xs' | 'sm' | 'md' | 'lg' = 'sm';
	export let showCount = false;
	export let interactive = false;
	export let onChange: (value: number) => void = () => {};

	const sizes = {
		xs: 'w-3 h-3',
		sm: 'w-4 h-4',
		md: 'w-5 h-5',
		lg: 'w-6 h-6',
	};

	$: fullStars = Math.floor(value);
	$: fraction = value % 1;
	$: hasHalf = fraction >= 0.25 && fraction < 0.75;
	$: hasPartial = fraction >= 0.75;

	function getStarAriaLabel(index: number): string {
		if (index < fullStars) return 'Estrella completa';
		if (index === fullStars && hasHalf) return 'Media estrella';
		if (index === fullStars && hasPartial) return 'Estrella casi completa';
		return 'Estrella vacía';
	}

	function handleClick(index: number) {
		if (!interactive) return;
		const newValue = index + 1;
		onChange(newValue);
	}
</script>

<div
	class="inline-flex items-center gap-0.5"
	role="img"
	aria-label="Calificación: {value.toFixed(2)} de 5 estrellas{count ? ', ' + count + ' reseñas' : ''}"
>
	{#each Array(5) as _, index}
		<button
			type="button"
			class={sizes[size]}
			aria-label={getStarAriaLabel(index)}
			aria-pressed={interactive && index < value}
			on:click={() => handleClick(index)}
			disabled={!interactive}
			style="color: {index < fullStars || (index === fullStars && (hasHalf || hasPartial)) ? 'var(--rating)' : 'currentColor'}"
		>
			{#if index < fullStars}
				<svg class={sizes[size]} fill="currentColor" viewBox="0 0 24 24"><path d="M12 2l3.09 6.26L24 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7.19 18.7l5.58-.94L6.09 9.42 12 3.27z"/></svg>
			{:else if index === fullStars && hasHalf}
				<svg class={sizes[size]} viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l3.09 6.26L24 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7.19 18.7l5.58-.94L6.09 9.42 12 3.27z"/></svg>
			{:else if index === fullStars && hasPartial}
				<svg class={sizes[size]} viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l3.09 6.26L24 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7.19 18.7l5.58-.94L6.09 9.42 12 3.27z"/></svg>
			{:else}
				<svg class={sizes[size]} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2l3.09 6.26L24 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7.19 18.7l5.58-.94L6.09 9.42 12 3.27z"/></svg>
			{/if}
		<button>
	{/each}

	{#if showCount && count > 0}
		<span class="ml-1 text-sm text-muted-foreground">({count})</span>
	{/if}

<style>
	:global(.rating-stars) {
		@apply inline-flex items-center gap-0.5;
	}
	:global(.rating-stars button) {
		@apply transition-colors duration-150;
	}
	:global(.rating-stars button:disabled) {
		@apply cursor-not-allowed;
	}
	:global(.rating-stars button:not(:disabled):hover) {
		@apply scale-110;
	}
</style>