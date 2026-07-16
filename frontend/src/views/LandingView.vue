<template>
  <div class="cs-page">
    <main class="cs-main" id="main-content">
      <div class="cs-layout">

        <!-- ── Linker Bereich: Marke & Info ──────────────────── -->
        <section class="cs-brand" aria-labelledby="cs-headline">
          <RouterLink to="/" class="cs-logo-link" aria-label="Fahrando – Startseite">
            <FahrandoLogo variant="large" />
          </RouterLink>

          <h1 id="cs-headline" class="cs-headline">
            <span class="cs-headline-light">Hier entsteht</span><br>
            <span class="cs-headline-accent">etwas Großes.</span>
          </h1>
          <div class="cs-headline-rule" aria-hidden="true"></div>

          <p class="cs-desc">
            Fahrando entwickelt eine Plattform für barrierefreie Mobilität –
            für selbstbestimmte Wege und eine offenere Welt für alle.
          </p>

          <!-- Nutzenpunkte -->
          <ul class="cs-benefits" role="list" aria-label="Unsere Versprechen">
            <li class="cs-benefit">
              <span class="cs-benefit-icon" aria-hidden="true">
                <i class="pi pi-heart"></i>
              </span>
              <div>
                <strong class="cs-benefit-title">Barrierefreie Mobilität</strong>
                <span class="cs-benefit-sub">für alle Lebenslagen</span>
              </div>
            </li>
            <li class="cs-benefit">
              <span class="cs-benefit-icon" aria-hidden="true">
                <i class="pi pi-map"></i>
              </span>
              <div>
                <strong class="cs-benefit-title">Bessere Informationen</strong>
                <span class="cs-benefit-sub">für bessere Wege</span>
              </div>
            </li>
            <li class="cs-benefit">
              <span class="cs-benefit-icon" aria-hidden="true">
                <i class="pi pi-users"></i>
              </span>
              <div>
                <strong class="cs-benefit-title">Gemeinsam für</strong>
                <span class="cs-benefit-sub">eine offene Welt</span>
              </div>
            </li>
          </ul>

          <!-- Hinweisbox -->
          <div class="cs-notice" role="note">
            <i class="pi pi-calendar" aria-hidden="true"></i>
            <div>
              <strong class="cs-notice-title">Der öffentliche Auftritt folgt bald.</strong>
              <p class="cs-notice-text">Vielen Dank für dein Interesse und deine Unterstützung.</p>
            </div>
          </div>
        </section>

        <!-- ── Rechter Bereich: Login-Card ──────────────────── -->
        <section class="cs-login-section" aria-label="Testzugang">
          <!-- Eingeloggt: Dashboard-Hinweis -->
          <div v-if="isAuthenticated" class="cs-login-card cs-already-in">
            <div class="cs-already-icon" aria-hidden="true">
              <i class="pi pi-check-circle"></i>
            </div>
            <h2 class="cs-card-title">Willkommen zurück</h2>
            <p class="cs-already-hint">Du bist bereits angemeldet.</p>
            <RouterLink to="/dashboard" class="am-btn am-btn-primary cs-btn">
              <i class="pi pi-th-large" aria-hidden="true"></i>
              Zum Dashboard
            </RouterLink>
            <button class="am-btn cs-btn-logout" @click="handleLogout">
              <i class="pi pi-sign-out" aria-hidden="true"></i>
              Abmelden
            </button>
          </div>

          <!-- Nicht eingeloggt: Login-Formular -->
          <div v-else class="cs-login-card">
            <!-- Shield-Icon -->
            <div class="cs-shield" aria-hidden="true">
              <i class="pi pi-shield"></i>
            </div>

            <h2 class="cs-card-title" id="cs-login-title">Geschützter Testzugang</h2>
            <p class="cs-card-sub" aria-describedby="cs-login-title">Nur für Tester</p>

            <div class="cs-divider" aria-hidden="true"></div>

            <!-- Fehler aria-live -->
            <div
              v-if="errorMsg"
              class="cs-error"
              role="alert"
              aria-live="assertive"
              aria-atomic="true"
            >
              <i class="pi pi-exclamation-circle" aria-hidden="true"></i>
              <span>{{ errorMsg }}</span>
            </div>

            <form
              class="cs-form"
              @submit.prevent="handleSubmit"
              novalidate
              aria-labelledby="cs-login-title"
            >
              <!-- E-Mail -->
              <div class="cs-field">
                <label for="cs-email" class="cs-label">E-Mail-Adresse</label>
                <input
                  id="cs-email"
                  v-model="email"
                  type="email"
                  class="cs-input"
                  :class="{ 'cs-input--error': fieldErrors.email }"
                  autocomplete="username"
                  aria-required="true"
                  :aria-invalid="!!fieldErrors.email"
                  :aria-describedby="fieldErrors.email ? 'cs-email-err' : undefined"
                  placeholder="E-Mail-Adresse"
                />
                <span
                  v-if="fieldErrors.email"
                  id="cs-email-err"
                  class="cs-field-error"
                  role="alert"
                >{{ fieldErrors.email }}</span>
              </div>

              <!-- Passwort -->
              <div class="cs-field">
                <label for="cs-password" class="cs-label">Passwort</label>
                <div class="cs-input-group">
                  <input
                    id="cs-password"
                    v-model="password"
                    :type="showPw ? 'text' : 'password'"
                    class="cs-input cs-input--pw"
                    :class="{ 'cs-input--error': fieldErrors.password }"
                    autocomplete="current-password"
                    aria-required="true"
                    :aria-invalid="!!fieldErrors.password"
                    :aria-describedby="fieldErrors.password ? 'cs-pw-err' : undefined"
                    placeholder="Passwort"
                  />
                  <button
                    type="button"
                    class="cs-pw-toggle"
                    :aria-label="showPw ? 'Passwort verbergen' : 'Passwort anzeigen'"
                    @click="showPw = !showPw"
                  >
                    <i :class="['pi', showPw ? 'pi-eye-slash' : 'pi-eye']" aria-hidden="true"></i>
                  </button>
                </div>
                <span
                  v-if="fieldErrors.password"
                  id="cs-pw-err"
                  class="cs-field-error"
                  role="alert"
                >{{ fieldErrors.password }}</span>
              </div>

              <!-- Submit -->
              <button
                type="submit"
                class="am-btn am-btn-primary cs-submit"
                :disabled="loading"
                :aria-busy="loading"
              >
                <i v-if="loading" class="pi pi-spin pi-spinner" aria-hidden="true"></i>
                <i v-else class="pi pi-arrow-right" aria-hidden="true"></i>
                {{ loading ? 'Anmeldung läuft …' : 'Einloggen' }}
              </button>
            </form>

            <!-- Hinweis -->
            <p class="cs-lock-hint" aria-hidden="true">
              <i class="pi pi-lock"></i>
              Dieser Bereich ist passwortgeschützt.
            </p>
          </div>
        </section>
      </div>
    </main>

    <!-- Footer -->
    <footer class="cs-footer" role="contentinfo">
      <p class="cs-footer-copy">
        &copy; {{ year }} <span class="cs-footer-brand">Fahrando</span>. Alle Rechte vorbehalten.
      </p>
      <nav class="cs-footer-links" aria-label="Rechtliche Links">
        <RouterLink to="/impressum" class="cs-footer-link">Impressum</RouterLink>
        <span class="cs-footer-sep" aria-hidden="true">|</span>
        <RouterLink to="/datenschutz" class="cs-footer-link">Datenschutz</RouterLink>
      </nav>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import FahrandoLogo from '@/components/branding/FahrandoLogo.vue'

