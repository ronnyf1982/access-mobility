<template>
  <div class="legal-page">
    <div class="legal-card">
      <RouterLink to="/" class="legal-back">
        <i class="pi pi-arrow-left" aria-hidden="true"></i>
        Zurück zur Startseite
      </RouterLink>
      <h1 class="legal-title">Datenschutzerklärung</h1>
      <div class="legal-notice" role="status">
        <i class="pi pi-clock" aria-hidden="true"></i>
        <div>
          <strong>Diese Seite wird derzeit vorbereitet.</strong>
          <p>Die vollständige Datenschutzerklärung wird vor dem öffentlichen Launch veröffentlicht.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Placeholder — vollständiger Inhalt folgt vor öffentlichem Launch
</script>

<style scoped>
.legal-page {
  min-height: 100dvh;
  background: var(--am-bg-base);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--am-space-l);
}

.legal-card {
  width: 100%;
  max-width: 540px;
  background: var(--am-bg-surface);
  border: 1px solid var(--am-border);
  border-radius: var(--am-radius-l);
  padding: 40px;
  display: flex;
  flex-direction: column;
  gap: var(--am-space-l);
}

.legal-back {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.875rem;
  color: var(--am-text-secondary);
  text-decoration: none;
  transition: color var(--am-transition);
}

.legal-back:hover {
  color: var(--am-text-primary);
}

.legal-title {
  font-size: 1.75rem;
  font-weight: 800;
  color: var(--am-text-primary);
  margin: 0;
}

.legal-notice {
  display: flex;
  align-items: flex-start;
  gap: var(--am-space-m);
  background: var(--am-bg-raised);
  border: 1px solid var(--am-border);
  border-radius: var(--am-radius-m);
  padding: var(--am-space-m);
}

.legal-notice > .pi {
  color: var(--am-accent);
  font-size: 1.2rem;
  margin-top: 2px;
  flex-shrink: 0;
}

.legal-notice strong {
  display: block;
  font-size: 0.9rem;
  color: var(--am-text-primary);
  margin-bottom: 6px;
}

.legal-notice p {
  margin: 0;
  font-size: 0.85rem;
  color: var(--am-text-secondary);
}
</style>
