<template>
  <aside class="sidebar" aria-label="Portalnavigation">
    <!-- Logo -->
    <div class="sidebar-logo">
      <RouterLink to="/" class="sidebar-logo-link" aria-label="Zur Startseite">
        <span class="sidebar-logo-mark">AM</span>
        <span class="sidebar-logo-text">Access<br><strong>Mobility</strong></span>
      </RouterLink>
    </div>

    <!-- Navigation -->
    <nav class="sidebar-nav">
      <template v-for="item in navItems" :key="item.label">
        <RouterLink
          v-if="item.to"
          :to="item.to"
          class="sidebar-nav-item"
          :class="{ active: isActive(item.to) }"
          :aria-current="isActive(item.to) ? 'page' : undefined"
        >
          <i :class="['pi', item.icon]" aria-hidden="true"></i>
          <span>{{ item.label }}</span>
        </RouterLink>
        <button
          v-else
          class="sidebar-nav-item sidebar-nav-item--soon"
          disabled
          :title="`${item.label} – folgt in einem späteren Sprint`"
        >
          <i :class="['pi', item.icon]" aria-hidden="true"></i>
          <span>{{ item.label }}</span>
          <span class="soon-chip" aria-label="In Entwicklung">bald</span>
        </button>
      </template>
    </nav>

    <!-- Plattform-Admin-Bereich -->
    <nav v-if="isPlatformAdmin" class="sidebar-nav sidebar-admin-section" aria-label="Plattform-Admin">
      <div class="sidebar-section-label">Plattform-Admin</div>
      <RouterLink
        to="/platform-admin/users"
        class="sidebar-nav-item"
        :class="{ active: isActive('/platform-admin/users') }"
        :aria-current="isActive('/platform-admin/users') ? 'page' : undefined"
      >
        <i class="pi pi-users" aria-hidden="true"></i>
        <span>Benutzerverwaltung</span>
      </RouterLink>
    </nav>

    <!-- Support + Abmelden -->
    <div class="sidebar-support">
      <div class="support-label">Support</div>
      <a href="mailto:support@access-mobility.de" class="sidebar-nav-item support-link">
        <i class="pi pi-question-circle" aria-hidden="true"></i>
        <span>Hilfe &amp; Support</span>
      </a>
      <button class="sidebar-nav-item sidebar-logout" @click="handleLogout">
        <i class="pi pi-sign-out" aria-hidden="true"></i>
        <span>Abmelden</span>
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

interface NavItem {
  label: string
  icon: string
  to?: string
}

const PASSENGER_ROLES = new Set(['passenger', 'trusted_person', 'organization_coordinator'])
const DISPO_ROLES = new Set(['provider_admin', 'dispatcher', 'organization_admin'])

const navItems = computed<NavItem[]>(() => {
  const role = authStore.role ?? ''

  if (PASSENGER_ROLES.has(role)) {
    return [
      { label: 'Dashboard',        icon: 'pi-th-large', to: '/dashboard' },
      { label: 'Fahrten anfragen', icon: 'pi-car',      to: '/transport-requests' },
      { label: 'Mobilitätsprofil', icon: 'pi-heart',    to: '/mobility-profile' },
    ]
  }

  if (role === 'driver') {
    return [
      { label: 'Meine Schicht',  icon: 'pi-car',     to: '/driver' },
      { label: 'Meine Aufträge', icon: 'pi-list',    to: '/driver' },
      { label: 'Dashboard',      icon: 'pi-th-large', to: '/dashboard' },
    ]
  }

  if (DISPO_ROLES.has(role)) {
    return [
      { label: 'Dashboard',     icon: 'pi-th-large',  to: '/dashboard' },
      { label: 'Disposition',   icon: 'pi-car',       to: '/transport-requests' },
      { label: 'Fahrzeuge',     icon: 'pi-truck',     to: '/vehicles' },
      { label: 'Fahrer',        icon: 'pi-id-card',   to: '/drivers' },
      { label: 'Fahrgäste',     icon: 'pi-users' },
      { label: 'Organisationen', icon: 'pi-building' },
      { label: 'Abrechnung',    icon: 'pi-file' },
    ]
  }

  return [
    { label: 'Dashboard', icon: 'pi-th-large', to: '/dashboard' },
  ]
})

