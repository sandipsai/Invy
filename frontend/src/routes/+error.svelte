<script>
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
</script>

<div class="error-page">
  <div class="error-card">

    <div class="error-code">{$page.status}</div>

    <h1 class="error-title">
      {#if $page.status === 404}
        Page not found
      {:else if $page.status === 409}
        Action not allowed
      {:else if $page.status === 422}
        Invalid request
      {:else}
        Something went wrong
      {/if}
    </h1>

    <p class="error-message">
      {$page.error?.message ?? 'An unexpected error occurred.'}
    </p>

    <div class="error-actions">
      <button class="btn-primary" on:click={() => history.back()}>
        ← Go back
      </button>
      <button class="btn-outline" on:click={() => goto('/dashboard')}>
        Dashboard
      </button>
    </div>

    {#if $page.status >= 500}
      <p class="error-hint">
        Make sure the Python backend is running at
        <code>{import.meta.env.PUBLIC_API_BASE ?? 'http://localhost:8000'}</code>
      </p>
    {/if}

  </div>
</div>

<style>
  .error-page {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-app);
    padding: 24px;
  }

  .error-card {
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-md);
    padding: 48px 40px;
    max-width: 440px;
    width: 100%;
    text-align: center;
  }

  .error-code {
    font-size: 64px;
    font-weight: 700;
    color: var(--accent);
    font-variant-numeric: tabular-nums;
    line-height: 1;
    margin-bottom: 16px;
    letter-spacing: -0.04em;
    font-family: 'DM Mono', monospace;
  }

  .error-title {
    font-size: 20px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 10px;
  }

  .error-message {
    font-size: 14px;
    color: var(--text-secondary);
    line-height: 1.6;
    margin-bottom: 28px;
  }

  .error-actions {
    display: flex;
    gap: 10px;
    justify-content: center;
    flex-wrap: wrap;
  }

  .btn-primary {
    padding: 8px 18px;
    border-radius: var(--radius-sm);
    background: var(--accent);
    color: var(--text-on-accent);
    font-size: 13.5px;
    font-weight: 500;
    font-family: inherit;
    cursor: pointer;
    border: none;
    transition: opacity 0.12s;
  }
  .btn-primary:hover { opacity: 0.88; }

  .btn-outline {
    padding: 8px 18px;
    border-radius: var(--radius-sm);
    background: var(--bg-surface);
    color: var(--text-secondary);
    border: 1px solid var(--border);
    font-size: 13.5px;
    font-weight: 500;
    font-family: inherit;
    cursor: pointer;
    transition: background 0.12s;
  }
  .btn-outline:hover { background: var(--bg-surface-alt); }

  .error-hint {
    margin-top: 24px;
    font-size: 12px;
    color: var(--text-muted);
    line-height: 1.6;
  }

  .error-hint code {
    font-family: 'DM Mono', monospace;
    font-size: 11.5px;
    background: var(--bg-surface-alt);
    padding: 1px 6px;
    border-radius: 4px;
    border: 1px solid var(--border);
  }
</style>