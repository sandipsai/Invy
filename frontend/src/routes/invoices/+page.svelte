<script>
  import Invoices from '$lib/pages/Invoices.svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';

  /** @type {import('./$types').PageData} */
  export let data;

  function onNavigate(e) {
    goto(`/${e.detail.page}`);
  }

  function onTab(e) {
    const params = new URLSearchParams($page.url.searchParams);
    params.set('status', e.detail.tab);
    params.delete('page');
    goto(`?${params}`);
  }

  function onPageChange(e) {
    const params = new URLSearchParams($page.url.searchParams);
    params.set('page', e.detail.page);
    goto(`?${params}`);
  }

  function onDateRange(e) {
    const params = new URLSearchParams($page.url.searchParams);
    params.set('dateRange', e.detail.value);
    params.delete('page');
    goto(`?${params}`);
  }
</script>

<Invoices
  invoices={data.invoices}
  activeTab={data.activeTab}
  currentPage={data.currentPage}
  perPage={data.perPage}
  total={data.total}
  on:navigate={onNavigate}
  on:tab={onTab}
  on:pageChange={onPageChange}
  on:dateRange={onDateRange}
  on:action={e => goto(`/invoices/${e.detail.invoice._raw.id}`)}
/>