<script lang="ts">
	import { Search, Heart, Utensils, BookOpen, AlertCircle } from 'lucide-svelte';

	export let variant: 'search' | 'favorites' | 'recipes' | 'categories' | 'tags' = 'search';
	export let title: string = '';
	export let description: string = '';
	export let actionLabel: string = '';
	export let actionHref: string = '';

	function getConfig() {
		switch (variant) {
			case 'search':
				return {
					icon: Search,
					defaultTitle: 'No se encontraron recetas',
					defaultDescription: 'Intenta cambiar los filtros o busca con otros términos',
					defaultActionLabel: 'Limpiar filtros',
					defaultActionHref: '/recipes',
				};
			case 'favorites':
				return {
					icon: Heart,
					defaultTitle: 'No tienes recetas guardadas',
					defaultDescription: 'Empieza a explorar y guarda tus recetas favoritas',
					defaultActionLabel: 'Explorar recetas',
					defaultActionHref: '/recipes',
				};
			case 'recipes':
				return {
					icon: Utensils,
					defaultTitle: 'No hay recetas disponibles',
					defaultDescription: 'Sé el primero en crear una receta en esta categoría',
					defaultActionLabel: 'Crear receta',
					defaultActionHref: '/recipes/new',
				};
			case 'categories':
				return {
					icon: BookOpen,
					defaultTitle: 'No hay categorías',
					defaultDescription: 'Las categorías aparecerán aquí cuando se agreguen recetas',
					defaultActionLabel: 'Ver recetas',
					defaultActionHref: '/recipes',
				};
			case 'tags':
				return {
					icon: AlertCircle,
					defaultTitle: 'No hay etiquetas',
					defaultDescription: 'Las etiquetas aparecerán cuando se usen en recetas',
					defaultActionLabel: 'Ver recetas',
					defaultActionHref: '/recipes',
				};
		}
	}

	const config = getConfig();
	const finalTitle = title || config.defaultTitle;
	const finalDescription = description || config.defaultDescription;
	const finalActionLabel = actionLabel || config.defaultActionLabel;
	const finalActionHref = actionHref || config.defaultActionHref;
	const Icon = config.icon;
</script>

<div class="empty-state flex flex-col items-center justify-center py-16 px-4 text-center">
	<div class="empty-state-icon mb-6 text-muted-foreground/50">
		<Icon class="h-16 w-16" />
	</div>
	<h3 class="text-xl font-playfair font-medium text-foreground mb-2">{finalTitle}</h3>
	<p class="text-muted-foreground mb-6 max-w-md">{finalDescription}</p>
	{#if finalActionLabel && finalActionHref}
		<a href={finalActionHref} class="btn btn-primary">
			{finalActionLabel}
		</a>
	{/if}
</div>

<style>
	.empty-state {
		@apply min-h-[300px];
	}
</style>