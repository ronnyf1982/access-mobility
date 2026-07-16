<template>
  <div class="gp">

    <!-- ══════════════════════════════════════════
         LINKE SPALTE — Branding & Info
    ══════════════════════════════════════════ -->
    <section class="gp-left" aria-label="Fahrando Projektvorschau">

      <!-- Logo -->
      <div class="gp-logo">
        <FahrandoLogo variant="default" />
      </div>

      <!-- Haupt-Headline -->
      <div class="gp-headline-wrap">
        <h1 class="gp-h1">
          Hier entsteht<br>
          <em class="gp-h1-yellow">etwas Großes.</em>
        </h1>
      </div>

      <!-- Beschreibung -->
      <p class="gp-desc">
        Fahrando entwickelt eine Plattform für barrierefreie
        Mobilität – für selbstbestimmte Wege und eine
        offenere Welt für alle.
      </p>

      <!-- 3 Nutzen-Punkte NEBENEINANDER -->
      <div class="gp-benefits">
        <div class="gp-benefit">
          <span class="gp-benefit-icon" aria-hidden="true">
            <i class="pi pi-heart-fill"></i>
          </span>
          <span class="gp-benefit-body">
            <strong class="gp-benefit-title">Barrierefreie Mobilität</strong>
            <span class="gp-benefit-sub">Für alle Lebenssituationen</span>
          </span>
        </div>
        <div class="gp-benefit">
          <span class="gp-benefit-icon" aria-hidden="true">
            <i class="pi pi-map-marker"></i>
          </span>
          <span class="gp-benefit-body">
            <strong class="gp-benefit-title">Bessere Informationen</strong>
            <span class="gp-benefit-sub">Für bessere Wege</span>
          </span>
        </div>
        <div class="gp-benefit">
          <span class="gp-benefit-icon" aria-hidden="true">
            <i class="pi pi-users"></i>
          </span>
          <span class="gp-benefit-body">
            <strong class="gp-benefit-title">Gemeinsam für</strong>
            <span class="gp-benefit-sub">eine offene Welt</span>
          </span>
        </div>
      </div>

      <!-- Hinweis-Box -->
      <div class="gp-notice" role="note">
        <i class="pi pi-clock gp-notice-icon" aria-hidden="true"></i>
        <div>
          <p class="gp-notice-title">Der öffentliche Auftritt folgt bald.</p>
          <p class="gp-notice-text">Vielen Dank für Ihr Interesse und Ihre Unterstützung.</p>
        </div>
      </div>

    </section>

    <!-- ══════════════════════════════════════════
         RECHTE SPALTE — Login-Card
    ══════════════════════════════════════════ -->
    <section class="gp-right" aria-label="Anmeldung Testzugang">
      <div class="gp-card">

        <!-- Schild-Symbol -->
        <div class="gp-shield" aria-hidden="true">
          <i class="pi pi-shield"></i>
        </div>

        <h2 class="gp-card-title" id="gp-card-title">Geschützter Testzugang</h2>
        <p class="gp-card-sub">Nur für Tester</p>

        <!-- Fehlermeldung -->
        <div
          v-if="errorMsg"
          class="gp-error"
          role="alert"
          aria-live="assertive"
          aria-atomic="true"
        >
          <i class="pi pi-exclamation-circle" aria-hidden="true"></i>
          <span>{{ errorMsg }}</span>
        </div>

        <!-- Formular -->
        <form class="gp-form" @submit.prevent="handleSubmit" novalidate aria-labelledby="gp-card-title">

          <div class="gp-field">
            <label for="gp-email" class="gp-label">Benutzername oder E-Mail</label>
            <div class="gp-input-wrap">
              <i class="pi pi-user gp-iicon" aria-hidden="true"></i>
              <input
                id="gp-email"
                ref="emailRef"
                v-model="emailOrUsername"
                type="text"
                class="gp-input gp-input--il"
                :class="{ 'gp-input--err': errorMsg }"
                autocomplete="username"
                aria-required="true"
                :aria-invalid="!!errorMsg"
                placeholder="Benutzername oder E-Mail"
              />
            </div>
          </div>

          <div class="gp-field">
            <label for="gp-pw" class="gp-label">Passwort</label>
            <div class="gp-input-wrap">
              <i class="pi pi-lock gp-iicon" aria-hidden="true"></i>
              <input
                id="gp-pw"
                v-model="password"
                :type="showPw ? 'text' : 'password'"
                class="gp-input gp-input--il gp-input--ir"
                :class="{ 'gp-input--err': errorMsg }"
                autocomplete="current-password"
                aria-required="true"
                :aria-invalid="!!errorMsg"
                placeholder="Passwort"
              />
              <button
                type="button"
                class="gp-eye"
                :aria-label="showPw ? 'Passwort verbergen' : 'Passwort anzeigen'"
                @click="showPw = !showPw"
              >
                <i :class="['pi', showPw ? 'pi-eye-slash' : 'pi-eye']" aria-hidden="true"></i>
              </button>
            </div>
          </div>

          <button
            type="submit"
            class="gp-btn"
            :disabled="loading || !emailOrUsername || !password"
            :aria-busy="loading"
          >
            <i v-if="loading" class="pi pi-spin pi-spinner" aria-hidden="true"></i>
            <span>{{ loading ? 'Prüfen …' : 'Einloggen' }}</span>
            <i v-if="!loading" class="pi pi-arrow-right" aria-hidden="true"></i>
          </button>

        </form>

        <p class="gp-secure">
          <i class="pi pi-lock" aria-hidden="true"></i>
          Dieser Bereich ist passwortgeschützt.
        </p>

      </div>
    </section>

    <!-- ══════════════════════════════════════════
         FOOTER
    ══════════════════════════════════════════ -->
    <footer class="gp-footer" role="contentinfo">
      <span class="gp-copy">&copy; {{ year }} <em class="gp-copy-brand">Fahrando</em>. Alle Rechte vorbehalten.</span>
      <nav class="gp-legal" aria-label="Rechtliches">
        <RouterLink to="/impressum" class="gp-legal-link">Impressum</RouterLink>
        <span class="gp-legal-sep" aria-hidden="true">|</span>
        <RouterLink to="/datenschutz" class="gp-legal-link">Datenschutz</RouterLink>
      </nav>
    </footer>

    <!-- Logo — absolut zentriert zwischen linker und rechter Spalte -->
    <div class="gp-center" aria-hidden="true">
      <img src="/Logo1.png" alt="" class="gp-center-img" />
    </div>

    <!-- Dekorative Hintergrund-Ellipsen rechts unten -->
    <div class="gp-deco" aria-hidden="true">
      <svg viewBox="0 0 560 420" fill="none" xmlns="http://www.w3.org/2000/svg" width="560" height="420">
        <ellipse cx="430" cy="340" rx="290" ry="200" fill="#FFD600" fill-opacity="0.04"/>
        <ellipse cx="480" cy="390" rx="210" ry="150" fill="#FFD600" fill-opacity="0.03"/>
        <ellipse cx="380" cy="360" rx="370" ry="250" fill="#FFD600" fill-opacity="0.015"/>
      </svg>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import FahrandoLogo from '@/components/branding/FahrandoLogo.vue'

