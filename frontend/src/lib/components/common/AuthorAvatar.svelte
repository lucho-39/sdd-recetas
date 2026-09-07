<script lang="ts">
	export let author: {
		id: string;
		display_name: string;
		avatar_url?: string;
	} | null = null;
	export let size: 'xs' | 'sm' | 'md' | 'lg' = 'sm';
	export let href: string | undefined = undefined;

	const sizes = {
		xs: 'w-6 h-6',
		sm: 'w-8 h-8',
		md: 'w-10 h-10',
		lg: 'w-12 h-12',
	};

	function getInitials(name: string): string {
		return name
			.split(' ')
			.map(n => n[0])
			.slice(0, 2)
			.join('')
			.toUpperCase();
	}

	function getColor(name: string): string {
		let hash = 0;
		for (let i = 0; i < name.length; i++) {
			hash = name.charCodeAt(i) + ((hash << 5) - hash);
		}
		const hue = Math.abs(hash) % 360;
		return `hsl(${hue}, 65%, 55%)`;
	}
</script>

{#if href}
	<a href={href} class="block" aria-label="Ver perfil de {author?.display_name || 'Usuario'}">
		{@render avatar()}
	</a>
{:else}
	{@render avatar()}
{/if}

{#snippet avatar()}
	<div class={sizes[size]} aria-hidden="true">
		{#if author?.avatar_url}
			<img
				src={author.avatar_url}
				alt=""
				class="w-full h-full rounded-full object-cover"
			/>
		{:else}
			<div
				class="w-full h-full rounded-full flex items-center justify-center font-medium text-white text-center"
				style="background-color: {getColor(author?.display_name || 'Usuario')}; font-size: {size === 'xs' ? '0.5rem' : size === 'sm' ? '0.625rem' : size === 'md' ? '0.75rem' : '1rem'};"
			>
				{getInitials(author?.display_name || 'U')}
			</div>
		{/if}
	</div>
</script>