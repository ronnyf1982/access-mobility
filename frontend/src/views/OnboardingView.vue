<template>
  <div class="onboarding-page" role="main">
    <div class="onboarding-card" role="region" aria-label="Ersteinrichtung">
      <!-- Logo -->
      <div class="onboarding-logo" aria-hidden="true">
        <span class="logo-mark">AM</span>
        <span class="logo-text">Access <strong>Mobility</strong></span>
      </div>

      <h1 class="onboarding-title">Willkommen bei Access Mobility</h1>
      <p class="onboarding-subtitle">
        Wir möchten die App so einrichten, dass Sie gut für Sie funktioniert.<br />
        Bitte wählen Sie Ihren bevorzugten Bedienungsmodus.
      </p>

      <!-- Status-Meldung (aria-live) -->
      <div
        v-if="statusMsg"
        class="onboarding-status"
        :class="statusMsg.type === 'error' ? 'onboarding-status--error' : 'onboarding-status--success'"
        role="alert"
        aria-live="assertive"
        aria-atomic="true"
      >
        <i
          :class="['pi', statusMsg.type === 'error' ? 'pi-exclamation-circle' : 'pi-check-circle']"
          aria-hidden="true"
        ></i>
        {{ statusMsg.text }}
      </div>

      <!-- Auswahl-Kacheln -->
      <div
        class="choice-grid"
        role="group"
        aria-label="Bedienungsmodus wählen"
        aria-required="true"
      >
        <!-- Sprachführung aktivieren -->
        <button
          type="button"
          class="choice-tile"
          :class="{ 'choice-tile--selected': selected === 'voice' }"
          :aria-pressed="selected === 'voice'"
          aria-describedby="voice-desc"
          @click="select('voice')"
          @keydown.enter="select('voice')"
          @keydown.space.prevent="select('voice')"
        >
          <span class="choice-icon" aria-hidden="true">
            <i class="pi pi-microphone"></i>
          </span>
          <span class="choice-label">Ja, Sprachführung aktivieren</span>
          <span id="voice-desc" class="choice-desc">
            Die App führt Sie per Sprache durch Buchungen und Einstellungen.
            Ideal für blinde und sehbehinderte Nutzer.
          </span>
          <span class="choice-check" aria-hidden="true">
            <i class="pi pi-check-circle"></i>
          </span>
        </button>

        <!-- Normale Einrichtung -->
        <button
          type="button"
          class="choice-tile"
          :class="{ 'choice-tile--selected': selected === 'normal' }"
          :aria-pressed="selected === 'normal'"
          aria-describedby="normal-desc"
          @click="select('normal')"
          @keydown.enter="select('normal')"
          @keydown.space.prevent="select('normal')"
        >
          <span class="choice-icon" aria-hidden="true">
            <i class="pi pi-desktop"></i>
          </span>
          <span class="choice-label">Nein, normale Einrichtung starten</span>
          <span id="normal-desc" class="choice-desc">
            Klassische visuelle Bedienung. Sprachführung kann später in
            den Einstellungen aktiviert werden.
          </span>
          <span class="choice-check" aria-hidden="true">
            <i class="pi pi-check-circle"></i>
          </span>
        </button>
      </div>

      <!-- Bestätigen -->
      <button
        type="button"
        class="am-btn am-btn-primary onboarding-submit"
        :disabled="!selected || loading"
        :aria-busy="loading"
        @click="confirm"
      >
        <i v-if="loading" class="pi pi-spin pi-spinner" aria-hidden="true"></i>
        <i v-else class="pi pi-arrow-right" aria-hidden="true"></i>
        {{ loading ? 'Einrichten …' : 'Weiter' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { saveOnboardingPreferences } from '@/api/onboarding'

const router = useRouter()
const authStore = useAuthStore()

const selected = ref<'voice' | 'normal' | null>(null)
const loading = ref(false)
const statusMsg = ref<{ type: 'error' | 'success'; text: string } | null>(null)

function select(choice: 'voice' | 'normal') {
  selected.value = choice
  statusMsg.value = null
}

async function confirm() {
  if (!selected.value) return
  loading.value = true
  statusMsg.value = null
  try {
    const updated = await saveOnboardingPreferences(selected.value === 'voice')
    authStore.user = updated
    const role = updated.role
    const isPassengerRole = role === 'passenger' || role === 'trusted_person' || role === 'organization_coordinator'
    if (isPassengerRole && selected.value === 'voice') {
      // Voice mode: geführten Mobilitätscheck starten
      await router.push('/mobility-profile/assistant')
    } else if (isPassengerRole) {
      await router.push('/mobility-profile')
    } else {
      await router.push('/dashboard')
    }
  } catch {
    statusMsg.value = { type: 'error', text: 'Einstellungen konnten nicht gespeichert werden. Bitte versuchen Sie es erneut.' }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.onboarding-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--am-bg-base);
  padding: var(--am-space-l);
}

.onboarding-card {
  width: 100%;
  max-width: 560px;
  background: var(--am-bg-surface);
  border: 1px solid var(--am-border);
  border-radius: var(--am-radius-l);
  padding: var(--am-space-xl);
  display: flex;
  flex-direction: column;
  gap: var(--am-space-l);
}

/* Logo */
.onboarding-logo {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
}

.logo-mark {
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

.logo-text {
  font-size: 1rem;
  color: var(--am-text-primary);
  font-weight: 400;
}

.logo-text strong {
  font-weight: 700;
}

/* Heading */
.onboarding-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--am-text-primary);
  margin: 0;
  line-height: 1.2;
}

.onboarding-subtitle {
  font-size: 0.9rem;
  color: var(--am-text-secondary);
  margin: 0;
  line-height: 1.6;
}

/* Status */
.onboarding-status {
  display: flex;
  align-items: flex-start;
  gap: var(--am-space-s);
  padding: var(--am-space-s) var(--am-space-m);
  border-radius: var(--am-radius-s);
  font-size: 0.875rem;
}

.onboarding-status--error {
  background: var(--am-danger-bg);
  border: 1px solid var(--am-danger);
  color: var(--am-danger);
}

.onboarding-status--success {
  background: color-mix(in srgb, var(--am-success) 12%, transparent);
  border: 1px solid var(--am-success);
  color: var(--am-success);
}

/* Choice grid */
.choice-grid {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-m);
}

