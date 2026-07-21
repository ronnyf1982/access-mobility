<template>
  <div v-if="visible" class="efm-overlay" role="dialog" aria-modal="true" aria-labelledby="efm-title" @click.self="$emit('close')">
    <div class="efm-dialog">
      <header class="efm-header">
        <div class="efm-header-icon" aria-hidden="true"><i class="pi pi-shield"></i></div>
        <div>
          <h2 id="efm-title" class="efm-title">Notfallakte</h2>
          <p class="efm-subtitle">{{ data?.passenger_display_name ?? 'Fahrgast' }}</p>
        </div>
        <button class="efm-close" aria-label="Schließen" @click="$emit('close')">
          <i class="pi pi-times" aria-hidden="true"></i>
        </button>
      </header>

      <div v-if="loading" class="efm-loading" role="status">
        <i class="pi pi-spin pi-spinner" aria-hidden="true"></i>
        Notfallakte wird geladen …
      </div>

      <div v-else-if="error" class="efm-error" role="alert">
        <i class="pi pi-exclamation-circle" aria-hidden="true"></i>
        {{ error }}
      </div>

      <div v-else-if="data" class="efm-body">
        <!-- Kein Profil -->
        <div v-if="!data.disabilities_visible && !data.medication_visible && !data.emergency_notes_visible && !data.communication_notes_visible && data.visible_contacts.length === 0" class="efm-empty">
          <i class="pi pi-info-circle" aria-hidden="true"></i>
          Für diesen Fahrgast wurden keine Daten für den Fahrer freigegeben.
        </div>

        <!-- Behinderungen / Erkrankungen -->
        <section v-if="data.disabilities_visible" class="efm-section">
          <h3 class="efm-section-title"><i class="pi pi-heart" aria-hidden="true"></i> Erkrankungen / Behinderungen</h3>
          <div class="efm-tag-row">
            <span v-if="data.uses_wheelchair" class="efm-tag">Rollstuhlnutzung</span>
            <span v-if="data.has_epilepsy" class="efm-tag efm-tag--warn">Epilepsie</span>
            <span v-if="data.is_blind_or_visually_impaired" class="efm-tag">Sehbehinderung</span>
            <span v-if="data.is_deaf_or_hard_of_hearing" class="efm-tag">Hörbehinderung</span>
            <span v-if="data.is_mute" class="efm-tag">Sprechbehinderung</span>
          </div>
          <p v-if="data.known_conditions" class="efm-text">{{ data.known_conditions }}</p>
          <p v-if="data.other_disabilities_notes" class="efm-text efm-text--sub">{{ data.other_disabilities_notes }}</p>
        </section>

        <!-- Kommunikationshinweise -->
        <section v-if="data.communication_notes_visible && data.communication_notes" class="efm-section">
          <h3 class="efm-section-title"><i class="pi pi-comment" aria-hidden="true"></i> Kommunikationshinweise</h3>
          <p class="efm-text">{{ data.communication_notes }}</p>
        </section>

        <!-- Notfallhinweise -->
        <section v-if="data.emergency_notes_visible && (data.emergency_care_notes || data.what_helps_notes || data.what_to_avoid_notes)" class="efm-section">
          <h3 class="efm-section-title"><i class="pi pi-exclamation-triangle" aria-hidden="true"></i> Notfallhinweise</h3>
          <div v-if="data.emergency_care_notes">
            <p class="efm-field-label">Im Notfall:</p>
            <p class="efm-text">{{ data.emergency_care_notes }}</p>
          </div>
          <div v-if="data.what_helps_notes">
            <p class="efm-field-label">Das hilft:</p>
            <p class="efm-text">{{ data.what_helps_notes }}</p>
          </div>
          <div v-if="data.what_to_avoid_notes">
            <p class="efm-field-label">Das vermeiden:</p>
            <p class="efm-text efm-text--danger">{{ data.what_to_avoid_notes }}</p>
          </div>
        </section>

        <!-- Kontakte -->
        <section v-if="data.visible_contacts.length > 0" class="efm-section">
          <h3 class="efm-section-title"><i class="pi pi-phone" aria-hidden="true"></i> Notfallkontakte</h3>
          <div v-for="contact in data.visible_contacts" :key="contact.id" class="efm-contact">
            <div class="efm-contact-info">
              <span class="efm-contact-name">{{ contact.name }}</span>
              <span v-if="contact.role_label" class="efm-contact-role">{{ contact.role_label }}</span>
            </div>
            <a v-if="contact.phone_number" :href="`tel:${contact.phone_number}`" class="efm-call-btn" :aria-label="`${contact.name} anrufen`">
              <i class="pi pi-phone" aria-hidden="true"></i>
              {{ contact.phone_number }}
            </a>
            <span v-else class="efm-no-phone">Keine Telefonnummer</span>
          </div>
        </section>

        <!-- Standort -->
        <section v-if="data.current_location_label" class="efm-section efm-section--location">
          <h3 class="efm-section-title"><i class="pi pi-map-marker" aria-hidden="true"></i> Aktueller Abholort</h3>
          <p class="efm-text">{{ data.current_location_label }}</p>
        </section>

        <!-- Haftungshinweis -->
        <p class="efm-disclaimer">{{ data.medical_disclaimer }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { getEmergencyFile } from '@/api/passengerContacts'
import type { EmergencyFileResponse } from '@/types'

const props = defineProps<{
  visible: boolean
  requestId: string | null
}>()

defineEmits<{ (e: 'close'): void }>()

const data = ref<EmergencyFileResponse | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

watch(
  () => [props.visible, props.requestId],
  async ([vis, id]) => {
    if (!vis || !id) {
      data.value = null
      error.value = null
      return
    }
    loading.value = true
    error.value = null
    try {
      data.value = await getEmergencyFile(id as string, false)
    } catch {
      error.value = 'Notfallakte konnte nicht geladen werden.'
    } finally {
      loading.value = false
    }
  },
  { immediate: true },
)
</script>

<style scoped>
.efm-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.65);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: var(--am-space-m);
}

