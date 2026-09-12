<script lang="ts">
	import { onMount } from 'svelte';

	let ready = false;

	onMount(() => {
		ready = true;
	});
</script>

<svelte:head>
	<title>Recetario IA</title>
</svelte:head>

<main class="splash">
	<div class="splash-card">
		<span class="splash-badge">MVP</span>
		<h1 class="splash-title">Recetario IA</h1>
		<p class="splash-subtitle">
			Donde cada ingrediente cuenta una historia y cada receta nace del corazón.
		</p>
		<p class="splash-status" class:is-ready={ready}>
			{ready ? 'Frontend en línea' : 'Iniciando…'}
		</p>
		<div class="splash-actions">
			<a class="splash-link" href="http://localhost:8000/docs">API Docs</a>
			<a class="splash-link" href="http://localhost:8000/health">Backend Health</a>
			<a class="splash-link" href="http://localhost:3001">Panel Admin</a>
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
		background: #faf9f6;
		color: #2d2b28;
		font-family: 'Inter', system-ui, -apple-system, sans-serif;
	}

	.splash-card {
		max-width: 32rem;
		text-align: center;
		background: #ffffff;
		border: 1px solid #e8e4df;
		border-radius: 6px;
		padding: 3rem 2rem;
		box-shadow: 0 1px 3px rgba(61, 64, 52, 0.08);
	}

	.splash-badge {
		display: inline-block;
		font-size: 0.75rem;
		font-weight: 600;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: #3d4034;
		background: #f0ede8;
		border-radius: 2px;
		padding: 0.25rem 0.6rem;
	}

	.splash-title {
		font-family: 'Playfair Display', Georgia, serif;
		font-size: 2.5rem;
		font-weight: 500;
		margin: 1.25rem 0 0.75rem;
		color: #3d4034;
	}

	.splash-subtitle {
		font-size: 1rem;
		line-height: 1.6;
		color: #6b6762;
		margin: 0 0 1.5rem;
	}

	.splash-status {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 0.875rem;
		color: #c47a2a;
		margin-bottom: 2rem;
	}

	.splash-status::before {
		content: '';
		width: 0.5rem;
		height: 0.5rem;
		border-radius: 9999px;
		background: #c47a2a;
	}

	.splash-status.is-ready {
		color: #5a7d4a;
	}

	.splash-status.is-ready::before {
		background: #5a7d4a;
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
		color: #3d4034;
		text-decoration: none;
		border: 1px solid #e8e4df;
		border-radius: 4px;
		padding: 0.5rem 1rem;
		transition: background 0.15s ease, border-color 0.15s ease;
	}

	.splash-link:hover {
		background: #f0ede8;
		border-color: #3d4034;
	}
</style>
