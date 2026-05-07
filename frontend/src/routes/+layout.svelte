<script>
  import AppShell from '$lib/layout/AppShell.svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';

  /** @type {import('./$types').LayoutData} */
  export let data;

  // Derive the active sidebar key from the current URL path.
  // e.g. /invoices/new → 'invoices', /dashboard → 'dashboard'
  $: activePage = $page.url.pathname.split('/').filter(Boolean)[0] ?? 'dashboard';

  function onNavigate(e) {
    const dest = e.detail.page;
    // 'create' maps to /invoices/new
    if (dest === 'create') {
      goto('/invoices/new');
    } else {
      goto(`/${dest}`);
    }
  }
</script>

<AppShell
  {activePage}
  userName={data.profile.businessName}
  on:navigate={onNavigate}
  on:logout={() => goto('/auth/logout')}
  on:search={e => goto(`/invoices?search=${encodeURIComponent(e.detail.value)}`)}
>
  <slot />
</AppShell>