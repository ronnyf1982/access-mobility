<template>
  <div class="mp-page">
    <!-- Seitenheader -->
    <div class="mp-header">
      <div>
        <h1 class="mp-title">Mein Mobilitätsprofil</h1>
        <p class="mp-subtitle">
          Ihr Mobilitätsprofil hilft uns, später automatisch ein passendes Fahrzeug und die
          richtige Unterstützung auszuwählen.
        </p>
      </div>
    </div>

    <div
      v-if="store.loading"
      class="mp-loading"
      role="status"
      aria-live="polite"
      aria-label="Profil wird geladen"
    >
      <i class="pi pi-spin pi-spinner" aria-hidden="true"></i>
      Profil wird geladen …
    </div>

    <form v-else class="mp-form" @submit.prevent="handleSave" novalidate>
      <!-- Hinweisbox -->
      <div class="mp-notice" role="note">
        <i class="pi pi-info-circle" aria-hidden="true"></i>
        Alle Angaben können jederzeit geändert werden.
        <strong>Medizinische Hinweise sind freiwillig</strong> und werden ausschließlich zur
        Fahrtplanung genutzt.
      </div>

      <!-- Erfolgsmeldung -->
      <div
        v-if="saveSuccess"
        class="mp-alert mp-alert--success"
        role="alert"
        aria-live="assertive"
      >
        <i class="pi pi-check-circle" aria-hidden="true"></i>
        Ihr Mobilitätsprofil wurde gespeichert.
      </div>

      <!-- Fehlermeldung -->
      <div
        v-if="saveError"
        class="mp-alert mp-alert--error"
        role="alert"
        aria-live="assertive"
      >
        <i class="pi pi-exclamation-circle" aria-hidden="true"></i>
        {{ saveError }}
      </div>

      <!-- ── Abschnitt 1: Notfallkontakt ────────────────────────────────── -->
      <section class="mp-section am-card" aria-labelledby="s1-heading">
        <h2 id="s1-heading" class="mp-section-title">
          <i class="pi pi-phone" aria-hidden="true"></i>
          Notfallkontakt
        </h2>
        <p class="mp-section-desc">
          Wer soll im Notfall kontaktiert werden? Die Angabe ist freiwillig.
        </p>
        <div class="mp-field-row">
          <div class="mp-field">
            <label for="ec-name" class="mp-label">Name der Kontaktperson</label>
            <input
              id="ec-name"
              v-model="form.emergency_contact_name"
              type="text"
              class="mp-input"
              autocomplete="off"
              aria-label="Name der Notfallkontaktperson"
              placeholder="Vorname Nachname"
            />
          </div>
          <div class="mp-field">
            <label for="ec-phone" class="mp-label">Telefonnummer</label>
            <input
              id="ec-phone"
              v-model="form.emergency_contact_phone"
              type="tel"
              class="mp-input"
              autocomplete="off"
              aria-label="Telefonnummer der Notfallkontaktperson"
              placeholder="+49 30 …"
            />
          </div>
        </div>
      </section>

      <!-- ── Abschnitt 2: Mobilitätsbedarf ──────────────────────────────── -->
      <section class="mp-section am-card" aria-labelledby="s2-heading">
        <h2 id="s2-heading" class="mp-section-title">
          <i class="pi pi-heart" aria-hidden="true"></i>
          Mein Mobilitätsbedarf
        </h2>
        <p class="mp-section-desc">
          Wählen Sie alles aus, was auf Sie zutrifft. Mehrfachauswahl ist möglich.
        </p>

        <div class="mp-need-grid" role="group" aria-label="Mobilitätsbedarf auswählen">
          <button
            v-for="need in store.mobilityNeedItems"
            :key="String(need.key)"
            type="button"
            class="mp-need-card"
            :class="{ 'mp-need-card--active': form[need.key] as boolean }"
            role="checkbox"
            :aria-checked="!!(form[need.key] as boolean)"
            :aria-label="`${need.label}: ${need.description}`"
            @click="toggleNeed(need.key as NeedKey)"
          >
            <div class="mp-need-icon" aria-hidden="true">
              <i :class="['pi', need.icon]"></i>
            </div>
            <div class="mp-need-text">
              <span class="mp-need-label">{{ need.label }}</span>
              <span class="mp-need-desc">{{ need.description }}</span>
            </div>
            <div class="mp-need-check" aria-hidden="true">
              <i class="pi pi-check"></i>
            </div>
          </button>
        </div>

        <!-- Rollstuhl-Typ (nur wenn Rollstuhl aktiv) -->
        <div v-if="form.uses_wheelchair" class="mp-wheelchair-type" role="group" aria-labelledby="wct-heading">
          <p id="wct-heading" class="mp-label">Welche Art von Rollstuhl nutzen Sie?</p>
          <div class="mp-radio-group">
            <label v-for="opt in wheelchairTypeOptions" :key="opt.value" class="mp-radio-label">
              <input
                type="radio"
                class="mp-radio"
                :value="opt.value"
                v-model="form.wheelchair_type"
                :name="`wheelchair_type`"
              />
              <span>{{ opt.label }}</span>
            </label>
          </div>
        </div>
      </section>

      <!-- ── Abschnitt 3: Fahrzeug- / Service-Hinweise ──────────────────── -->
      <section class="mp-section am-card" aria-labelledby="s3-heading">
        <h2 id="s3-heading" class="mp-section-title">
          <i class="pi pi-car" aria-hidden="true"></i>
          Fahrzeug- und Service-Hinweise
        </h2>
        <p class="mp-section-desc">
          Diese Angaben helfen dem Fahrdienst, das passende Fahrzeug bereit zu stellen.
        </p>

        <div class="mp-toggle-list">
          <!-- Rollstuhlplatz erforderlich -->
          <label class="mp-toggle-row">
            <span class="mp-toggle-label">
              Rollstuhlplatz im Fahrzeug erforderlich
              <span class="mp-toggle-sub">Das Fahrzeug muss einen gesicherten Rollstuhlplatz haben.</span>
            </span>
            <button
              type="button"
              class="mp-toggle-btn"
              :class="{ 'mp-toggle-btn--on': form.requires_wheelchair_space }"
              role="switch"
              :aria-checked="form.requires_wheelchair_space"
              aria-label="Rollstuhlplatz erforderlich"
              @click="form.requires_wheelchair_space = !form.requires_wheelchair_space"
            >
              <span class="mp-toggle-knob"></span>
            </button>
          </label>

          <!-- Zusätzliche Zeit -->
          <label class="mp-toggle-row">
            <span class="mp-toggle-label">
              Zusätzliche Zeit einplanen
              <span class="mp-toggle-sub">Für Ein- und Aussteigen wird mehr Zeit benötigt.</span>
            </span>
            <button
              type="button"
              class="mp-toggle-btn"
              :class="{ 'mp-toggle-btn--on': form.requires_extra_time }"
              role="switch"
              :aria-checked="form.requires_extra_time"
              aria-label="Zusätzliche Zeit einplanen"
              @click="form.requires_extra_time = !form.requires_extra_time"
            >
              <span class="mp-toggle-knob"></span>
            </button>
          </label>

          <!-- Auf Sitz wechseln -->
          <div class="mp-tristate-row">
            <span class="mp-toggle-label">
              Kann auf normalen Fahrzeugsitz wechseln
              <span class="mp-toggle-sub">Wenn ja, kann der Rollstuhl ggf. im Kofferraum transportiert werden.</span>
            </span>
            <div class="mp-tristate-btns" role="group" aria-label="Kann auf normalen Sitz wechseln">
              <button
                v-for="opt in tristateOptions"
                :key="String(opt.value)"
                type="button"
                class="mp-tristate-btn"
                :class="{ 'mp-tristate-btn--active': form.can_transfer_to_seat === opt.value }"
                :aria-pressed="form.can_transfer_to_seat === opt.value"
                @click="form.can_transfer_to_seat = opt.value"
              >
                {{ opt.label }}
              </button>
            </div>
          </div>

          <!-- Eigener Rollstuhl -->
          <div class="mp-tristate-row">
            <span class="mp-toggle-label">
              Eigener Rollstuhl vorhanden
              <span class="mp-toggle-sub">Falls ja, wird er im Fahrzeug mitgenommen.</span>
            </span>
            <div class="mp-tristate-btns" role="group" aria-label="Eigener Rollstuhl vorhanden">
              <button
                v-for="opt in tristateOptions"
                :key="String(opt.value)"
                type="button"
                class="mp-tristate-btn"
                :class="{ 'mp-tristate-btn--active': form.has_own_wheelchair === opt.value }"
                :aria-pressed="form.has_own_wheelchair === opt.value"
                @click="form.has_own_wheelchair = opt.value"
              >
                {{ opt.label }}
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- ── Abschnitt 4: Hinweise ───────────────────────────────────────── -->
      <section class="mp-section am-card" aria-labelledby="s4-heading">
        <h2 id="s4-heading" class="mp-section-title">
          <i class="pi pi-comment" aria-hidden="true"></i>
          Weitere Hinweise
        </h2>

        <div class="mp-field">
          <label for="comm-notes" class="mp-label">Kommunikationshinweise</label>
          <p class="mp-field-hint">
            Z. B. „Bitte laut und deutlich sprechen", „bevorzuge schriftliche Kommunikation"
          </p>
          <textarea
            id="comm-notes"
            v-model="form.communication_notes"
            class="mp-textarea"
            rows="3"
            aria-label="Kommunikationshinweise"
          ></textarea>
        </div>

        <div class="mp-field">
          <label for="med-notes" class="mp-label">
            Medizinische Hinweise
            <span class="mp-optional-badge">freiwillig</span>
          </label>
          <p class="mp-field-hint">
            Relevante Informationen für den Fahrdienst, z. B. Sauerstoffgerät, Medikamente im
            Notfall. Wird vertraulich behandelt.
          </p>
          <textarea
            id="med-notes"
            v-model="form.medical_notes"
            class="mp-textarea"
            rows="3"
            aria-label="Medizinische Hinweise — freiwillig"
          ></textarea>
        </div>

        <div class="mp-field">
          <label for="gen-notes" class="mp-label">Allgemeine Hinweise</label>
          <p class="mp-field-hint">
            Alles Weitere, das für den Fahrdienst wichtig sein könnte.
          </p>
          <textarea
            id="gen-notes"
            v-model="form.general_notes"
            class="mp-textarea"
            rows="3"
            aria-label="Allgemeine Hinweise"
          ></textarea>
        </div>
      </section>

      <!-- ── Abschnitt 5: Speichern ──────────────────────────────────────── -->
      <div class="mp-save-bar">
        <button
          type="submit"
          class="am-btn am-btn-primary mp-save-btn"
          :disabled="store.saving"
          :aria-busy="store.saving"
        >
          <i v-if="store.saving" class="pi pi-spin pi-spinner" aria-hidden="true"></i>
          <i v-else class="pi pi-save" aria-hidden="true"></i>
          {{ store.saving ? 'Wird gespeichert …' : 'Mobilitätsprofil speichern' }}
        </button>
        <span class="mp-save-hint">Ihre Daten werden sicher auf dem Server gespeichert.</span>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, watch, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useMobilityProfileStore } from '@/stores/mobilityProfile'
