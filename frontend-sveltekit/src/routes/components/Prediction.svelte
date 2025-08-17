<script>
	export let item = "";
</script>

<div>
	{#if item === ""}
		<p>Computing ... </p>
	{:else}
	<div class="w-1/2">
		<h1 class="text-xl font-bold">
			Uniprot Id: {item} 
			<!-- {item.uniprot_id} -->
		</h1>
		<hr />
		<p class="text-sm">
			<!-- {item.sequence} -->
			Prediction: {item} 
		</p>
	</div>
	{/if}
</div>
