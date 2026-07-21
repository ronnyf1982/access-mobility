<template>
  <div v-if="visible" class="emm-overlay" role="dialog" aria-modal="true" aria-labelledby="emm-title" @click.self="$emit('close')">
    <div class="emm-dialog">
      <header class="emm-header">
        <div class="emm-header-icon" aria-hidden="true"><i class="pi pi-exclamation-triangle"></i></div>
        <div>
          <h2 id="emm-title" class="emm-title">NOTFALL-ASSISTENT</h2>
          <p class="emm-subtitle">{{ data?.passenger_display_name ?? 'Fahrgast' }}</p>
        </div>
        <button class="emm-close" aria-label="Schließen" @click="$emit('close')">
          <i class="pi pi-times" aria-hidden="true"></i>
        </button>
      </header>

      <div v-if="loading" class="emm-loading" role="status">
        <i class="pi pi-spin pi-spinner" aria-hidden="true"></i>
        Lade Notfalldaten …
      </div>

      <div v-else-if="error" class="emm-error" role="alert">
        <i class="pi pi-exclamation-circle" aria-hidden="true"></i>
        {{ error }}
      </div>

      <div v-else-if="data" class="emm-body">

        <!-- 112 ANRUF-BUTTON + SUMMARY ────────────────────────────────────── -->
        <section class="emm-section emm-section--urgent">
          <h3 class="emm-section-title"><i class="pi pi-phone" aria-hidden="true"></i> Notruf 112</h3>
          <a href="tel:112" class="emm-call-112">
            <i class="pi pi-phone" aria-hidden="true"></i>
            112 ANRUFEN
          </a>
          <details class="emm-details">
            <summary class="emm-details-summary">Ansagetext für 112 anzeigen</summary>
            <p class="emm-script">{{ data.emergency_summary_for_112 }}</p>
          </details>
        </section>

        <!-- NOTFALLKONTAKT ANRUFEN ─────────────────────────────────────────── -->
        <section v-if="data.primary_emergency_contact?.phone_number" class="emm-section emm-section--contact">
          <h3 class="emm-section-title"><i class="pi pi-user" aria-hidden="true"></i> Notfallkontakt</h3>
          <div class="emm-contact-row">
            <div>
              <strong class="emm-contact-name">{{ data.primary_emergency_contact.name }}</strong>
              <span v-if="data.primary_emergency_contact.role_label" class="emm-contact-role">
                {{ data.primary_emergency_contact.role_label }}
              </span>
            </div>
            <a :href="`tel:${data.primary_emergency_contact.phone_number}`" class="emm-call-contact">
              <i class="pi pi-phone" aria-hidden="true"></i>
              {{ data.primary_emergency_contact.phone_number }}
            </a>
          </div>
        </section>

        <!-- ERKRANKUNGEN + WICHTIGE HINWEISE ─────────────────────────────── -->
        <section v-if="data.disabilities_visible && (data.has_epilepsy || data.is_mute || data.uses_wheelchair || data.is_blind_or_visually_impaired || data.is_deaf_or_hard_of_hearing || data.known_conditions)" class="emm-section">
          <h3 class="emm-section-title"><i class="pi pi-heart" aria-hidden="true"></i> Erkrankungen</h3>
          <div class="emm-tag-row">
            <span v-if="data.uses_wheelchair" class="emm-tag">Rollstuhl</span>
            <span v-if="data.has_epilepsy" class="emm-tag emm-tag--warn">Epilepsie</span>
            <span v-if="data.is_blind_or_visually_impaired" class="emm-tag">Sehbehinderung</span>
            <span v-if="data.is_deaf_or_hard_of_hearing" class="emm-tag">Hörbehinderung</span>
            <span v-if="data.is_mute" class="emm-tag">Sprechbehinderung</span>
          </div>
          <p v-if="data.known_conditions" class="emm-text">{{ data.known_conditions }}</p>
        </section>

        <!-- MEDIKAMENTE ───────────────────────────────────────────────────── -->
        <section v-if="data.medication_visible && (data.medication_notes || data.allergy_notes)" class="emm-section">
          <h3 class="emm-section-title"><i class="pi pi-plus-circle" aria-hidden="true"></i> Medikamente / Allergien</h3>
          <p v-if="data.medication_notes" class="emm-text">
            <strong>Medikamente:</strong> {{ data.medication_notes }}
          </p>
          <p v-if="data.allergy_notes" class="emm-text emm-text--warn">
            <strong>Allergien / Unverträglichkeiten:</strong> {{ data.allergy_notes }}
          </p>
        </section>

        <!-- KÖRPERDATEN ────────────────────────────────────────────────────── -->
        <section v-if="data.body_data_visible" class="emm-section">
          <h3 class="emm-section-title"><i class="pi pi-user" aria-hidden="true"></i> Körperdaten</h3>
          <div class="emm-body-data">
            <div v-if="data.gender" class="emm-body-item">
              <span class="emm-body-label">Geschlecht</span>
              <span class="emm-body-value">{{ data.gender }}</span>
            </div>
            <div v-if="data.body_height_cm" class="emm-body-item">
              <span class="emm-body-label">Größe</span>
              <span class="emm-body-value">ca. {{ data.body_height_cm }} cm</span>
            </div>
            <div v-if="data.body_weight_kg" class="emm-body-item">
              <span class="emm-body-label">Gewicht</span>
              <span class="emm-body-value">ca. {{ data.body_weight_kg }} kg</span>
            </div>
          </div>
        </section>

        <!-- WAS HILFT / WAS VERMEIDEN ───────────────────────────────────── -->
        <section v-if="data.emergency_notes_visible && (data.what_helps_notes || data.what_to_avoid_notes)" class="emm-section">
          <h3 class="emm-section-title"><i class="pi pi-info-circle" aria-hidden="true"></i> Wichtige Hinweise</h3>
          <div v-if="data.what_helps_notes" class="emm-hint emm-hint--green">
            <strong>Das hilft:</strong> {{ data.what_helps_notes }}
          </div>
          <div v-if="data.what_to_avoid_notes" class="emm-hint emm-hint--red">
            <strong>Das NICHT tun:</strong> {{ data.what_to_avoid_notes }}
          </div>
        </section>

        <!-- ERSTE-HILFE-GLOSSAR ──────────────────────────────────────────── -->
        <section v-if="data.glossary_entries.length > 0" class="emm-section emm-section--glossary">
          <h3 class="emm-section-title"><i class="pi pi-book" aria-hidden="true"></i> Erste-Hilfe-Anleitung</h3>
          <div v-for="entry in data.glossary_entries" :key="entry.key" class="emm-glossary-entry">
            <h4 class="emm-glossary-title">{{ entry.immediate_action_title }}</h4>
            <ol class="emm-list emm-list--steps">
              <li v-for="(step, i) in entry.first_aid_steps" :key="i">{{ step }}</li>
            </ol>
            <div v-if="entry.do_not_do.length > 0" class="emm-donot">
              <strong>NICHT TUN:</strong>
              <ul class="emm-list emm-list--donot">
                <li v-for="(item, i) in entry.do_not_do" :key="i">{{ item }}</li>
              </ul>
            </div>
            <div v-if="entry.call_112_when.length > 0" class="emm-call-when">
              <strong>112 rufen wenn:</strong>
              <ul class="emm-list emm-list--warn">
                <li v-for="(item, i) in entry.call_112_when" :key="i">{{ item }}</li>
              </ul>
            </div>
            <p class="emm-source">{{ entry.source_note }}</p>
          </div>
        </section>

        <!-- STANDORT ────────────────────────────────────────────────────── -->
        <section v-if="data.current_location_label" class="emm-section">
          <h3 class="emm-section-title"><i class="pi pi-map-marker" aria-hidden="true"></i> Standort</h3>
          <p class="emm-text emm-text--location">{{ data.current_location_label }}</p>
          <p v-if="data.pickup_latitude" class="emm-text emm-text--sub">
            GPS: {{ data.pickup_latitude.toFixed(5) }}, {{ data.pickup_longitude?.toFixed(5) }}
          </p>
        </section>

        <!-- HAFTUNGSHINWEIS ─────────────────────────────────────────────── -->
        <p class="emm-disclaimer">{{ data.medical_disclaimer }}</p>
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
      data.value = await getEmergencyFile(id as string, true)
    } catch {
      error.value = 'Notfalldaten konnten nicht geladen werden.'
    } finally {
      loading.value = false
    }
  },
  { immediate: true },
)
</script>

