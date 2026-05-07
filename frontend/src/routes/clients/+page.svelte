<script>
  import Clients from '$lib/pages/Clients.svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';

  /** @type {import('./$types').PageData} */
  export let data;

  function onSearch(e) {
    const params = new URLSearchParams($page.url.searchParams);
    if (e.detail.value) {
      params.set('search', e.detail.value);
    } else {
      params.delete('search');
    }
    goto(`?${params}`);
  }
</script>

<Clients
  clients={data.clients}
  on:selectClient={e => goto(`/clients/${e.detail.client._raw.id}`)}
  on:addClient={() => goto('/clients/new')}
  on:search={onSearch}
/>