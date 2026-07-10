<template>
  <header class="pub-header" :class="{ scrolled: isScrolled }">
    <div class="am-container pub-header-inner">
      <!-- Logo -->
      <RouterLink to="/" class="pub-logo" aria-label="Access Mobility – Startseite">
        <span class="pub-logo-mark">AM</span>
        <span class="pub-logo-text">Access <strong>Mobility</strong></span>
      </RouterLink>

      <!-- Navigation Desktop -->
      <nav class="pub-nav am-hide-mobile" aria-label="Hauptnavigation">
        <a href="#zielgruppen" class="pub-nav-link">Für Fahrgäste</a>
        <a href="#zielgruppen" class="pub-nav-link">Für Fahrdienste</a>
        <a href="#zielgruppen" class="pub-nav-link">Organisationen</a>
        <a href="#kontakt" class="pub-nav-link">Kontakt</a>
      </nav>

      <!-- CTA -->
      <RouterLink to="/dashboard" class="am-btn am-btn-primary pub-cta">
        <i class="pi pi-user" aria-hidden="true"></i>
        Anmelden&nbsp;/&nbsp;Registrieren
      </RouterLink>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const isScrolled = ref(false)

function onScroll() {
  isScrolled.value = window.scrollY > 40
}

onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', onScroll))
</script>

<style scoped>
.pub-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: transparent;
  border-bottom: 1px solid transparent;
  transition:
    background var(--am-transition),
    border-color var(--am-transition);
}

.pub-header.scrolled {
  background: rgba(17, 17, 17, 0.95);
  backdrop-filter: blur(10px);
  border-bottom-color: var(--am-border);
}

.pub-header-inner {
  display: flex;
  align-items: center;
  gap: var(--am-space-l);
  height: 68px;
}

/* Logo */
.pub-logo {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  text-decoration: none;
  flex-shrink: 0;
}

.pub-logo-mark {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: var(--am-accent);
  color: var(--am-text-on-accent);
  font-weight: 800;
  font-size: 0.85rem;
  border-radius: var(--am-radius-s);
  letter-spacing: 0.5px;
}

.pub-logo-text {
  font-size: 1rem;
  color: var(--am-text-primary);
  font-weight: 400;
}

.pub-logo-text strong {
  font-weight: 700;
}

/* Nav */
.pub-nav {
  display: flex;
  align-items: center;
  gap: var(--am-space-l);
  flex: 1;
  justify-content: center;
}

.pub-nav-link {
  color: var(--am-text-secondary);
  font-size: 0.9rem;
  text-decoration: none;
  transition: color var(--am-transition);
}

.pub-nav-link:hover {
  color: var(--am-text-primary);
}

/* CTA */
.pub-cta {
  flex-shrink: 0;
  font-size: 0.85rem;
  padding: 0.45rem 1rem;
  min-height: 40px;
}
</style>
