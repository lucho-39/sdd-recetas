<script lang="ts">
	export let author: {
		id: string;
		display_name: string;
		avatar_url?: string | null;
	} | null = null;
	export let size: 'xs' | 'sm' | 'md' | 'lg' = 'sm';
	export let href: string | undefined = undefined;

	const sizes = {
		xs: 'h-6 w-6 text-[0.625rem]',
		sm: 'h-8 w-8 text-xs',
		md: 'h-10 w-10 text-sm',
		lg: 'h-12 w-12 text-base'
	} as const;

	const name = author?.display_name ?? 'Usuario';

	function getInitials(value: string): string {
		return value
			.split(' ')
			.filter(Boolean)
			.map((n) => n[0])
			.slice(0, 2)
			.join('')
			.toUpperCase();
	}

	function getColor(value: string): string {
		let hash = 0;
		for (let i = 0; i < value.length; i++) hash = value.charCodeAt(i) + ((hash << 5) - hash);
		return `hsl(${Math.abs(hash) % 360}, 55%, 45%)`;
	}
</script>

<svelte:element
	this={href ? 'a' : 'span'}
	{href}
	class="inline-flex shrink-0 items-center justify-center overflow-hidden rounded-full {sizes[size]}"
	style={author?.avatar_url ? '' : `background-color: ${getColor(name)};`}
	aria-label={href ? `Ver perfil de ${name}` : undefined}
	title={name}
>
	{#if author?.avatar_url}
		<img src={author.avatar_url} alt="" class="h-full w-full object-cover" />
	{:else}
		<span class="font-medium text-white" aria-hidden="true">{getInitials(name)}</span>
	{/if}
</svelte:element>
