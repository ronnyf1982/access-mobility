<template>
  <div class="gate-page">
    <main class="gate-main" id="main-content">
      <div class="gate-card">

        <!-- Logo -->
        <div class="gate-logo" aria-hidden="true">
          <FahrandoLogo variant="default" />
        </div>

        <div class="gate-divider" aria-hidden="true"></div>

        <!-- Shield-Icon -->
        <div class="gate-shield" aria-hidden="true">
          <i class="pi pi-shield"></i>
        </div>

        <h1 class="gate-title" id="gate-title">Geschützter Testzugang</h1>
        <p class="gate-hint" aria-describedby="gate-title">
          Diese Testseite ist nur für freigeschaltete Tester zugänglich.
        </p>

        <!-- Fehlermeldung -->
        <div
          v-if="errorMsg"
          class="gate-error"
          role="alert"
          aria-live="assertive"
          aria-atomic="true"
        >
          <i class="pi pi-exclamation-circle" aria-hidden="true"></i>
          <span>{{ errorMsg }}</span>
        </div>

        <!-- Formular -->
        <form
          class="gate-form"
          @submit.prevent="handleSubmit"
          novalidate
          aria-labelledby="gate-title"
        >
          <div class="gate-field">
            <label for="gate-code" class="gate-label">Zugangscode</label>
            <div class="gate-input-wrap">
              <input
                id="gate-code"
                ref="inputRef"
                v-model="code"
                :type="showCode ? 'text' : 'password'"
                class="gate-input"
                :class="{ 'gate-input--error': errorMsg }"
                autocomplete="current-password"
                aria-required="true"
                :aria-invalid="!!errorMsg"
                placeholder="Zugangscode eingeben"
              />
              <button
                type="button"
                class="gate-eye"
                :aria-label="showCode ? 'Code verbergen' : 'Code anzeigen'"
                @click="showCode = !showCode"
              >
                <i :class="['pi', showCode ? 'pi-eye-slash' : 'pi-eye']" aria-hidden="true"></i>
              </button>
            </div>
          </div>

          <button
            type="submit"
            class="am-btn am-btn-primary gate-submit"
            :disabled="loading || !code"
            :aria-busy="loading"
          >
            <i v-if="loading" class="pi pi-spin pi-spinner" aria-hidden="true"></i>
            <i v-else class="pi pi-arrow-right" aria-hidden="true"></i>
            {{ loading ? 'Prüfen …' : 'Website öffnen' }}
          </button>
        </form>

      </div>
    </main>

    <footer class="gate-footer" role="contentinfo">
      <p class="gate-footer-text">
        &copy; {{ year }} <span class="gate-footer-brand">Fahrando</span>. Alle Rechte vorbehalten.
      </p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import FahrandoLogo from '@/components/branding/FahrandoLogo.vue'

const router = useRouter()
const year = new Date().getFullYear()

const code = ref('')
const showCode = ref(false)
const loading = ref(false)
const errorMsg = ref('')
const inputRef = ref<HTMLInputElement | null>(null)

onMounted(() => {
  inputRef.value?.focus()
})

async function handleSubmit() {
  if (!code.value || loading.value) return
  errorMsg.value = ''
  loading.value = true

  try {
    const res = await fetch('/api/v1/public/test-access', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code: code.value }),
    })

    if (res.ok) {
      sessionStorage.setItem('fahrando_unlocked', '1')
      await router.push('/')
    } else if (res.status === 401) {
      errorMsg.value = 'Zugangsdaten nicht korrekt.'
      code.value = ''
    } else if (res.status === 503) {
      errorMsg.value = 'Testzugang derzeit nicht verfügbar.'
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
/* ── Seite ────────────────────────────────────────────── */
.gate-page {
  min-height: 100dvh;
  background: var(--am-bg-base);
  display: flex;
  flex-direction: column;
}

.gate-main {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--am-space-xl) var(--am-space-m);
}

/* ── Card ─────────────────────────────────────────────── */
.gate-card {
  width: 100%;
  max-width: 400px;
  background: var(--am-bg-surface);
  border: 1px solid var(--am-border);
  border-radius: var(--am-radius-l);
  padding: 40px 36px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--am-space-m);
}

.gate-logo {
  margin-bottom: 4px;
}

.gate-divider {
  width: 100%;
  height: 1px;
  background: var(--am-border);
  margin: 4px 0;
}

/* Shield-Icon */
.gate-shield {
  width: 56px;
  height: 56px;
  background: var(--am-accent-bg);
  border: 1px solid rgba(255, 214, 0, 0.25);
  border-radius: var(--am-radius-m);
  display: flex;
  align-items: center;
  justify-content: center;
}

.gate-shield .pi {
  color: var(--am-accent);
  font-size: 1.5rem;
}

.gate-title {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--am-text-primary);
  text-align: center;
  margin: 0;
}

.gate-hint {
  font-size: 0.875rem;
  color: var(--am-text-secondary);
  text-align: center;
  margin: 0;
  line-height: 1.5;
}

/* Fehler */
.gate-error {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  width: 100%;
  padding: var(--am-space-s) var(--am-space-m);
  background: var(--am-danger-bg);
  border: 1px solid var(--am-danger);
  border-radius: var(--am-radius-s);
  color: var(--am-danger);
  font-size: 0.875rem;
}

/* Formular */
.gate-form {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: var(--am-space-m);
}

.gate-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.gate-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--am-text-primary);
}

.gate-input-wrap {
  position: relative;
}

.gate-input {
  width: 100%;
  height: 48px;
  background: var(--am-bg-raised);
  border: 1px solid var(--am-border-strong);
  border-radius: var(--am-radius-s);
  color: var(--am-text-primary);
  font-size: 0.925rem;
  padding: 0 48px 0 var(--am-space-m);
  outline: none;
  box-sizing: border-box;
  transition: border-color var(--am-transition), box-shadow var(--am-transition);
}

.gate-input:focus {
  border-color: var(--am-accent);
  box-shadow: 0 0 0 3px rgba(255, 214, 0, 0.18);
}

.gate-input--error {
  border-color: var(--am-danger) !important;
}

.gate-eye {
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
}

.gate-eye:hover {
  color: var(--am-text-primary);
}

/* Submit-Button */
.gate-submit {
  width: 100%;
  height: 52px;
  font-size: 1rem;
  font-weight: 700;
  justify-content: center;
  gap: var(--am-space-s);
}

.gate-submit:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

/* ── Footer ───────────────────────────────────────────── */
.gate-footer {
  padding: var(--am-space-m);
  text-align: center;
  border-top: 1px solid var(--am-border);
}

.gate-footer-text {
  font-size: 0.78rem;
  color: var(--am-text-muted);
  margin: 0;
}

.gate-footer-brand {
  color: var(--am-accent);
  font-weight: 700;
}

/* ── Accessibility ────────────────────────────────────── */
:focus-visible {
  outline: 2px solid var(--am-accent);
  outline-offset: 3px;
  border-radius: var(--am-radius-s);
}

@media (prefers-reduced-motion: reduce) {
  * { transition: none !important; }
}
</style>
