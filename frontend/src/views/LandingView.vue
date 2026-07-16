<template>
  <!-- Hero -->
  <section class="hero" aria-labelledby="hero-headline">
    <div class="am-container hero-inner">
      <div class="hero-text">
        <p class="hero-eyebrow">Barrierefreie Mobilität</p>
        <h1 id="hero-headline">
          Mobil bleiben.<br>
          <span class="am-accent-text">Einfach buchbar.</span>
        </h1>
        <p class="hero-sub">
          Access Mobility verbindet Fahrgäste mit spezialisierten Fahrdiensten.
          Sicher, komfortabel und barrierefrei – wann und wo Sie uns brauchen.
        </p>
        <div class="hero-actions">
          <RouterLink to="/dashboard" class="am-btn am-btn-primary">
            <i class="pi pi-car" aria-hidden="true"></i>
            Fahrt buchen
          </RouterLink>
          <a href="#so-funktioniert" class="am-btn am-btn-secondary">
            So funktioniert's
          </a>
        </div>
      </div>

      <!-- Stat-Card statt Bild-Einbettung -->
      <div class="hero-visual" aria-hidden="true">
        <div class="hero-stat-card">
          <div class="hero-stat-header">
            <span class="hero-stat-label">Plattform-Übersicht</span>
            <span class="hero-stat-dot"></span>
          </div>
          <div class="hero-stats">
            <div class="hero-stat">
              <span class="hero-stat-value">1.200+</span>
              <span class="hero-stat-desc">Fahrten täglich</span>
            </div>
            <div class="hero-stat">
              <span class="hero-stat-value">98</span>
              <span class="hero-stat-desc">Partner-Fahrdienste</span>
            </div>
            <div class="hero-stat">
              <span class="hero-stat-value">96 %</span>
              <span class="hero-stat-desc">Pünktlichkeitsrate</span>
            </div>
          </div>
          <div class="hero-stat-footer">
            <i class="pi pi-check-circle"></i>
            <span>Rollstuhlgerecht · Rampe · Escort</span>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Feature Strip -->
  <section class="feature-strip" id="so-funktioniert" aria-label="Vorteile auf einen Blick">
    <div class="am-container feature-strip-inner">
      <div class="feature-strip-item">
        <div class="feature-icon" aria-hidden="true"><i class="pi pi-shield"></i></div>
        <div>
          <strong>Zuverlässig &amp; sicher</strong>
          <p>Qualifizierte Fahrer:innen, geprüfte Fahrzeuge.</p>
        </div>
      </div>
      <div class="feature-strip-item">
        <div class="feature-icon" aria-hidden="true"><i class="pi pi-sliders-v"></i></div>
        <div>
          <strong>Für Ihren Bedarf</strong>
          <p>Rollstuhlrampe, Begleitperson, Liegendtransport – alles wählbar.</p>
        </div>
      </div>
      <div class="feature-strip-item">
        <div class="feature-icon" aria-hidden="true"><i class="pi pi-calendar"></i></div>
        <div>
          <strong>Flexibel planierbar</strong>
          <p>Einzel- oder Serienfahrten, spontan oder langfristig buchbar.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- Zielgruppen -->
  <section class="am-section zielgruppen" id="zielgruppen" aria-labelledby="zielgruppen-headline">
    <div class="am-container">
      <div class="section-header">
        <h2 id="zielgruppen-headline">Für wen ist Access Mobility?</h2>
        <p>Eine Plattform – drei Perspektiven.</p>
      </div>

      <div class="zielgruppen-grid">
        <article class="am-card target-card">
          <div class="target-icon" aria-hidden="true">
            <i class="pi pi-user"></i>
          </div>
          <h3>Für Fahrgäste</h3>
          <p>
            Buchen Sie Fahrten zu Ärzten, Reha-Zentren oder zur Arbeit –
            mit dem richtigen Fahrzeug und geschultem Personal.
          </p>
          <RouterLink to="/dashboard" class="am-btn am-btn-secondary card-btn">
            Fahrt buchen
          </RouterLink>
        </article>

        <article class="am-card target-card">
          <div class="target-icon" aria-hidden="true">
            <i class="pi pi-truck"></i>
          </div>
          <h3>Für Fahrdienste</h3>
          <p>
            Verwalten Sie Ihre Flotte, Fahrer und Aufträge zentral.
            Profitieren Sie von einer zuverlässigen Buchungsplattform.
          </p>
          <RouterLink to="/dashboard" class="am-btn am-btn-secondary card-btn">
            Portal öffnen
          </RouterLink>
        </article>

        <article class="am-card target-card">
          <div class="target-icon" aria-hidden="true">
            <i class="pi pi-building"></i>
          </div>
          <h3>Für Organisationen</h3>
          <p>
            Buchen und verwalten Sie Fahrten für Mitarbeiter:innen,
            Schüler:innen oder Klient:innen – transparent und effizient.
          </p>
          <RouterLink to="/dashboard" class="am-btn am-btn-secondary card-btn">
            Mehr erfahren
          </RouterLink>
        </article>
      </div>
    </div>
  </section>

  <!-- Vorteile -->
  <section class="am-section vorteile" aria-labelledby="vorteile-headline">
    <div class="am-container">
      <div class="section-header">
        <h2 id="vorteile-headline">Ihre Vorteile mit Access Mobility</h2>
        <p>Was unsere Plattform von herkömmlichen Lösungen unterscheidet.</p>
      </div>

      <div class="vorteile-grid">
        <div class="vorteil-item">
          <div class="vorteil-icon" aria-hidden="true"><i class="pi pi-calendar-clock"></i></div>
          <h3>Flexible Buchung</h3>
          <p>Einmalige Fahrten oder Serienfahrten – buchen Sie so, wie es zu Ihrem Alltag passt.</p>
        </div>
        <div class="vorteil-item">
          <div class="vorteil-icon" aria-hidden="true"><i class="pi pi-car"></i></div>
          <h3>Spezialisierte Fahrzeuge</h3>
          <p>Rampen, Rollstuhlplätze, Liegen – wir stellen das passende Fahrzeug bereit.</p>
        </div>
        <div class="vorteil-item">
          <div class="vorteil-icon" aria-hidden="true"><i class="pi pi-verified"></i></div>
          <h3>Geschulte Fahrer:innen</h3>
          <p>Alle Fahrer sind qualifiziert, zertifiziert und im Umgang mit Assistenzbedarf erfahren.</p>
        </div>
        <div class="vorteil-item">
          <div class="vorteil-icon" aria-hidden="true"><i class="pi pi-chart-bar"></i></div>
          <h3>Zentrale Verwaltung</h3>
          <p>Organisationen behalten den Überblick über alle Buchungen, Kosten und Berichte.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- CTA-Banner -->
  <section class="cta-banner am-section" aria-label="Jetzt starten">
    <div class="am-container cta-banner-inner">
      <div>
        <h2>Bereit loszulegen?</h2>
        <p>Registrieren Sie sich kostenlos und buchen Sie Ihre erste Fahrt in wenigen Minuten.</p>
      </div>
      <RouterLink to="/dashboard" class="am-btn am-btn-primary cta-banner-btn">
        <i class="pi pi-arrow-right" aria-hidden="true"></i>
        Jetzt starten
      </RouterLink>
    </div>
  </section>
