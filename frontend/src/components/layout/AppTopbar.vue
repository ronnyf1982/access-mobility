<template>
  <header class="topbar" role="banner">
    <!-- Suche -->
    <div class="topbar-search">
      <i class="pi pi-search topbar-search-icon" aria-hidden="true"></i>
      <input
        v-model="searchQuery"
        type="search"
        class="topbar-search-input"
        placeholder="Suche nach Fahrten, Fahrgästen, Fahrzeugen …"
        aria-label="Globale Suche"
      />
    </div>

    <!-- Rechte Seite -->
    <div class="topbar-right">
      <!-- Benachrichtigungen -->
      <button class="topbar-icon-btn" aria-label="Benachrichtigungen" @click="showNotifications">
        <i class="pi pi-bell" aria-hidden="true"></i>
        <span class="topbar-badge" aria-label="3 neue Benachrichtigungen">3</span>
      </button>

      <!-- Divider -->
      <div class="topbar-divider" aria-hidden="true"></div>

      <!-- User -->
      <div class="topbar-user" role="button" tabindex="0" aria-label="Benutzerprofil öffnen">
        <div class="topbar-avatar" aria-hidden="true">MM</div>
        <div class="topbar-user-info am-hide-mobile">
          <span class="topbar-user-name">Max Mustermann</span>
          <span class="topbar-user-role">Administrator</span>
        </div>
        <i class="pi pi-chevron-down topbar-chevron am-hide-mobile" aria-hidden="true"></i>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useToast } from 'primevue/usetoast'

const searchQuery = ref('')
const toast = useToast()

function showNotifications() {
  toast.add({
    severity: 'info',
    summary: 'Benachrichtigungen',
    detail: 'Benachrichtigungsmodul folgt in einem späteren Sprint.',
    life: 3000,
  })
}
</script>

<style scoped>
.topbar {
  position: sticky;
  top: 0;
  z-index: 40;
  display: flex;
  align-items: center;
  gap: var(--am-space-m);
  height: var(--am-topbar-height);
  padding: 0 var(--am-space-l);
  background: var(--am-bg-base);
  border-bottom: 1px solid var(--am-border);
  flex-shrink: 0;
}

/* Search */
.topbar-search {
  flex: 1;
  position: relative;
  max-width: 460px;
}

.topbar-search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--am-text-muted);
  font-size: 0.875rem;
  pointer-events: none;
}

.topbar-search-input {
  width: 100%;
  background: var(--am-bg-surface);
  border: 1px solid var(--am-border);
  border-radius: var(--am-radius-s);
  color: var(--am-text-primary);
  font-size: 0.875rem;
  padding: 0.45rem 0.75rem 0.45rem 2.25rem;
  outline: none;
  transition: border-color var(--am-transition);
  height: 38px;
}

.topbar-search-input::placeholder {
  color: var(--am-text-muted);
}

.topbar-search-input:focus {
  border-color: var(--am-accent);
}

/* Right side */
.topbar-right {
  display: flex;
  align-items: center;
  gap: var(--am-space-m);
  margin-left: auto;
}

.topbar-icon-btn {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  border-radius: var(--am-radius-s);
  background: var(--am-bg-surface);
  border: 1px solid var(--am-border);
  color: var(--am-text-secondary);
  cursor: pointer;
  transition: color var(--am-transition), background var(--am-transition);
}

.topbar-icon-btn:hover {
  color: var(--am-text-primary);
  background: var(--am-bg-raised);
}

.topbar-badge {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--am-accent);
  color: var(--am-text-on-accent);
  font-size: 0.65rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.topbar-divider {
  width: 1px;
  height: 28px;
  background: var(--am-border);
}

/* User */
.topbar-user {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  cursor: pointer;
  padding: 4px 8px;
  border-radius: var(--am-radius-s);
  transition: background var(--am-transition);
}

.topbar-user:hover {
  background: var(--am-bg-raised);
}

.topbar-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: var(--am-accent);
  color: var(--am-text-on-accent);
  font-weight: 700;
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.topbar-user-info {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.topbar-user-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--am-text-primary);
  line-height: 1.2;
}

.topbar-user-role {
  font-size: 0.7rem;
  color: var(--am-text-muted);
  line-height: 1.2;
}

.topbar-chevron {
  color: var(--am-text-muted);
  font-size: 0.7rem;
}
</style>
