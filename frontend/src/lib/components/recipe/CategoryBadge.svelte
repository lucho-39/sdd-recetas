<script lang="ts">
	export let category: {
		id: string;
		name: string;
		icon?: string | null;
		color: string;
		slug: string;
	};
	export let className = '';
</script>

<span
	class="badge {className}"
	style="background-color: {category.color}1f; color: {category.color}; border: 1px solid {category.color}40;"
>
	{#if category.icon}<span aria-hidden="true">{category.icon}</span>{/if}
	{category.name}
</span>