</template>

<script setup lang="ts">
// Keine Datenlader nötig – statische Landingpage
</script>

<style scoped>
/* ── Hero ────────────────────────────────────────────── */
.hero {
  padding: 140px 0 80px; /* Platz für fixed Header */
  background: linear-gradient(160deg, #161616 0%, var(--am-bg-base) 60%);
  border-bottom: 1px solid var(--am-border);
}

.hero-inner {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--am-space-xl);
  align-items: center;
}

@media (max-width: 900px) {
  .hero-inner {
    grid-template-columns: 1fr;
  }
  .hero-visual {
    display: none;
  }
  .hero {
    padding: 120px 0 60px;
  }
}

.hero-eyebrow {
  font-size: 0.8rem;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--am-accent);
  margin-bottom: var(--am-space-m);
}

.hero-text h1 {
  font-size: clamp(2rem, 4vw, 3rem);
  font-weight: 800;
  line-height: 1.15;
  margin-bottom: var(--am-space-m);
}

.hero-sub {
  font-size: 1rem;
  color: var(--am-text-secondary);
  max-width: 460px;
  margin-bottom: var(--am-space-l);
  line-height: 1.7;
}

.hero-actions {
  display: flex;
  gap: var(--am-space-m);
  flex-wrap: wrap;
}

/* Hero stat card */
.hero-stat-card {
  background: var(--am-bg-surface);
  border: 1px solid var(--am-border);
  border-radius: var(--am-radius-l);
  padding: var(--am-space-l);
}

.hero-stat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--am-space-l);
}