const router = useRouter()
const route = useRoute()
const year = new Date().getFullYear()

const emailOrUsername = ref('')
const password = ref('')
const showPw = ref(false)
const loading = ref(false)
const errorMsg = ref('')
const emailRef = ref<HTMLInputElement | null>(null)

onMounted(() => emailRef.value?.focus())

async function handleSubmit() {
  if (!emailOrUsername.value || !password.value || loading.value) return
  errorMsg.value = ''
  loading.value = true
  try {
    const res = await fetch('/api/v1/public/test-access/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email_or_username: emailOrUsername.value, password: password.value }),
    })
    if (res.ok) {
      sessionStorage.setItem('fahrando_preview_unlocked', '1')
      const raw = route.query.redirect as string | undefined
      const target = raw && raw.startsWith('/') && !raw.startsWith('//') ? raw : '/'
      await router.push(target)
    } else if (res.status === 401) {
      errorMsg.value = 'Zugangsdaten nicht korrekt.'
      password.value = ''
    } else {
      errorMsg.value = 'Ein Fehler ist aufgetreten. Bitte erneut versuchen.'
    }
  } catch {
    errorMsg.value = 'Server nicht erreichbar. Bitte später erneut versuchen.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* ─────────────────────────────────────────────────────────────
   ROOT — Seiten-Grid
───────────────────────────────────────────────────────────── */
.gp {
  min-height: 100dvh;
  background: #0f0f10;
  display: grid;
  grid-template-columns: 1fr 480px;
  grid-template-rows: 1fr auto;
  grid-template-areas:
    "left  right"
    "footer footer";
  position: relative;
  overflow: hidden;
}

/* ─────────────────────────────────────────────────────────────
   LINKE SPALTE
───────────────────────────────────────────────────────────── */
.gp-left {
  grid-area: left;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 64px 48px 64px 72px;
  gap: 28px;
  z-index: 1;
}

/* Logo */
.gp-logo {
  margin-bottom: 4px;
}

/* Headline */
.gp-headline-wrap {
  /* kein extra-Wrapper nötig, aber nützlich falls Anpassungen nötig */
}

.gp-h1 {
  font-size: clamp(3rem, 4.2vw, 3.75rem); /* ~48–60 px */
  font-weight: 900;
  font-style: normal;
  line-height: 1.07;
  letter-spacing: -0.03em;
  color: #ffffff;
  margin: 0;
}

.gp-h1-yellow {
  /* "etwas Großes." — gelb, kursiv wie in der Vorlage */
  color: #FFD600;
  font-style: italic;
}

/* Beschreibungstext */
.gp-desc {
  font-size: 0.9375rem;   /* 15 px */
  line-height: 1.68;
  color: rgba(255, 255, 255, 0.48);
  margin: 0;
  max-width: 440px;
}

/* ── Benefits ──────────────────────────────────────────── */
.gp-benefits {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 18px;
}

.gp-benefit {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.gp-benefit-icon {
  flex-shrink: 0;
  width: 34px;
  height: 34px;
  border-radius: 7px;
  background: rgba(255, 214, 0, 0.1);
  border: 1px solid rgba(255, 214, 0, 0.14);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFD600;
  font-size: 0.8125rem;
}

.gp-benefit-body {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.gp-benefit-title {
  font-size: 0.8rem;
  font-weight: 700;
  color: #ffffff;
  line-height: 1.3;
}

.gp-benefit-sub {
  font-size: 0.72rem;
  color: rgba(255, 255, 255, 0.42);
  line-height: 1.4;
}

/* ── Hinweis-Box ───────────────────────────────────────── */
.gp-notice {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 14px 18px;
  background: rgba(255, 255, 255, 0.045);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  max-width: 500px;
}

.gp-notice-icon {
  flex-shrink: 0;
  color: #FFD600;
  font-size: 0.85rem;
  margin-top: 1px;
}

.gp-notice-title {
  font-size: 0.85rem;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 3px;
  line-height: 1.3;
}

.gp-notice-text {
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.45);
  margin: 0;
  line-height: 1.5;
}

/* ─────────────────────────────────────────────────────────────
   RECHTE SPALTE
───────────────────────────────────────────────────────────── */
.gp-right {
  grid-area: right;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 64px 52px;
  background: rgba(255, 255, 255, 0.018);
  border-left: 1px solid rgba(255, 255, 255, 0.07);
}

/* ── Card ──────────────────────────────────────────────── */
.gp-card {
  width: 100%;
  max-width: 358px;
  background: #1b1b1d;
  border: 1px solid rgba(255, 255, 255, 0.09);
  border-radius: 14px;
  padding: 36px 30px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 18px;
}

/* Schild-Icon */
.gp-shield {
  width: 52px;
  height: 52px;
  border-radius: 11px;
  background: rgba(255, 214, 0, 0.1);
  border: 1px solid rgba(255, 214, 0, 0.18);
  display: flex;
  align-items: center;
  justify-content: center;
}

.gp-shield .pi-shield {
  font-size: 1.55rem;
  color: #FFD600;
}

.gp-card-title {
  font-size: 1rem;
  font-weight: 700;
  color: #ffffff;
  text-align: center;
  margin: 0;
}

.gp-card-sub {
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.38);
  text-align: center;
  margin: -6px 0 2px;
}

/* Fehlermeldung */
.gp-error {
  display: flex;
  align-items: center;
  gap: 7px;
  width: 100%;
  padding: 9px 13px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.35);
  border-radius: 7px;
  color: #f87171;
  font-size: 0.82rem;
}

