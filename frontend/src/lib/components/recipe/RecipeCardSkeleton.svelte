<div class="group relative flex flex-col h-full bg-card rounded-xl border border-border shadow-sm overflow-hidden animate-pulse">
	<!-- Imagen skeleton -->
	<div class="aspect-[4/3] w-full bg-muted">
		<div class="w-full h-full animate-shimmer"></div>
	</div>

	<!-- Contenido skeleton -->
	<div class="flex-1 flex flex-col p-4 space-y-3">
		<!-- Tags skeleton -->
		<div class="flex flex-wrap gap-1.5">
			<div class="h-5 w-20 bg-muted animate-shimmer rounded-full"></div>
			<div class="h-5 w-20 bg-muted animate-shimmer rounded-full"></div>
		</div>

		<!-- Título skeleton -->
		<div class="h-6 w-3/4 bg-muted animate-shimmer rounded"></div>
		<div class="h-6 w-1/2 bg-muted animate-shimmer rounded"></div>

		<!-- Meta skeleton -->
		<div class="flex items-center gap-3 text-sm">
			<div class="h-4 w-24 bg-muted animate-shimmer rounded"></div>
			<div class="h-4 w-20 bg-muted animate-shimmer rounded"></div>
			<div class="h-4 w-20 bg-muted animate-shimmer rounded"></div>
			<div class="w-8 h-8 rounded-full bg-muted animate-shimmer"></div>
		</div>
	</div>
</div>

<style>
	:global(.animate-shimmer) {
		animation: shimmer 1.8s infinite linear;
		background: linear-gradient(90deg,
			hsl(var(--muted)) 25%,
			hsl(var(--muted-foreground) / 0.08) 50%,
			hsl(var(--muted)) 75%
		);
		background-size: 200% 100%;
	}

	@keyframes shimmer {
		0% { background-position: -200% 0; }
		100% { background-position: 200% 0; }
	}
</style>