.hero-stat-label {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--am-text-muted);
}

.hero-stat-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--am-success);
  box-shadow: 0 0 0 3px var(--am-success-bg);
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--am-space-m);
  margin-bottom: var(--am-space-l);
}

.hero-stat {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.hero-stat-value {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--am-accent);
  line-height: 1;
}

.hero-stat-desc {
  font-size: 0.75rem;
  color: var(--am-text-muted);
  line-height: 1.4;
}

.hero-stat-footer {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  padding-top: var(--am-space-m);
  border-top: 1px solid var(--am-border);
  font-size: 0.8rem;
  color: var(--am-success);
}

/* ── Feature Strip ───────────────────────────────────── */
.feature-strip {
  background: var(--am-bg-surface);
  border-bottom: 1px solid var(--am-border);
  padding: var(--am-space-l) 0;
}

.feature-strip-inner {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--am-space-l);
}

@media (max-width: 768px) {
  .feature-strip-inner {
    grid-template-columns: 1fr;
    gap: var(--am-space-m);
  }
}

.feature-strip-item {
  display: flex;
  align-items: flex-start;
  gap: var(--am-space-m);
}

.feature-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--am-radius-s);
  background: var(--am-accent);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.feature-icon .pi {
  color: var(--am-text-on-accent);
  font-size: 1rem;
}

.feature-strip-item strong {
  display: block;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--am-text-primary);
  margin-bottom: 2px;
}

.feature-strip-item p {
  font-size: 0.8rem;
  color: var(--am-text-secondary);
  margin: 0;
}

/* ── Section Header ──────────────────────────────────── */
.section-header {
  text-align: center;
  margin-bottom: var(--am-space-xl);
}

.section-header h2 {
  font-size: clamp(1.4rem, 2.5vw, 1.85rem);
  font-weight: 700;
  margin-bottom: var(--am-space-s);
}

.section-header p {
  color: var(--am-text-secondary);
  font-size: 1rem;
}

/* ── Zielgruppen ─────────────────────────────────────── */
.zielgruppen-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--am-space-l);
}

@media (max-width: 768px) {
  .zielgruppen-grid {
    grid-template-columns: 1fr;
  }
}

.target-card {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-m);
  transition: border-color var(--am-transition), background var(--am-transition);
}

.target-card:hover {
  border-color: var(--am-border-strong);
  background: var(--am-bg-raised);
}

.target-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--am-radius-s);
  background: var(--am-accent);
  display: flex;
  align-items: center;
  justify-content: center;
}

.target-icon .pi {
  color: var(--am-text-on-accent);
  font-size: 1.1rem;
}

.target-card h3 {
  font-size: 1rem;
  font-weight: 600;
}

.target-card p {
  font-size: 0.875rem;
  color: var(--am-text-secondary);
  line-height: 1.6;
  flex: 1;
}

.card-btn {
  align-self: flex-start;
  font-size: 0.85rem;
  padding: 0.4rem 1rem;
  min-height: 38px;
}

/* ── Vorteile ────────────────────────────────────────── */
.vorteile {
  background: var(--am-bg-surface);
  border-top: 1px solid var(--am-border);
  border-bottom: 1px solid var(--am-border);
}

.vorteile-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--am-space-l);
}

@media (max-width: 900px) {
  .vorteile-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .vorteile-grid {
    grid-template-columns: 1fr;
  }
}

.vorteil-item {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-s);
}

.vorteil-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--am-radius-s);
  background: var(--am-accent-bg);
  border: 1px solid rgba(255, 214, 0, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--am-space-xs);
}

.vorteil-icon .pi {
  color: var(--am-accent);
  font-size: 1rem;
}

.vorteil-item h3 {
  font-size: 0.95rem;
  font-weight: 600;
}

.vorteil-item p {
  font-size: 0.85rem;
  color: var(--am-text-secondary);
  line-height: 1.6;
}

/* ── CTA Banner ──────────────────────────────────────── */
.cta-banner {
  border-top: 1px solid var(--am-border);
}

.cta-banner-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--am-space-l);
  flex-wrap: wrap;
}

.cta-banner h2 {
  font-size: 1.4rem;
  font-weight: 700;
  margin-bottom: var(--am-space-xs);
}

.cta-banner p {
  color: var(--am-text-secondary);
  font-size: 0.9rem;
}

.cta-banner-btn {
  flex-shrink: 0;
  font-size: 0.95rem;
  padding: 0.65rem 1.5rem;
}
</style>