.choice-tile {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: var(--am-space-s);
  padding: var(--am-space-l);
  background: var(--am-bg-raised);
  border: 2px solid var(--am-border);
  border-radius: var(--am-radius-m);
  cursor: pointer;
  text-align: left;
  transition: border-color var(--am-transition), background var(--am-transition);
  min-height: 88px;
}

.choice-tile:hover {
  border-color: var(--am-border-strong);
  background: var(--am-bg-surface);
}

.choice-tile:focus-visible {
  outline: 2px solid var(--am-accent);
  outline-offset: 2px;
}

.choice-tile--selected {
  border-color: var(--am-accent);
  background: color-mix(in srgb, var(--am-accent) 8%, var(--am-bg-raised));
}

.choice-icon {
  font-size: 1.8rem;
  color: var(--am-accent);
  line-height: 1;
}

.choice-label {
  font-size: 1rem;
  font-weight: 700;
  color: var(--am-text-primary);
}

.choice-desc {
  font-size: 0.85rem;
  color: var(--am-text-secondary);
  line-height: 1.5;
}

.choice-check {
  position: absolute;
  top: var(--am-space-m);
  right: var(--am-space-m);
  font-size: 1.25rem;
  color: var(--am-accent);
  opacity: 0;
  transition: opacity var(--am-transition);
}

.choice-tile--selected .choice-check {
  opacity: 1;
}

/* Submit */
.onboarding-submit {
  width: 100%;
  height: 52px;
  font-size: 1rem;
  justify-content: center;
}

.onboarding-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