/* ── Formular ──────────────────────────────────────────── */
.gp-form {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 13px;
}

.gp-field {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.gp-label {
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 500;
  line-height: 1;
}

.gp-input-wrap {
  position: relative;
}

.gp-iicon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(255, 255, 255, 0.32);
  font-size: 0.84rem;
  pointer-events: none;
}

.gp-input {
  width: 100%;
  height: 44px;
  background: rgba(255, 255, 255, 0.058);
  border: 1px solid rgba(255, 255, 255, 0.11);
  border-radius: 7px;
  color: #ffffff;
  font-size: 0.88rem;
  padding: 0 13px;
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.gp-input::placeholder {
  color: rgba(255, 255, 255, 0.22);
}

.gp-input--il { padding-left: 36px; }   /* icon links */
.gp-input--ir { padding-right: 42px; }  /* icon rechts (Passwort-Toggle) */

.gp-input:focus {
  border-color: rgba(255, 214, 0, 0.45);
  box-shadow: 0 0 0 3px rgba(255, 214, 0, 0.1);
}

.gp-input--err {
  border-color: rgba(239, 68, 68, 0.45) !important;
}

.gp-eye {
  position: absolute;
  right: 0;
  top: 0;
  width: 42px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.3);
  cursor: pointer;
  transition: color 0.15s;
}
.gp-eye:hover { color: rgba(255, 255, 255, 0.65); }