import type { MobilityProfile, WheelchairType } from '@/types'

type NeedKey =
  | 'uses_wheelchair'
  | 'uses_rollator'
  | 'uses_crutches'
  | 'is_blind_or_visually_impaired'
  | 'is_deaf_or_hard_of_hearing'
  | 'needs_escort'
  | 'needs_entry_assistance'
  | 'needs_door_to_door_assistance'
  | 'needs_ramp'
  | 'needs_lift'
  | 'needs_stretcher_transport'

const store = useMobilityProfileStore()
const toast = useToast()

const saveSuccess = ref(false)
const saveError = ref('')

const wheelchairTypeOptions = [
  { value: 'manual' as WheelchairType, label: 'Manueller Rollstuhl' },
  { value: 'electric' as WheelchairType, label: 'Elektrorollstuhl' },
  { value: 'unknown' as WheelchairType, label: 'Ich weiß es nicht genau' },
]

const tristateOptions: Array<{ value: boolean | null; label: string }> = [
  { value: true, label: 'Ja' },
  { value: false, label: 'Nein' },
  { value: null, label: 'Unbekannt' },
]

// Lokales Formular-State — wird beim Laden aus dem Store befüllt
const form = reactive<Partial<MobilityProfile>>({
  emergency_contact_name: null,
  emergency_contact_phone: null,
  uses_wheelchair: false,
  wheelchair_type: null,
  uses_rollator: false,
  uses_crutches: false,
  is_blind_or_visually_impaired: false,
  is_deaf_or_hard_of_hearing: false,
  needs_escort: false,
  needs_entry_assistance: false,
  needs_door_to_door_assistance: false,
  needs_ramp: false,
  needs_lift: false,
  needs_stretcher_transport: false,
  can_transfer_to_seat: null,
  has_own_wheelchair: null,
  requires_wheelchair_space: false,
  requires_extra_time: false,
  communication_notes: null,
  medical_notes: null,
  general_notes: null,
})

