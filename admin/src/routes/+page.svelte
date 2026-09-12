<script lang="ts">
	import { onMount } from 'svelte';

	let ready = false;

	onMount(() => {
		ready = true;
	});
</script>

<svelte:head>
	<title>Recetario IA — Admin</title>
</svelte:head>

<main class="splash">
	<div class="splash-card">
		<span class="splash-badge">Admin</span>
		<h1 class="splash-title">Panel de Administración</h1>
		<p class="splash-subtitle">
			Gestión de categorías, usuarios, ingredientes y métricas de Recetario IA.
		</p>
		<p class="splash-status" class:is-ready={ready}>
			{ready ? 'Admin en línea' : 'Iniciando…'}
		</p>
		<div class="splash-actions">
			<a class="splash-link" href="http://localhost:3000">Ir a la app</a>
			<a class="splash-link" href="http://localhost:8000/docs">API Docs</a>
		</div>
	</div>
</main>

<style>
	.splash {
		min-height: 100vh;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 2rem;
		background: #1c1a18;
		color: #e8e5e1;
		font-family: 'Inter', system-ui, -apple-system, sans-serif;
	}

	.splash-card {
		max-width: 32rem;
		text-align: center;
		background: #24211f;
		border: 1px solid #3d3935;
		border-radius: 6px;
		padding: 3rem 2rem;
	}

	.splash-badge {
		display: inline-block;
		font-size: 0.75rem;
		font-weight: 600;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: #c8c4bc;
		background: #2a2724;
		border-radius: 2px;
		padding: 0.25rem 0.6rem;
	}

	.splash-title {
		font-family: 'Playfair Display', Georgia, serif;
		font-size: 2.25rem;
		font-weight: 500;
		margin: 1.25rem 0 0.75rem;
		color: #c8c4bc;
	}

	.splash-subtitle {
		font-size: 1rem;
		line-height: 1.6;
		color: #a8a4a0;
		margin: 0 0 1.5rem;
	}

	.splash-status {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 0.875rem;
		color: #d4a84a;
		margin-bottom: 2rem;
	}

	.splash-status::before {
		content: '';
		width: 0.5rem;
		height: 0.5rem;
		border-radius: 9999px;
		background: #d4a84a;
	}

	.splash-status.is-ready {
		color: #7ab86a;
	}

	.splash-status.is-ready::before {
		background: #7ab86a;
	}

	.splash-actions {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 0.75rem;
	}

	.splash-link {
		font-size: 0.875rem;
		font-weight: 500;
		color: #c8c4bc;
		text-decoration: none;
		border: 1px solid #3d3935;
		border-radius: 4px;
		padding: 0.5rem 1rem;
		transition: background 0.15s ease, border-color 0.15s ease;
	}

	.splash-link:hover {
		background: #2a2724;
		border-color: #8f8c84;
	}
</style>