/* Anmelde-Button */
.gp-btn {
  width: 100%;
  height: 48px;
  background: #FFD600;
  color: #0f0f10;
  border: none;
  border-radius: 7px;
  font-size: 0.9375rem;
  font-weight: 800;
  letter-spacing: 0.01em;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 9px;
  margin-top: 2px;
  transition: opacity 0.15s, transform 0.12s;
}
.gp-btn:hover:not(:disabled) { opacity: 0.9; transform: translateY(-1px); }
.gp-btn:disabled { opacity: 0.38; cursor: not-allowed; transform: none; }

/* Sicherheitshinweis */
.gp-secure {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.73rem;
  color: rgba(255, 255, 255, 0.28);
  margin: 0;
  text-align: center;
}
.gp-secure .pi { font-size: 0.68rem; }

/* ─────────────────────────────────────────────────────────────
   FOOTER
───────────────────────────────────────────────────────────── */
.gp-footer {
  grid-area: footer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 13px 72px;
  border-top: 1px solid rgba(255, 255, 255, 0.065);
}

.gp-copy {
  font-size: 0.74rem;
  color: rgba(255, 255, 255, 0.28);
  font-style: normal;
}

.gp-copy-brand {
  color: #FFD600;
  font-style: normal;
  font-weight: 700;
}

.gp-legal {
  display: flex;
  align-items: center;
  gap: 9px;
}

.gp-legal-link {
  font-size: 0.74rem;
  color: rgba(255, 255, 255, 0.28);
  text-decoration: none;
  transition: color 0.15s;
}
.gp-legal-link:hover { color: rgba(255, 255, 255, 0.6); }

.gp-legal-sep {
  font-size: 0.74rem;
  color: rgba(255, 255, 255, 0.18);
}

/* ─────────────────────────────────────────────────────────────
   DEKORATIVE KURVEN (rechts unten)
───────────────────────────────────────────────────────────── */
.gp-deco {
  position: absolute;
  bottom: 0;
  right: 0;
  pointer-events: none;
  z-index: 0;
}

/* ─────────────────────────────────────────────────────────────
   RESPONSIVE — Mobile (≤ 860 px)
───────────────────────────────────────────────────────────── */
@media (max-width: 860px) {
  .gp {
    grid-template-columns: 1fr;
    grid-template-areas:
      "right"
      "left"
      "footer";
  }

  .gp-center {
    display: none; /* auf Mobile ausblenden */
  }

  .gp-right {
    border-left: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.07);
    padding: 48px 20px;
  }

  .gp-left {
    padding: 40px 20px;
    gap: 24px;
  }

  .gp-h1 {
    font-size: clamp(2.4rem, 7vw, 3rem);
  }

  .gp-benefits {
    grid-template-columns: 1fr;
    gap: 14px;
  }

  .gp-notice { max-width: 100%; }

  .gp-footer {
    flex-direction: column;
    gap: 6px;
    text-align: center;
    padding: 13px 20px;
  }
}

/* ─────────────────────────────────────────────────────────────
   ACCESSIBILITY
───────────────────────────────────────────────────────────── */
:focus-visible {
  outline: 2px solid #FFD600;
  outline-offset: 2px;
  border-radius: 5px;
}

@media (prefers-reduced-motion: reduce) {
  * { transition: none !important; }
}

/* ── Logo — absolut zwischen linker und rechter Spalte ─── */
.gp-center {
  position: absolute;
  /* horizontal: Mittelpunkt der gesamten Seite */
  left: 50%;
  transform: translateX(-50%);
  /* vertikal: auf Höhe der H1 ausgerichtet (~25 % vom Seitenanfang) */
  top: 25%;
  z-index: 2;
  pointer-events: none;
}

.gp-center-img {
  width: 600px;
  height: auto;
  object-fit: contain;
  opacity: 0.95;
  display: block;
}
</style>
