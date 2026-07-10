<template>
  <div class="login-page" role="main">
    <div class="login-card" role="region" aria-label="Anmelden">
      <!-- Logo -->
      <div class="login-logo" aria-hidden="true">
        <span class="login-logo-mark">AM</span>
        <span class="login-logo-text">Access <strong>Mobility</strong></span>
      </div>

      <h1 class="login-title">Anmelden</h1>
      <p class="login-subtitle">Melden Sie sich mit Ihren Zugangsdaten an.</p>

      <!-- Fehler-Anzeige (aria-live für Screenreader) -->
      <div
        v-if="errorMsg"
        class="login-error"
        role="alert"
        aria-live="assertive"
        aria-atomic="true"
      >
        <i class="pi pi-exclamation-circle" aria-hidden="true"></i>
        {{ errorMsg }}
      </div>

      <form class="login-form" @submit.prevent="handleSubmit" novalidate>
        <!-- E-Mail -->
        <div class="form-field">
          <label for="login-email" class="form-label">
            E-Mail-Adresse
            <span class="form-required" aria-hidden="true">*</span>
          </label>
          <input
            id="login-email"
            v-model="email"
            type="email"
            class="form-input"
            :class="{ 'form-input--error': fieldErrors.email }"
            autocomplete="email"
            aria-required="true"
            :aria-describedby="fieldErrors.email ? 'email-error' : undefined"
            :aria-invalid="!!fieldErrors.email"
            placeholder="name@beispiel.de"
          />
          <span v-if="fieldErrors.email" id="email-error" class="form-field-error" role="alert">
            {{ fieldErrors.email }}
          </span>
        </div>

        <!-- Passwort -->
        <div class="form-field">
          <label for="login-password" class="form-label">
            Passwort
            <span class="form-required" aria-hidden="true">*</span>
          </label>
          <div class="form-input-group">
            <input
              id="login-password"
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              class="form-input form-input--with-action"
              :class="{ 'form-input--error': fieldErrors.password }"
              autocomplete="current-password"
              aria-required="true"
              :aria-describedby="fieldErrors.password ? 'password-error' : undefined"
              :aria-invalid="!!fieldErrors.password"
            />
            <button
              type="button"
              class="form-input-action"
              :aria-label="showPassword ? 'Passwort verbergen' : 'Passwort anzeigen'"
              @click="showPassword = !showPassword"
            >
              <i :class="['pi', showPassword ? 'pi-eye-slash' : 'pi-eye']" aria-hidden="true"></i>
            </button>
          </div>
          <span v-if="fieldErrors.password" id="password-error" class="form-field-error" role="alert">
            {{ fieldErrors.password }}
          </span>
        </div>

        <!-- Submit -->
        <button
          type="submit"
          class="am-btn am-btn-primary login-submit"
          :disabled="loading"
          :aria-busy="loading"
        >
          <i v-if="loading" class="pi pi-spin pi-spinner" aria-hidden="true"></i>
          <i v-else class="pi pi-sign-in" aria-hidden="true"></i>
          {{ loading ? 'Anmelden …' : 'Anmelden' }}
        </button>
      </form>

      <!-- Demo-Zugangsdaten -->
      <details class="demo-section">
        <summary class="demo-summary">
          <i class="pi pi-info-circle" aria-hidden="true"></i>
          Demo-Zugangsdaten
        </summary>
        <div class="demo-list" role="list">
          <button
            v-for="demo in demoUsers"
            :key="demo.email"
            type="button"
            class="demo-item"
            role="listitem"
            :aria-label="`Als ${demo.label} anmelden: ${demo.email}`"
            @click="fillDemo(demo)"
          >
            <span class="demo-role">{{ demo.label }}</span>
            <span class="demo-email">{{ demo.email }}</span>
          </button>
        </div>
        <p class="demo-pw-hint">Passwort für alle Konten: <code>Access123!</code></p>
      </details>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const errorMsg = ref('')
const fieldErrors = reactive({ email: '', password: '' })

const demoUsers = [
  { label: 'Fahrgast',           email: 'passenger@access.test' },
  { label: 'Vertrauensperson',   email: 'relative@access.test' },
  { label: 'Organisations-Admin', email: 'orgadmin@access.test' },
  { label: 'Koordinator:in',     email: 'coordinator@access.test' },
  { label: 'Fahrdienst-Admin',   email: 'provider@access.test' },
  { label: 'Disponent:in',       email: 'dispatcher@access.test' },
  { label: 'Fahrer:in',          email: 'driver@access.test' },
  { label: 'Plattform-Admin',    email: 'admin@access.test' },
]

function fillDemo(demo: { email: string }) {
  email.value = demo.email
  password.value = 'Access123!'
  errorMsg.value = ''
  fieldErrors.email = ''
  fieldErrors.password = ''
}

