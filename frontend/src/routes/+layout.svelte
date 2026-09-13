<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import Navbar from '$components/layout/Navbar.svelte';
	import Footer from '$components/layout/Footer.svelte';
	import { theme } from '$lib/stores/theme';
	import { auth } from '$lib/stores/auth';
	import { notifications } from '$lib/stores/notifications';

	onMount(() => {
		theme.init();
		auth.init();
		notifications.start();
		if ('serviceWorker' in navigator) {
			navigator.serviceWorker.register('/service-worker.js').catch(() => {});
		}
	});
</script>

<div class="flex min-h-screen flex-col bg-background text-foreground">
	<Navbar />
	<main id="main-content" class="flex-1">
		<slot />
	</main>
	<Footer />
</div>