const router = useRouter()
const authStore = useAuthStore()

const isAuthenticated = computed(() => authStore.isAuthenticated)
const year = new Date().getFullYear()

const email = ref('')
const password = ref('')
const showPw = ref(false)
const loading = ref(false)
const errorMsg = ref('')
const fieldErrors = reactive({ email: '', password: '' })

function validate(): boolean {
  fieldErrors.email = ''
  fieldErrors.password = ''
  let ok = true
  if (!email.value.trim()) {
    fieldErrors.email = 'Bitte E-Mail-Adresse eingeben.'
    ok = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
    fieldErrors.email = 'Bitte eine gültige E-Mail-Adresse eingeben.'
    ok = false
  }
  if (!password.value) {
    fieldErrors.password = 'Bitte Passwort eingeben.'
    ok = false
  }
  return ok
}

async function handleSubmit() {
  errorMsg.value = ''
  if (!validate()) return
  if (loading.value) return

  loading.value = true
  try {
    await authStore.login(email.value.trim(), password.value)
    // Onboarding and role routing handled by router guard
    const user = authStore.user
    if (user?.needs_onboarding) {
      await router.push('/onboarding')
    } else {
      await router.push('/dashboard')
    }
  } catch (err: unknown) {
    const httpStatus = (err as { response?: { status?: number } })?.response?.status
    if (httpStatus === 401) {
      errorMsg.value = 'E-Mail-Adresse oder Passwort sind nicht korrekt.'
    } else if (httpStatus === 403) {
      errorMsg.value = 'Dieser Zugang ist derzeit deaktiviert.'
    } else {
      errorMsg.value = 'Der Testzugang ist momentan nicht erreichbar. Bitte versuche es später erneut.'
    }
    password.value = ''
  } finally {
    loading.value = false
  }
}