function syncFormFromStore() {
  const p = store.profile
  if (!p) return
  Object.assign(form, {
    emergency_contact_name: p.emergency_contact_name,
    emergency_contact_phone: p.emergency_contact_phone,
    uses_wheelchair: p.uses_wheelchair,
    wheelchair_type: p.wheelchair_type,
    uses_rollator: p.uses_rollator,
    uses_crutches: p.uses_crutches,
    is_blind_or_visually_impaired: p.is_blind_or_visually_impaired,
    is_deaf_or_hard_of_hearing: p.is_deaf_or_hard_of_hearing,
    needs_escort: p.needs_escort,
    needs_entry_assistance: p.needs_entry_assistance,
    needs_door_to_door_assistance: p.needs_door_to_door_assistance,
    needs_ramp: p.needs_ramp,
    needs_lift: p.needs_lift,
    needs_stretcher_transport: p.needs_stretcher_transport,
    can_transfer_to_seat: p.can_transfer_to_seat,
    has_own_wheelchair: p.has_own_wheelchair,
    requires_wheelchair_space: p.requires_wheelchair_space,
    requires_extra_time: p.requires_extra_time,
    communication_notes: p.communication_notes,
    medical_notes: p.medical_notes,
    general_notes: p.general_notes,
  })
}

// Wenn Rollstuhl deaktiviert wird, Rollstuhl-Typ zurücksetzen
watch(
  () => form.uses_wheelchair,
  (val) => {
    if (!val) form.wheelchair_type = null
  },
)

