<script lang="ts">
	import { IconChefHatFilled as ChefHat } from '@tabler/icons-svelte';
</script>

<section class="hero relative py-20 md:py-32 overflow-hidden">
	<div class="absolute inset-0 bg-gradient-to-br from-primary/5 via-background to-secondary/5" />
	<div class="absolute inset-0 bg-[url('/grid.svg')] opacity-[0.03]" />
	<div class="relative container">
		<div class="max-w-3xl mx-auto text-center">
			<div class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary border border-primary/20 mb-6 text-sm font-medium">
				<ChefHat class="h-4 w-4" />
				<span>Recetario IA - Tu libro de recetas inteligente</span>
			</div>
			<h1 class="text-4xl md:text-5xl lg:text-6xl font-playfair font-medium text-foreground mb-6 leading-tight">
				Descubre, crea y comparte<br />
				<span class="text-primary">recetas deliciosas</span>
			</h1>
			<p class="text-lg md:text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
				Tu asistente culinario personal. Encuentra recetas por ingredientes,
				categorías o preferencias. Guarda tus favoritas y califica las que pruebes.
			</p>
			<div class="flex flex-col sm:flex-row items-center justify-center gap-4">
				<a
					href="/recipes"
					class="btn btn-primary btn-lg w-full sm:w-auto"
				>
					Explorar recetas
				</a>
				<a
					href="/recipes/new"
					class="btn btn-outline btn-lg w-full sm:w-auto"
				>
					Crear receta
				</a>
			</div>
		</div>
		<div class="mt-16 grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
			<div>
				<div class="text-3xl md:text-4xl font-bold text-foreground">500+</div>
				<div class="text-sm text-muted-foreground mt-1">Recetas</div>
			</div>
			<div>
				<div class="text-3xl md:text-4xl font-bold text-foreground">50+</div>
				<div class="text-sm text-muted-foreground mt-1">Categorías</div>
			</div>
			<div>
				<div class="text-3xl md:text-4xl font-bold text-foreground">10k+</div>
				<div class="text-sm text-muted-foreground mt-1">Usuarios</div>
			</div>
			<div>
				<div class="text-3xl md:text-4xl font-bold text-foreground">4.8★</div>
				<div class="text-sm text-muted-foreground mt-1">Valoración</div>
			</div>
		</div>
	</div>
</section>

<style>
	.hero {
		@apply relative;
	}
</style>