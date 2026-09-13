<script lang="ts">
	import { goto } from '$app/navigation';
	import CookingStepper from '$components/cooking/CookingStepper.svelte';

	export let data;

	function exit() {
		goto(`/receta/${data.recipe.slug}`);
	}
</script>

<svelte:head>
	<title>Cocinando: {data.recipe.title} — Recetario IA</title>
	<meta name="robots" content="noindex" />
</svelte:head>

<CookingStepper recipe={data.recipe} steps={data.steps} onExit={exit} />