const isPlatformAdmin = computed(() => authStore.role === 'platform_admin')

function isActive(to: string): boolean {
  return route.path === to || route.path.startsWith(to + '/')
}

async function handleLogout() {
  await authStore.logout()
  await router.push('/')
}
</script>

<style scoped>
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  width: var(--am-sidebar-width);
  height: 100vh;
  background: var(--am-bg-sidebar);
  border-right: 1px solid var(--am-border);
  display: flex;
  flex-direction: column;
  z-index: 50;
  overflow-y: auto;
  overflow-x: hidden;
}

/* Logo */
.sidebar-logo {
  padding: var(--am-space-l) var(--am-space-m);
  border-bottom: 1px solid var(--am-border);
  flex-shrink: 0;
}

.sidebar-logo-link {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  text-decoration: none;
}

.sidebar-logo-mark {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  background: var(--am-accent);
  color: var(--am-text-on-accent);
  font-weight: 800;
  font-size: 0.8rem;
  border-radius: var(--am-radius-s);
  flex-shrink: 0;
}

.sidebar-logo-text {
  font-size: 0.8rem;
  line-height: 1.3;
  color: var(--am-text-primary);
  font-weight: 400;
}

.sidebar-logo-text strong {
  font-weight: 700;
}

/* Nav */
.sidebar-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: var(--am-space-m) var(--am-space-s);
  gap: 2px;
}

.sidebar-nav-item {
  display: flex;
  align-items: center;
  gap: var(--am-space-m);
  padding: 10px var(--am-space-m);
  border-radius: var(--am-radius-s);
  font-size: 0.875rem;
  color: var(--am-text-secondary);
  text-decoration: none;
  background: none;
  border: none;
  width: 100%;
  text-align: left;
  cursor: pointer;
  transition:
    background var(--am-transition),
    color var(--am-transition);
  position: relative;
  min-height: 44px;
}

.sidebar-nav-item:hover:not([disabled]) {
  background: var(--am-bg-raised);
  color: var(--am-text-primary);
}

.sidebar-nav-item.active {
  background: var(--am-accent);
  color: var(--am-text-on-accent);
  font-weight: 600;
}

.sidebar-nav-item.active .pi {
  color: var(--am-text-on-accent);
}

.sidebar-nav-item .pi {
  font-size: 1rem;
  width: 20px;
  flex-shrink: 0;
}

/* Disabled (coming soon) */
.sidebar-nav-item--soon {
  opacity: 0.45;
  cursor: default;
}

.soon-chip {
  margin-left: auto;
  font-size: 0.65rem;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 99px;
  background: var(--am-bg-raised);
  color: var(--am-text-secondary);
  border: 1px solid var(--am-border);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

/* Support */
.sidebar-support {
  padding: var(--am-space-m) var(--am-space-s);
  border-top: 1px solid var(--am-border);
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.sidebar-admin-section {
  border-top: 1px solid var(--am-border);
  padding-top: var(--am-space-m);
}

.sidebar-section-label {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--am-accent);
  padding: 0 var(--am-space-m);
  margin-bottom: var(--am-space-xs);
}

.support-label {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--am-text-secondary);
  padding: 0 var(--am-space-m);
  margin-bottom: var(--am-space-xs);
}

.support-link {
  color: var(--am-text-secondary);
}

.sidebar-logout {
  color: var(--am-text-secondary);
}

.sidebar-logout:hover {
  color: var(--am-danger);
  background: var(--am-danger-bg);
}
</style>
