<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { theme } from '$lib/stores/theme';
	import { auth } from '$lib/stores/auth';
	import { Navbar } from '$components/layout/Navbar.svelte';
	import { Footer } from '$components/layout/Footer.svelte';
	import { ToastContainer } from '$components/ui/Toast.svelte';

	let mounted = false;

	onMount(() => {
		mounted = true;
		theme.init();
		auth.init();
	});
</script>

<div class="min-h-screen flex flex-col" class:data-theme={$theme.current}>
	<Navbar />
	<main class="flex-1" id="main-content">
		<slot />
	</main>
	<Footer />
	<ToastContainer />
</div>

<style>
	:global(*) {
		margin: 0;
		padding: 0;
		box-sizing: border-box;
	}

	:global(html) {
		font-size: 16px;
		scroll-behavior: smooth;
	}

	:global(body) {
		@apply bg-background text-foreground font-sans antialiased;
		font-feature-settings: "cv02", "cv03", "cv04", "cv11";
	}

	:global(:root) {
		--font-sans: 'Inter', system-ui, -apple-system, sans-serif;
		--font-serif: 'Playfair Display', Georgia, serif;
		--font-mono: 'JetBrains Mono', monospace;
	}