function validate(): boolean {
  fieldErrors.email = ''
  fieldErrors.password = ''
  let ok = true
  if (!email.value.trim()) {
    fieldErrors.email = 'Bitte geben Sie Ihre E-Mail-Adresse ein.'
    ok = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
    fieldErrors.email = 'Bitte geben Sie eine gültige E-Mail-Adresse ein.'
    ok = false
  }
  if (!password.value) {
    fieldErrors.password = 'Bitte geben Sie Ihr Passwort ein.'
    ok = false
  }
  return ok
}

async function handleSubmit() {
  errorMsg.value = ''
  if (!validate()) return

  loading.value = true
  try {
    await authStore.login(email.value.trim(), password.value)
    await router.push('/dashboard')
  } catch (err: unknown) {
    const status = (err as { response?: { status?: number } })?.response?.status
    if (status === 401) {
      errorMsg.value = 'E-Mail-Adresse oder Passwort ist nicht korrekt.'
    } else if (status === 403) {
      errorMsg.value = 'Ihr Konto ist deaktiviert. Bitte kontaktieren Sie den Support.'
    } else {
      errorMsg.value = 'Anmeldung fehlgeschlagen. Bitte versuchen Sie es erneut.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--am-bg-base);
  padding: var(--am-space-l);
}

.login-card {
  width: 100%;
  max-width: 420px;
  background: var(--am-bg-surface);
  border: 1px solid var(--am-border);
  border-radius: var(--am-radius-l);
  padding: var(--am-space-xl);
  display: flex;
  flex-direction: column;
  gap: var(--am-space-m);
}

/* Logo */
.login-logo {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  margin-bottom: var(--am-space-s);
}

.login-logo-mark {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  background: var(--am-accent);
  color: var(--am-text-on-accent);
  font-weight: 800;
  font-size: 0.85rem;
  border-radius: var(--am-radius-s);
  flex-shrink: 0;
}

.login-logo-text {
  font-size: 1rem;
  color: var(--am-text-primary);
  font-weight: 400;
}

.login-logo-text strong {
  font-weight: 700;
}

/* Heading */
.login-title {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--am-text-primary);
  margin: 0;
}

.login-subtitle {
  font-size: 0.875rem;
  color: var(--am-text-secondary);
  margin: 0;
}

/* Error */
.login-error {
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

/* Form */
.login-form {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-m);
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--am-text-primary);
}

.form-required {
  color: var(--am-danger);
  margin-left: 2px;
}

.form-input {
  width: 100%;
  height: 44px;
  background: var(--am-bg-raised);
  border: 1px solid var(--am-border-strong);
  border-radius: var(--am-radius-s);
  color: var(--am-text-primary);
  font-size: 0.9rem;
  padding: 0 var(--am-space-m);
  outline: none;
  transition: border-color var(--am-transition);
  box-sizing: border-box;
}

.form-input:focus {
  border-color: var(--am-accent);
  box-shadow: 0 0 0 3px rgba(255, 214, 0, 0.18);
}

.form-input--error {
  border-color: var(--am-danger) !important;
}

.form-input-group {
  position: relative;
}

.form-input--with-action {
  padding-right: 44px;
}

.form-input-action {
  position: absolute;
  right: 0;
  top: 0;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  color: var(--am-text-secondary);
  cursor: pointer;
  border-radius: 0 var(--am-radius-s) var(--am-radius-s) 0;
  transition: color var(--am-transition);
}

.form-input-action:hover {
  color: var(--am-text-primary);
}

.form-field-error {
  font-size: 0.8rem;
  color: var(--am-danger);
}

/* Submit */
.login-submit {
  width: 100%;
  height: 48px;
  font-size: 0.95rem;
  margin-top: var(--am-space-s);
  justify-content: center;
}

.login-submit:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

/* Demo section */
.demo-section {
  border: 1px solid var(--am-border);
  border-radius: var(--am-radius-s);
  overflow: hidden;
}

.demo-summary {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  padding: var(--am-space-s) var(--am-space-m);
  cursor: pointer;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--am-text-secondary);
  list-style: none;
  user-select: none;
}

.demo-summary::-webkit-details-marker {
  display: none;
}

.demo-summary:hover {
  color: var(--am-text-primary);
  background: var(--am-bg-raised);
}

.demo-list {
  display: flex;
  flex-direction: column;
  border-top: 1px solid var(--am-border);
}

.demo-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px var(--am-space-m);
  background: none;
  border: none;
  border-bottom: 1px solid var(--am-border);
  cursor: pointer;
  text-align: left;
  transition: background var(--am-transition);
  min-height: 44px;
  gap: var(--am-space-m);
}

.demo-item:last-child {
  border-bottom: none;
}

.demo-item:hover {
  background: var(--am-bg-raised);
}

.demo-role {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--am-text-primary);
  min-width: 140px;
}

.demo-email {
  font-size: 0.75rem;
  color: var(--am-text-secondary);
  font-family: monospace;
}

.demo-pw-hint {
  padding: var(--am-space-s) var(--am-space-m);
  font-size: 0.78rem;
  color: var(--am-text-secondary);
  border-top: 1px solid var(--am-border);
  margin: 0;
}

.demo-pw-hint code {
  font-family: monospace;
  color: var(--am-accent);
}
</style>
