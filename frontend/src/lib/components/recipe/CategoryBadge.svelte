<script lang="ts">
	export let category: {
		id: string;
		name: string;
		icon?: string;
		color: string;
		slug: string;
	};
	export let variant: 'outline' | 'solid' = 'outline';
	export let size: 'sm' | 'md' | 'lg' = 'md';
	export let class: string = '';
</script>

<span
	class:badge
	class:badge-category
	class="inline-flex items-center gap-1 font-medium rounded-full px-2.5 py-0.5 text-sm
		{variant === 'outline'
			? 'bg-transparent border-[{category.color}] text-white [&>svg]:stroke-[{category.color}]'
			: 'bg-[{category.color}] text-white'}"
	style="--badge-color: {category.color};"
	class={class}
>
	{#if category.icon}
		<span aria-hidden="true">{category.icon}</span>
	{/if}
	{category.name}
</span>

<style>
	:global(.badge) {
		@apply inline-flex items-center gap-1 font-medium rounded-full px-2.5 py-0.5 text-sm;
	}

	:global(.badge-category) {
		@apply transition-colors;
	}
</style>