async function handleLogout() {
  await authStore.logout()
  // Stay on / — already here
}
</script>

<style scoped>
/* ── Seite ────────────────────────────────────────────── */
.cs-page {
  min-height: 100dvh;
  background: var(--am-bg-base);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow-x: hidden;
}

/* Subtiler Hintergrund-Effekt (kein Foto, keine Stockbilder) */
.cs-page::before {
  content: '';
  position: fixed;
  bottom: -20%;
  right: -10%;
  width: 60vw;
  height: 60vw;
  max-width: 700px;
  max-height: 700px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 214, 0, 0.04) 0%, transparent 70%);
  pointer-events: none;
}

.cs-main {
  flex: 1;
  display: flex;
  align-items: center;
  padding: var(--am-space-xl) var(--am-space-l);
}

/* ── Zweispaltiges Layout ─────────────────────────────── */
.cs-layout {
  width: 100%;
  max-width: 1100px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1.15fr 1fr;
  gap: 80px;
  align-items: center;
}

@media (max-width: 900px) {
  .cs-layout {
    grid-template-columns: 1fr;
    gap: var(--am-space-xl);
  }
  .cs-main {
    align-items: flex-start;
    padding-top: 40px;
  }
}

/* ── Linker Bereich ───────────────────────────────────── */
.cs-brand {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-l);
}

.cs-logo-link {
  text-decoration: none;
  display: inline-block;
}

.cs-headline {
  font-size: clamp(2.2rem, 5vw, 3.6rem);
  font-weight: 800;
  line-height: 1.12;
  margin: 0;
}

.cs-headline-light {
  color: var(--am-text-primary);
}

.cs-headline-accent {
  color: var(--am-accent);
}

.cs-headline-rule {
  width: 48px;
  height: 3px;
  background: var(--am-accent);
  border-radius: 2px;
  margin-top: -4px;
}

.cs-desc {
  font-size: 1rem;
  color: var(--am-text-secondary);
  line-height: 1.75;
  max-width: 420px;
  margin: 0;
}

/* Nutzenpunkte */
.cs-benefits {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  gap: var(--am-space-xl);
}

@media (max-width: 600px) {
  .cs-benefits {
    flex-direction: column;
    gap: var(--am-space-m);
  }
}

.cs-benefit {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: var(--am-space-s);
  flex: 1;
}

.cs-benefit-icon {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--am-accent-bg);
  border: 1px solid rgba(255, 214, 0, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.cs-benefit-icon .pi {
  color: var(--am-accent);
  font-size: 1.1rem;
}

.cs-benefit-title {
  display: block;
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--am-text-primary);
  line-height: 1.3;
}

.cs-benefit-sub {
  display: block;
  font-size: 0.75rem;
  color: var(--am-text-secondary);
  line-height: 1.4;
}

/* Hinweisbox */
.cs-notice {
  display: flex;
  align-items: flex-start;
  gap: var(--am-space-m);
  background: var(--am-bg-surface);
  border: 1px solid var(--am-border);
  border-radius: var(--am-radius-m);
  padding: var(--am-space-m);
}

.cs-notice > .pi {
  color: var(--am-accent);
  font-size: 1.2rem;
  margin-top: 2px;
  flex-shrink: 0;
}

.cs-notice-title {
  display: block;
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--am-text-primary);
  margin-bottom: 4px;
}

.cs-notice-text {
  margin: 0;
  font-size: 0.8rem;
  color: var(--am-text-secondary);
}

/* ── Rechter Bereich: Login-Card ──────────────────────── */
.cs-login-section {
  display: flex;
  justify-content: center;
}

.cs-login-card {
  width: 100%;
  max-width: 400px;
  background: var(--am-bg-surface);
  border: 1px solid var(--am-border);
  border-radius: var(--am-radius-l);
  padding: 36px;
  display: flex;
  flex-direction: column;
  gap: var(--am-space-m);
}

/* Shield-Icon */
.cs-shield {
  width: 56px;
  height: 56px;
  background: var(--am-accent-bg);
  border: 1px solid rgba(255, 214, 0, 0.25);
  border-radius: var(--am-radius-m);
  display: flex;
  align-items: center;
  justify-content: center;
  align-self: center;
}

.cs-shield .pi {
  color: var(--am-accent);
  font-size: 1.5rem;
}

.cs-card-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--am-text-primary);
  text-align: center;
  margin: 0;
}

.cs-card-sub {
  font-size: 0.85rem;
  color: var(--am-text-secondary);
  text-align: center;
  margin: 0;
}

