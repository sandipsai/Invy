<script>
  import Card        from '$lib/primitives/Card.svelte';
  import Button      from '$lib/primitives/Button.svelte';
  import { enhance } from '$app/forms';
  import { goto }    from '$app/navigation';

  /** @type {import('./$types').ActionData} */
  export let form;

  // Restore field values on validation error so user doesn't retype
  $: v = form?.values ?? {};

  const currencies = ['USD','EUR','GBP','INR','JPY','CAD','AUD'];
</script>

<div class="page">

  <div class="page-header">
    <div class="header-left">
      <button class="back-btn" on:click={() => goto('/clients')}>← Clients</button>
      <h1 class="page-title">New Client</h1>
    </div>
  </div>

  {#if form?.error}
    <div class="error-banner">{form.error}</div>
  {/if}

  <form method="POST" action="?/create" use:enhance>
    <div class="form-section">
      <div class="section-header">
        <div class="section-icon">⊙</div>
        <span class="section-title">Client Details</span>
      </div>
      <div class="section-body">
        <div class="form-grid cols-2">

          <div class="form-field">
            <label class="field-label" for="cn-name">Name <span class="required">*</span></label>
            <input id="cn-name" class="form-input" name="name"
              value={v.name ?? ''} required placeholder="Jane Smith" />
          </div>

          <div class="form-field">
            <label class="field-label" for="cn-email">Email <span class="required">*</span></label>
            <input id="cn-email" class="form-input" name="email" type="email"
              value={v.email ?? ''} required placeholder="jane@acme.com" />
          </div>

          <div class="form-field">
            <label class="field-label" for="cn-phone">Phone</label>
            <input id="cn-phone" class="form-input" name="phone"
              value={v.phone ?? ''} placeholder="+1 212-555-0100" />
          </div>

          <div class="form-field">
            <label class="field-label" for="cn-company">Company</label>
            <input id="cn-company" class="form-input" name="company"
              value={v.company ?? ''} placeholder="Acme Corporation" />
          </div>

          <div class="form-field full">
            <label class="field-label" for="cn-address">Billing Address</label>
            <input id="cn-address" class="form-input" name="billing_address"
              value={v.billing_address ?? ''} placeholder="123 Main St, New York, NY 10001" />
          </div>

          <div class="form-field">
            <label class="field-label" for="cn-taxid">Tax ID</label>
            <input id="cn-taxid" class="form-input" name="tax_id"
              value={v.tax_id ?? ''} placeholder="US-12345678" />
          </div>

          <div class="form-field">
            <label class="field-label" for="cn-currency">Currency</label>
            <div class="select-wrap">
              <select id="cn-currency" class="form-input" name="currency">
                {#each currencies as cur}
                  <option value={cur} selected={v.currency === cur || (!v.currency && cur === 'USD')}>
                    {cur}
                  </option>
                {/each}
              </select>
            </div>
          </div>

          <div class="form-field full">
            <label class="field-label" for="cn-notes">Notes</label>
            <textarea id="cn-notes" class="form-input" name="notes"
              style="height:80px;resize:none;padding:8px"
              placeholder="Internal notes about this client…">{v.notes ?? ''}</textarea>
          </div>

        </div>
      </div>
    </div>

    <div class="form-actions">
      <Button variant="primary" type="submit">Create Client</Button>
      <Button variant="outline" on:click={() => goto('/clients')}>Cancel</Button>
    </div>
  </form>

</div>

<style>
  .page { padding: 28px; max-width: 680px; }

  .page-header    { display: flex; align-items: center; margin-bottom: 24px; }
  .header-left    { display: flex; align-items: center; gap: 12px; }
  .page-title     { font-size: 22px; font-weight: 600; color: var(--text-primary); }

  .back-btn { font-size: 13px; color: var(--text-muted); font-family: inherit; transition: color 0.12s; }
  .back-btn:hover { color: var(--accent); }

  .form-section {
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-sm);
    overflow: hidden;
    margin-bottom: 16px;
  }

  .section-header {
    display: flex; align-items: center; gap: 10px;
    padding: 14px 20px; border-bottom: 1px solid var(--border);
  }

  .section-icon {
    width: 24px; height: 24px; border-radius: 5px;
    background: var(--accent-soft); color: var(--accent);
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; flex-shrink: 0;
  }

  .section-title { font-size: 13.5px; font-weight: 600; color: var(--text-primary); }

  .section-body { padding: 18px 20px; }

  .form-grid { display: grid; gap: 14px; }
  .cols-2    { grid-template-columns: 1fr 1fr; }
  .full      { grid-column: 1 / -1; }

  @media (max-width: 560px) { .cols-2 { grid-template-columns: 1fr; } }

  .form-field  { display: flex; flex-direction: column; gap: 5px; }
  .field-label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); }
  .required    { color: var(--status-overdue-text); }
  .form-input  { height: 34px; padding: 0 10px; border-radius: var(--radius-sm); font-size: 13.5px; width: 100%; }

  .select-wrap { position: relative; }
  .select-wrap::after {
    content: '⌄'; position: absolute; right: 10px; top: 50%;
    transform: translateY(-55%); color: var(--text-muted); pointer-events: none;
  }
  .select-wrap .form-input { -webkit-appearance: none; appearance: none; padding-right: 28px; cursor: pointer; }

  .form-actions { display: flex; gap: 10px; }

  .error-banner {
    margin-bottom: 16px; padding: 10px 16px;
    background: var(--status-overdue-bg); color: var(--status-overdue-text);
    border: 1px solid currentColor; border-radius: var(--radius-sm); font-size: 13px;
  }
</style>