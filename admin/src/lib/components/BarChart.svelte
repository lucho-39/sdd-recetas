<script lang="ts">
	export let title = '';
	export let data: { label: string; count: number }[] = [];
	export let height = 180;

	$: max = Math.max(1, ...data.map((d) => d.count));
	$: total = data.reduce((sum, d) => sum + d.count, 0);
	$: barMax = height - 44;

	function barHeight(count: number): number {
		if (count <= 0) return 0;
		return Math.max(3, Math.round((count / max) * barMax));
	}
</script>

<div class="card p-4">
	<div class="mb-4 flex items-baseline justify-between">
		<h3 class="text-sm font-medium text-foreground">{title}</h3>
		<span class="text-xs text-muted-foreground">{total} en total</span>
	</div>

	{#if data.length === 0}
		<p class="py-8 text-center text-sm text-muted-foreground">Sin datos</p>
	{:else}
		<div
			class="flex items-end gap-2 overflow-x-auto"
			style="height: {height}px"
			role="img"
			aria-label={`${title}: ${data.map((d) => `${d.label} ${d.count}`).join(', ')}`}
		>
			{#each data as d (d.label)}
				<div class="flex min-w-[1.75rem] flex-1 flex-col items-center justify-end gap-1" title={`${d.label}: ${d.count}`}>
					<span class="text-[10px] font-medium text-muted-foreground">{d.count}</span>
					<div class="w-full rounded-t bg-primary" style="height: {barHeight(d.count)}px"></div>
				</div>
			{/each}
		</div>
		<div class="mt-2 flex gap-2 overflow-x-auto">
			{#each data as d (d.label)}
				<span class="min-w-[1.75rem] flex-1 truncate text-center text-[10px] text-muted-foreground">{d.label}</span>
			{/each}
		</div>
	{/if}
</div>