<style scoped>
.emm-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.80);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1100;
  padding: var(--am-space-m);
}

.emm-dialog {
  background: var(--am-bg-card);
  border-radius: var(--am-radius-m);
  border: 2px solid var(--am-danger, #dc2626);
  width: 100%;
  max-width: 580px;
  max-height: 92vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.emm-header {
  display: flex;
  align-items: center;
  gap: var(--am-space-m);
  padding: var(--am-space-l);
  background: var(--am-danger-bg, rgba(220,38,38,0.1));
  border-bottom: 1px solid var(--am-danger, #dc2626);
  position: sticky;
  top: 0;
  z-index: 1;
}

.emm-header-icon {
  width: 44px;
  height: 44px;
  background: rgba(220,38,38,0.15);
  color: var(--am-danger, #dc2626);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.3rem;
  flex-shrink: 0;
}

.emm-title {
  font-size: 1.1rem;
  font-weight: 800;
  margin: 0;
  color: var(--am-danger, #dc2626);
  letter-spacing: 0.04em;
}

.emm-subtitle {
  font-size: 0.8rem;
  color: var(--am-text-secondary);
  margin: 2px 0 0;
}

.emm-close {
  margin-left: auto;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--am-text-secondary);
  padding: 6px;
  border-radius: var(--am-radius-s);
  font-size: 1rem;
}

.emm-body {
  padding: var(--am-space-l);
  display: flex;
  flex-direction: column;
  gap: var(--am-space-m);
}

.emm-loading, .emm-error {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  padding: var(--am-space-xl);
  justify-content: center;
  font-size: 0.9rem;
  color: var(--am-text-secondary);
}

.emm-error { color: var(--am-danger, #dc2626); }

.emm-section {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-s);
  padding: var(--am-space-m);
  background: var(--am-bg-raised);
  border-radius: var(--am-radius-s);
  border: 1px solid var(--am-border);
}

.emm-section--urgent {
  border-color: var(--am-danger, #dc2626);
  background: rgba(220,38,38,0.06);
}

.emm-section--contact {
  border-color: var(--am-success, #22c55e);
  background: rgba(34,197,94,0.06);
}

.emm-section--glossary {
  border-color: var(--am-accent);
}

.emm-section-title {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--am-text-primary);
  margin: 0;
}

.emm-section-title .pi { color: var(--am-accent); }
.emm-section--urgent .emm-section-title .pi { color: var(--am-danger, #dc2626); }
.emm-section--contact .emm-section-title .pi { color: var(--am-success, #22c55e); }

.emm-call-112 {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--am-space-m);
  padding: var(--am-space-l);
  background: var(--am-danger, #dc2626);
  color: #fff;
  border-radius: var(--am-radius-s);
  font-size: 1.4rem;
  font-weight: 800;
  text-decoration: none;
  letter-spacing: 0.06em;
}

.emm-call-112 .pi { font-size: 1.3rem; }

.emm-details { margin-top: var(--am-space-s); }

.emm-details-summary {
  font-size: 0.8rem;
  color: var(--am-text-secondary);
  cursor: pointer;
}

.emm-script {
  font-size: 0.85rem;
  color: var(--am-text-primary);
  background: var(--am-bg-card);
  border: 1px solid var(--am-border);
  border-radius: var(--am-radius-s);
  padding: var(--am-space-m);
  margin: var(--am-space-s) 0 0;
  line-height: 1.6;
}

.emm-contact-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--am-space-m);
}

.emm-contact-name {
  display: block;
  font-size: 0.95rem;
  color: var(--am-text-primary);
}

.emm-contact-role {
  display: block;
  font-size: 0.75rem;
  color: var(--am-text-secondary);
}

.emm-call-contact {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--am-success, #22c55e);
  color: #fff;
  border-radius: var(--am-radius-s);
  font-size: 0.9rem;
  font-weight: 700;
  text-decoration: none;
  white-space: nowrap;
}

.emm-tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.emm-tag {
  font-size: 0.78rem;
  font-weight: 600;
  padding: 2px 10px;
  border-radius: 99px;
  background: var(--am-bg-card);
  border: 1px solid var(--am-border);
  color: var(--am-text-primary);
}

.emm-tag--warn {
  background: rgba(245,158,11,0.12);
  border-color: var(--am-warning, #f59e0b);
  color: var(--am-warning, #d97706);
}

.emm-text {
  font-size: 0.875rem;
  color: var(--am-text-primary);
  margin: 0;
  line-height: 1.5;
}

.emm-text--sub { color: var(--am-text-secondary); font-size: 0.8rem; }
.emm-text--warn { color: var(--am-warning, #d97706); }
.emm-text--location { font-weight: 600; }

.emm-hint {
  font-size: 0.875rem;
  padding: var(--am-space-s) var(--am-space-m);
  border-radius: var(--am-radius-s);
  line-height: 1.5;
}

.emm-hint--green { background: rgba(34,197,94,0.1); color: var(--am-success, #16a34a); border: 1px solid rgba(34,197,94,0.3); }
.emm-hint--red   { background: rgba(220,38,38,0.08); color: var(--am-danger, #dc2626); border: 1px solid rgba(220,38,38,0.2); }

.emm-body-data {
  display: flex;
  gap: var(--am-space-l);
  flex-wrap: wrap;
}

.emm-body-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.emm-body-label {
  font-size: 0.72rem;
  color: var(--am-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.emm-body-value {
  font-size: 1rem;
  font-weight: 700;
  color: var(--am-text-primary);
}

.emm-glossary-entry {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-s);
  padding: var(--am-space-m) 0;
  border-top: 1px solid var(--am-border);
}

.emm-glossary-entry:first-child { border-top: none; padding-top: 0; }

.emm-glossary-title {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--am-text-primary);
  margin: 0;
}

.emm-list {
  margin: 0;
  padding-left: var(--am-space-l);
  font-size: 0.85rem;
  line-height: 1.6;
}

.emm-list--steps { color: var(--am-text-primary); }
.emm-list--donot { color: var(--am-danger, #dc2626); }
.emm-list--warn  { color: var(--am-warning, #d97706); }

.emm-donot, .emm-call-when {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--am-text-secondary);
}

.emm-source {
  font-size: 0.72rem;
  color: var(--am-text-secondary);
  font-style: italic;
  margin: 0;
}

.emm-disclaimer {
  font-size: 0.72rem;
  color: var(--am-text-secondary);
  line-height: 1.4;
  margin: 0;
  padding: var(--am-space-s) 0;
  border-top: 1px solid var(--am-border);
}
</style>