function toggleNeed(key: NeedKey) {
  ;(form[key] as boolean) = !(form[key] as boolean)
}

async function handleSave() {
  saveSuccess.value = false
  saveError.value = ''
  try {
    await store.save({ ...form })
    saveSuccess.value = true
    toast.add({
      severity: 'success',
      summary: 'Gespeichert',
      detail: 'Ihr Mobilitätsprofil wurde erfolgreich gespeichert.',
      life: 4000,
    })
    // Erfolgsmeldung nach 6 Sek. ausblenden
    setTimeout(() => (saveSuccess.value = false), 6000)
  } catch {
    saveError.value =
      'Das Speichern ist fehlgeschlagen. Bitte prüfen Sie Ihre Verbindung und versuchen Sie es erneut.'
  }
}

onMounted(async () => {
  if (!store.profile) {
    await store.load()
  }
  syncFormFromStore()
})

// Store-Profil-Änderungen ins Formular übernehmen (z. B. nach erstem Load)
watch(() => store.profile, syncFormFromStore)
</script>

<style scoped>
.mp-page {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-l);
  max-width: 820px;
}

/* Header */
.mp-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--am-space-m);
}

.mp-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--am-text-primary);
  margin: 0;
}

.mp-subtitle {
  font-size: 0.875rem;
  color: var(--am-text-secondary);
  margin: 4px 0 0;
  line-height: 1.5;
}

