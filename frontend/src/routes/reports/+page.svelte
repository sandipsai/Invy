<script>
  import StatGrid           from '$lib/components/StatGrid.svelte';
  import StatCard           from '$lib/components/StatCard.svelte';
  import Card               from '$lib/primitives/Card.svelte';
  import HorizontalBarChart from '$lib/components/HorizontalBarChart.svelte';
  import Button             from '$lib/primitives/Button.svelte';

  /** @type {import('./$types').PageData} */
  export let data;

  $: s = data.stats;
</script>

<div class="page">

  <div class="page-header">
    <div>
      <h1 class="page-title">Reports</h1>
      <p class="page-sub">Financial summaries, tax overviews, and payment analytics.</p>
    </div>
    <Button variant="outline">↓ Download PDF</Button>
  </div>

  <StatGrid cols={3}>
    <StatCard
      label="Total Revenue"
      value={s.ytdRevenue}
      meta="All time"
    />
    <StatCard
      label="Outstanding"
      value={s.outstanding}
      meta="{s.overdueCount} overdue"
      valueWarning={s.overdueCount > 0}
    />
    <StatCard
      label="Total Invoices"
      value={String(s.totalInvoices)}
      meta="{s.paidCount} paid · {s.overdueCount} overdue"
    />
  </StatGrid>

  <Card>
    <svelte:fragment slot="header">
      <span class="card-title">Revenue by Client</span>
      <span class="sub">{data.revenueByClient.length} clients</span>
    </svelte:fragment>

    {#if data.revenueByClient.length > 0}
      <HorizontalBarChart rows={data.revenueByClient} labelWidth="150px" />
    {:else}
      <div class="empty">No client revenue data yet.</div>
    {/if}
  </Card>

</div>

<style>
  .page { padding: 28px; max-width: 1100px; }

  .page-header {
    display: flex; align-items: flex-start;
    justify-content: space-between; gap: 16px;
    margin-bottom: 24px; flex-wrap: wrap;
  }

  .page-title { font-size: 22px; font-weight: 600; color: var(--text-primary); line-height: 1.2; }
  .page-sub   { font-size: 13px; color: var(--text-muted); margin-top: 4px; }

  .card-title { font-size: 14px; font-weight: 600; color: var(--text-primary); }
  .sub        { font-size: 12px; color: var(--text-muted); }

  .empty { padding: 32px; text-align: center; font-size: 13px; color: var(--text-muted); }
</style>