<script lang="ts">
	import PublicProfile from '$components/profile/PublicProfile.svelte';

	export let data;
</script>

<PublicProfile profile={data.profile} recipes={data.recipes} />