/* Loading */
.mp-loading {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  color: var(--am-text-secondary);
  font-size: 0.9rem;
  padding: var(--am-space-xl);
  justify-content: center;
}

/* Notice */
.mp-notice {
  display: flex;
  align-items: flex-start;
  gap: var(--am-space-s);
  padding: var(--am-space-s) var(--am-space-m);
  background: var(--am-accent-bg);
  border: 1px solid rgba(255, 214, 0, 0.3);
  border-radius: var(--am-radius-s);
  font-size: 0.85rem;
  color: var(--am-text-secondary);
  line-height: 1.5;
}

.mp-notice .pi {
  color: var(--am-accent);
  flex-shrink: 0;
  margin-top: 2px;
}

/* Alerts */
.mp-alert {
  display: flex;
  align-items: flex-start;
  gap: var(--am-space-s);
  padding: var(--am-space-s) var(--am-space-m);
  border-radius: var(--am-radius-s);
  font-size: 0.875rem;
  line-height: 1.5;
}

.mp-alert--success {
  background: var(--am-success-bg);
  border: 1px solid var(--am-success);
  color: var(--am-success);
}

.mp-alert--error {
  background: var(--am-danger-bg);
  border: 1px solid var(--am-danger);
  color: var(--am-danger);
}

/* Form */
.mp-form {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-l);
}

/* Section */
.mp-section {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-m);
}

.mp-section-title {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  font-size: 1rem;
  font-weight: 700;
  color: var(--am-text-primary);
  margin: 0;
}

.mp-section-title .pi {
  color: var(--am-accent);
  font-size: 1rem;
}

.mp-section-desc {
  font-size: 0.85rem;
  color: var(--am-text-secondary);
  margin: 0;
  line-height: 1.5;
}

/* Fields */
.mp-field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--am-space-m);
}

@media (max-width: 600px) {
  .mp-field-row {
    grid-template-columns: 1fr;
  }
}

.mp-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.mp-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--am-text-primary);
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
}

.mp-field-hint {
  font-size: 0.78rem;
  color: var(--am-text-secondary);
  margin: 0;
  line-height: 1.4;
}

.mp-optional-badge {
  font-size: 0.68rem;
  font-weight: 600;
  padding: 1px 7px;
  border-radius: 99px;
  background: var(--am-bg-raised);
  color: var(--am-text-secondary);
  border: 1px solid var(--am-border);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.mp-input {
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
  width: 100%;
}

.mp-input:focus {
  border-color: var(--am-accent);
  box-shadow: 0 0 0 3px rgba(255, 214, 0, 0.18);
}

.mp-textarea {
  background: var(--am-bg-raised);
  border: 1px solid var(--am-border-strong);
  border-radius: var(--am-radius-s);
  color: var(--am-text-primary);
  font-size: 0.9rem;
  padding: var(--am-space-s) var(--am-space-m);
  outline: none;
  resize: vertical;
  transition: border-color var(--am-transition);
  width: 100%;
  min-height: 80px;
  box-sizing: border-box;
  font-family: inherit;
}

.mp-textarea:focus {
  border-color: var(--am-accent);
  box-shadow: 0 0 0 3px rgba(255, 214, 0, 0.18);
}

/* Need cards grid */
.mp-need-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: var(--am-space-s);
}

@media (max-width: 520px) {
  .mp-need-grid {
    grid-template-columns: 1fr;
  }
}

.mp-need-card {
  display: flex;
  align-items: flex-start;
  gap: var(--am-space-m);
  padding: var(--am-space-m);
  background: var(--am-bg-raised);
  border: 2px solid var(--am-border);
  border-radius: var(--am-radius-m);
  cursor: pointer;
  text-align: left;
  transition: border-color var(--am-transition), background var(--am-transition);
  min-height: 80px;
  position: relative;
}

.mp-need-card:hover {
  border-color: var(--am-border-strong);
  background: var(--am-bg-surface);
}

.mp-need-card--active {
  border-color: var(--am-accent);
  background: var(--am-accent-bg);
}

