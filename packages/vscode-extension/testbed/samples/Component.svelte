<script lang="ts">
  export let viewOnly: boolean = false;
  const human = "HUMAN_HIGHLIGHT";
  function goBack() { window.history.back(); }
</script>

<section class="wrap">
  <h2>{human}</h2>
  {#if !viewOnly}
    <button on:click={goBack}>Back</button>
  {:else}
    <p>Read-only</p>
  {/if}
</section>

<style>
  .wrap { padding: 12px; }
</style>
