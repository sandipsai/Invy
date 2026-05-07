<script>
  import Dashboard from '$lib/pages/Dashboard.svelte';
  import { goto } from '$app/navigation';

  /** @type {import('./$types').PageData} */
  export let data;
</script>

<Dashboard
  stats={data.stats}
  recentInvoices={data.recentInvoices}
  activityItems={data.activityItems}
  on:navigate={e => goto(`/${e.detail.page}`)}
  on:upgrade={() => goto('/settings')}
/>