.mp-need-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--am-radius-s);
  background: var(--am-bg-base);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: var(--am-text-secondary);
  font-size: 1.1rem;
  transition: color var(--am-transition), background var(--am-transition);
}

.mp-need-card--active .mp-need-icon {
  background: var(--am-accent);
  color: var(--am-text-on-accent);
}

.mp-need-text {
  flex: 1;
  min-width: 0;
}

.mp-need-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--am-text-primary);
  margin-bottom: 2px;
}

.mp-need-desc {
  display: block;
  font-size: 0.75rem;
  color: var(--am-text-secondary);
  line-height: 1.4;
}

.mp-need-check {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid var(--am-border-strong);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: transparent;
  font-size: 0.65rem;
  transition: all var(--am-transition);
}

.mp-need-card--active .mp-need-check {
  background: var(--am-accent);
  border-color: var(--am-accent);
  color: var(--am-text-on-accent);
}

/* Wheelchair type radio */
.mp-wheelchair-type {
  background: var(--am-bg-base);
  border: 1px solid var(--am-border);
  border-radius: var(--am-radius-s);
  padding: var(--am-space-m);
}

.mp-radio-group {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-s);
  margin-top: var(--am-space-s);
}

.mp-radio-label {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  font-size: 0.875rem;
  color: var(--am-text-primary);
  cursor: pointer;
  min-height: 36px;
}

.mp-radio {
  width: 18px;
  height: 18px;
  accent-color: var(--am-accent);
  cursor: pointer;
  flex-shrink: 0;
}

/* Toggle list */
.mp-toggle-list {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-m);
}

.mp-toggle-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--am-space-m);
  padding: var(--am-space-m);
  background: var(--am-bg-raised);
  border: 1px solid var(--am-border);
  border-radius: var(--am-radius-s);
  cursor: pointer;
  min-height: 64px;
}

.mp-toggle-label {
  display: flex;
  flex-direction: column;
  gap: 3px;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--am-text-primary);
  flex: 1;
}

.mp-toggle-sub {
  font-size: 0.78rem;
  font-weight: 400;
  color: var(--am-text-secondary);
}

.mp-toggle-btn {
  position: relative;
  width: 44px;
  height: 24px;
  border-radius: 99px;
  background: var(--am-border-strong);
  border: none;
  cursor: pointer;
  flex-shrink: 0;
  transition: background var(--am-transition);
  padding: 0;
}

.mp-toggle-btn--on {
  background: var(--am-accent);
}

.mp-toggle-knob {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #fff;
  transition: transform var(--am-transition);
  display: block;
}

.mp-toggle-btn--on .mp-toggle-knob {
  transform: translateX(20px);
}

/* Tristate */
.mp-tristate-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--am-space-m);
  padding: var(--am-space-m);
  background: var(--am-bg-raised);
  border: 1px solid var(--am-border);
  border-radius: var(--am-radius-s);
  min-height: 64px;
  flex-wrap: wrap;
}

.mp-tristate-btns {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.mp-tristate-btn {
  padding: 6px 14px;
  border-radius: var(--am-radius-s);
  border: 1px solid var(--am-border-strong);
  background: var(--am-bg-base);
  color: var(--am-text-secondary);
  font-size: 0.82rem;
  cursor: pointer;
  transition: all var(--am-transition);
  min-height: 36px;
  min-width: 60px;
}

.mp-tristate-btn:hover {
  border-color: var(--am-accent);
  color: var(--am-text-primary);
}

.mp-tristate-btn--active {
  background: var(--am-accent);
  border-color: var(--am-accent);
  color: var(--am-text-on-accent);
  font-weight: 700;
}

/* Save bar */
.mp-save-bar {
  display: flex;
  align-items: center;
  gap: var(--am-space-m);
  flex-wrap: wrap;
  padding: var(--am-space-m) 0;
}

.mp-save-btn {
  min-height: 48px;
  font-size: 0.95rem;
  padding: 0 var(--am-space-xl);
}

.mp-save-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.mp-save-hint {
  font-size: 0.78rem;
  color: var(--am-text-secondary);
}
</style>
