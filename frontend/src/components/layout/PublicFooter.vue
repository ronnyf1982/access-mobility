<template>
  <footer class="pub-footer" id="kontakt">
    <div class="am-container">
      <div class="footer-grid">
        <!-- Brand -->
        <div class="footer-brand">
          <div class="footer-logo">
            <span class="footer-logo-mark">AM</span>
            <span class="footer-logo-text">Access <strong>Mobility</strong></span>
          </div>
          <p class="footer-tagline">
            Barrierefreie Mobilität.<br>Einfach buchbar.
          </p>
        </div>

        <!-- Links -->
        <div class="footer-col">
          <h4 class="footer-heading">Plattform</h4>
          <a href="#zielgruppen">Für Fahrgäste</a>
          <a href="#zielgruppen">Für Fahrdienste</a>
          <a href="#zielgruppen">Für Organisationen</a>
          <RouterLink to="/dashboard">Portal öffnen</RouterLink>
        </div>

        <div class="footer-col">
          <h4 class="footer-heading">Unternehmen</h4>
          <a href="#">Über uns</a>
          <a href="#">Kontakt</a>
          <a href="#">Karriere</a>
          <a href="#">Presse</a>
        </div>

        <div class="footer-col">
          <h4 class="footer-heading">Rechtliches</h4>
          <a href="#">Datenschutz</a>
          <a href="#">Impressum</a>
          <a href="#">AGB</a>
        </div>
      </div>

      <div class="footer-bottom">
        <span>© {{ currentYear }} Access Mobility GmbH. Alle Rechte vorbehalten.</span>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
const currentYear = new Date().getFullYear()
</script>

<style scoped>
.pub-footer {
  background: var(--am-bg-sidebar);
  border-top: 1px solid var(--am-border);
  padding: var(--am-space-xl) 0 var(--am-space-l);
  margin-top: var(--am-space-xl);
}

.footer-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: var(--am-space-xl);
  margin-bottom: var(--am-space-xl);
}

@media (max-width: 768px) {
  .footer-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 480px) {
  .footer-grid {
    grid-template-columns: 1fr;
  }
}

/* Brand */
.footer-logo {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  margin-bottom: var(--am-space-m);
}

.footer-logo-mark {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: var(--am-accent);
  color: var(--am-text-on-accent);
  font-weight: 800;
  font-size: 0.8rem;
  border-radius: var(--am-radius-s);
}

.footer-logo-text {
  font-size: 0.95rem;
  color: var(--am-text-primary);
}

.footer-logo-text strong {
  font-weight: 700;
}

.footer-tagline {
  font-size: 0.85rem;
  color: var(--am-text-muted);
  line-height: 1.7;
}

/* Link columns */
.footer-col {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-s);
}

.footer-heading {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--am-text-muted);
  margin-bottom: var(--am-space-xs);
}

.footer-col a {
  font-size: 0.875rem;
  color: var(--am-text-secondary);
  text-decoration: none;
  transition: color var(--am-transition);
}

.footer-col a:hover {
  color: var(--am-text-primary);
}

/* Bottom bar */
.footer-bottom {
  padding-top: var(--am-space-l);
  border-top: 1px solid var(--am-border);
  font-size: 0.8rem;
  color: var(--am-text-muted);
  text-align: center;
}
</style>
