<script lang="ts">
	export let type: 'text' | 'email' | 'password' | 'number' | 'search' = 'text';
	export let placeholder = '';
	export let value = '';
	export let disabled = false;
	export let required = false;
	export let id: string;
	export let label: string;
	export let error: string | undefined;
	export let autocomplete = 'off';
</script>

<div class="space-y-1.5">
	{#if label}
		<label for={id} class="label">{label}</label>
	{/if}
	<input
		type={type}
		id={id}
		bind:value
		placeholder={placeholder}
		disabled={disabled}
		required={required}
		class="input-base"
		aria-invalid={!!error}
		aria-describedby={error ? `${id}-error` : undefined}
	/>
	{#if error}
		<p id={id}-error class="text-sm text-destructive" role="alert">{error}</p>
	{/if}
</div>