.efm-dialog {
  background: var(--am-bg-card);
  border-radius: var(--am-radius-m);
  border: 1px solid var(--am-border);
  width: 100%;
  max-width: 540px;
  max-height: 90vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.efm-header {
  display: flex;
  align-items: center;
  gap: var(--am-space-m);
  padding: var(--am-space-l);
  border-bottom: 1px solid var(--am-border);
  position: sticky;
  top: 0;
  background: var(--am-bg-card);
  z-index: 1;
}

.efm-header-icon {
  width: 40px;
  height: 40px;
  background: rgba(34,197,94,0.15);
  color: var(--am-success, #16a34a);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  flex-shrink: 0;
}

.efm-title {
  font-size: 1rem;
  font-weight: 700;
  margin: 0;
  color: var(--am-text-primary);
}

.efm-subtitle {
  font-size: 0.8rem;
  color: var(--am-text-secondary);
  margin: 2px 0 0;
}

.efm-close {
  margin-left: auto;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--am-text-secondary);
  padding: 6px;
  border-radius: var(--am-radius-s);
  display: flex;
  align-items: center;
  font-size: 1rem;
}

.efm-body {
  padding: var(--am-space-l);
  display: flex;
  flex-direction: column;
  gap: var(--am-space-m);
}

.efm-loading, .efm-error, .efm-empty {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  padding: var(--am-space-xl);
  justify-content: center;
  font-size: 0.9rem;
  color: var(--am-text-secondary);
}

.efm-error { color: var(--am-danger, #dc2626); }

.efm-section {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-s);
  padding: var(--am-space-m);
  background: var(--am-bg-raised);
  border-radius: var(--am-radius-s);
  border: 1px solid var(--am-border);
}

.efm-section--location {
  border-color: var(--am-accent);
}

.efm-section-title {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--am-text-primary);
  margin: 0;
}

.efm-section-title .pi { color: var(--am-accent); }

.efm-tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.efm-tag {
  font-size: 0.78rem;
  font-weight: 600;
  padding: 2px 10px;
  border-radius: 99px;
  background: var(--am-bg-card);
  border: 1px solid var(--am-border);
  color: var(--am-text-primary);
}

.efm-tag--warn {
  background: rgba(245,158,11,0.12);
  border-color: var(--am-warning, #f59e0b);
  color: var(--am-warning, #d97706);
}

.efm-text {
  font-size: 0.875rem;
  color: var(--am-text-primary);
  margin: 0;
  line-height: 1.5;
}

.efm-text--sub { color: var(--am-text-secondary); }
.efm-text--danger { color: var(--am-danger, #dc2626); }

.efm-field-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--am-text-secondary);
  margin: 0 0 2px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.efm-contact {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--am-space-s);
  padding: var(--am-space-s) 0;
  border-bottom: 1px solid var(--am-border);
}

.efm-contact:last-child { border-bottom: none; }

.efm-contact-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.efm-contact-name {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--am-text-primary);
}

.efm-contact-role {
  font-size: 0.75rem;
  color: var(--am-text-secondary);
}

.efm-call-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: var(--am-success-bg, rgba(34,197,94,0.1));
  color: var(--am-success, #16a34a);
  border: 1px solid var(--am-success, #22c55e);
  border-radius: var(--am-radius-s);
  font-size: 0.85rem;
  font-weight: 600;
  text-decoration: none;
  white-space: nowrap;
}

.efm-no-phone {
  font-size: 0.8rem;
  color: var(--am-text-secondary);
}

.efm-disclaimer {
  font-size: 0.75rem;
  color: var(--am-text-secondary);
  line-height: 1.4;
  margin: 0;
  padding: var(--am-space-s) 0;
  border-top: 1px solid var(--am-border);
}
</style>
