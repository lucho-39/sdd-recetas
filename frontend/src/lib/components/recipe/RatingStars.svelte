<script lang="ts">
	export let value = 0;
	export let count = 0;
	export let size: 'xs' | 'sm' | 'md' | 'lg' = 'sm';
	export let showCount = false;

	const sizeMap = {
		xs: 'h-3 w-3',
		sm: 'h-4 w-4',
		md: 'h-5 w-5',
		lg: 'h-6 w-6'
	} as const;

	const starPath =
		'M12 2.5l2.95 5.98 6.6.96-4.78 4.66 1.13 6.57L12 17.77l-5.9 3.9 1.13-6.57L2.45 9.44l6.6-.96L12 2.5z';

	function starFill(index: number): number {
		const diff = value - index;
		if (diff >= 1) return 100;
		if (diff <= 0) return 0;
		return Math.round(diff * 100);
	}
</script>

<div
	class="inline-flex items-center gap-0.5"
	role="img"
	aria-label={`Calificación: ${value.toFixed(2)} de 5${count ? `, ${count} reseñas` : ''}`}
>
	{#each [0, 1, 2, 3, 4] as i}
		<span class="relative inline-block {sizeMap[size]}">
			<svg class="{sizeMap[size]} absolute inset-0 text-muted-foreground/40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
				<path d={starPath} />
			</svg>
			<span class="absolute inset-0 overflow-hidden" style="width: {starFill(i)}%">
				<svg class="{sizeMap[size]} text-rating" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
					<path d={starPath} />
				</svg>
			</span>
		</span>
	{/each}
	{#if showCount}
		<span class="ml-1 text-sm text-muted-foreground">({count})</span>
	{/if}
</div>