.cs-divider {
  height: 1px;
  background: var(--am-border);
  margin: 0 -4px;
}

/* Fehler */
.cs-error {
  display: flex;
  align-items: flex-start;
  gap: var(--am-space-s);
  padding: var(--am-space-s) var(--am-space-m);
  background: var(--am-danger-bg);
  border: 1px solid var(--am-danger);
  border-radius: var(--am-radius-s);
  color: var(--am-danger);
  font-size: 0.875rem;
}

/* Formular */
.cs-form {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-m);
}

.cs-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.cs-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--am-text-primary);
}

.cs-input {
  width: 100%;
  height: 48px;
  background: var(--am-bg-raised);
  border: 1px solid var(--am-border-strong);
  border-radius: var(--am-radius-s);
  color: var(--am-text-primary);
  font-size: 0.925rem;
  padding: 0 var(--am-space-m);
  outline: none;
  box-sizing: border-box;
  transition: border-color var(--am-transition), box-shadow var(--am-transition);
}

.cs-input:focus {
  border-color: var(--am-accent);
  box-shadow: 0 0 0 3px rgba(255, 214, 0, 0.18);
}

.cs-input--error {
  border-color: var(--am-danger) !important;
}

.cs-input-group {
  position: relative;
}

.cs-input--pw {
  padding-right: 48px;
}

.cs-pw-toggle {
  position: absolute;
  right: 0;
  top: 0;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  color: var(--am-text-secondary);
  cursor: pointer;
  transition: color var(--am-transition);
  border-radius: 0 var(--am-radius-s) var(--am-radius-s) 0;
}

.cs-pw-toggle:hover {
  color: var(--am-text-primary);
}

.cs-field-error {
  font-size: 0.8rem;
  color: var(--am-danger);
}

/* Submit-Button */
.cs-submit {
  width: 100%;
  height: 52px;
  font-size: 1rem;
  font-weight: 700;
  justify-content: center;
  gap: var(--am-space-s);
  margin-top: 4px;
}

.cs-submit:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

/* Lock-Hinweis */
.cs-lock-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 0.78rem;
  color: var(--am-text-muted);
  margin: 0;
}

.cs-lock-hint .pi {
  font-size: 0.78rem;
}

/* Eingeloggt-State */
.cs-already-in {
  align-items: center;
  text-align: center;
}

.cs-already-icon {
  width: 56px;
  height: 56px;
  background: var(--am-success-bg);
  border: 1px solid rgba(34, 197, 94, 0.25);
  border-radius: var(--am-radius-m);
  display: flex;
  align-items: center;
  justify-content: center;
}

.cs-already-icon .pi {
  color: var(--am-success);
  font-size: 1.5rem;
}

.cs-already-hint {
  font-size: 0.875rem;
  color: var(--am-text-secondary);
  margin: 0;
}

.cs-btn {
  width: 100%;
  justify-content: center;
  height: 52px;
  font-size: 1rem;
  font-weight: 700;
}

.cs-btn-logout {
  width: 100%;
  height: 44px;
  background: none;
  border: 1px solid var(--am-border);
  border-radius: var(--am-radius-s);
  color: var(--am-text-secondary);
  font-size: 0.875rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--am-space-s);
  transition: color var(--am-transition), border-color var(--am-transition), background var(--am-transition);
}

.cs-btn-logout:hover {
  color: var(--am-danger);
  border-color: var(--am-danger);
  background: var(--am-danger-bg);
}

/* ── Footer ───────────────────────────────────────────── */
.cs-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--am-space-m) var(--am-space-l);
  border-top: 1px solid var(--am-border);
  flex-wrap: wrap;
  gap: var(--am-space-s);
}

.cs-footer-copy {
  font-size: 0.78rem;
  color: var(--am-text-muted);
  margin: 0;
}

.cs-footer-brand {
  color: var(--am-accent);
  font-weight: 700;
}

.cs-footer-links {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
}

.cs-footer-link {
  font-size: 0.78rem;
  color: var(--am-text-muted);
  text-decoration: none;
  transition: color var(--am-transition);
}

.cs-footer-link:hover {
  color: var(--am-text-secondary);
}

.cs-footer-sep {
  font-size: 0.78rem;
  color: var(--am-border-strong);
}

/* ── Fokus-Ring (Accessibility) ───────────────────────── */
:focus-visible {
  outline: 2px solid var(--am-accent);
  outline-offset: 3px;
  border-radius: var(--am-radius-s);
}

/* ── reduced motion ───────────────────────────────────── */
@media (prefers-reduced-motion: reduce) {
  * {
    transition: none !important;
  }
}
</style>
